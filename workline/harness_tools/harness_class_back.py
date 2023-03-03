import collections
import json
import math
import os
import tempfile
import logging
import pathlib
import subprocess
import gc
from threading import Thread
from typing import List

from dbConnecttion.Table_Operation import Table_Testbed
from utils import labdate

# from workline.mysql_tools.Table_Operation import Table_Result, Table_Suspicious_Result

Majority = collections.namedtuple('Majority', [
    'majority_outcome', 'outcome_majority_size',
    'majority_stdout', 'stdout_majority_size'
])


class DifferentialTestResult:
    def __init__(self, function_id: int, testcase_id: int, error_type: str, testbed_id: int, testbed_location: str,
                 testbed_name: str):
        self.function_id = function_id
        self.testcase_id = testcase_id
        self.error_type = error_type
        self.testbed_id = testbed_id
        self.testbed_name = testbed_name
        self.testbed_location = testbed_location
        self.classify_result = None
        self.classify_id = None
        self.remark = None
        self.Is_filtered = 0

    def serialize(self):
        return {"Differential Test Result": {"testcase_id": self.testcase_id,
                                             "error_type": self.error_type,
                                             "testbed_id": self.testbed_id,
                                             "testbed_name": self.testbed_name
                                             }}

    def __str__(self):
        return json.dumps(self.serialize(), indent=4)

    # def save_to_table_suspicious_Result(self):
    #     """
    #     Save the result to the database
    #     :return:
    #     """
    #     table_suspicious_Result = Table_Suspicious_Result()
    #     table_suspicious_Result.insertDataToTableSuspiciousResult(self.error_type, self.testcase_id, self.function_id,
    #                                                               self.testbed_id,
    #                                                               self.remark, self.Is_filtered)
    #


class HarnessResult:
    """
    This is the result type of the differential test, as opposed to ResultClass,
    which is the type that holds the results of the execution at runtime.
    """

    def __init__(self, function_id: int, testcase_id: int, testcase_context: str):
        self.function_id = function_id
        self.testcase_id = testcase_id
        self.testcase_context: str = testcase_context
        self.outputs: List[Output] = []
        self.seed_coverage = 0
        self.engine_coverage: str = ''

    def __str__(self):
        return json.dumps({"Harness_Result": {"testcase_id": self.testcase_id,
                                              "testcase_context": self.testcase_context,
                                              "engine_coverage": self.engine_coverage,
                                              "outputs": [e.serialize() for e in self.outputs]
                                              }
                           }, indent=4)

    def get_majority_output(self) -> Majority:
        """Majority vote on testcase outcomes and outputs."""
        # print(result)

        majority_outcome, outcome_majority_size = collections.Counter([
            output.output_class for output in self.outputs
        ]).most_common(1)[0]
        majority_stdout, stdout_majority_size = collections.Counter([
            output.stdout for output in self.outputs
        ]).most_common(1)[0]
        return Majority(majority_outcome, outcome_majority_size,
                        majority_stdout, stdout_majority_size)

    def differential_test(self) -> List[DifferentialTestResult]:
        if self.outputs is None:
            return []
        ratio = 2 / 3
        majority = self.get_majority_output()
        # print("majority_outputs: ",majority)

        testbed_num = len(self.outputs)

        bugs_info = []
        for output in self.outputs:
            if output.output_class == "crash":
                # print(f"{output.testbed_id}crash")
                bugs_info.append(
                    DifferentialTestResult(self.function_id, self.testcase_id, "crash", output.testbed_id,
                                           output.testbed_location, output.testbed_name))
                # pass
            elif majority.majority_outcome != output.output_class and majority.outcome_majority_size >= math.ceil(
                    ratio * testbed_num):
                if majority.majority_outcome == "pass":
                    bugs_info.append(
                        DifferentialTestResult(self.function_id, self.testcase_id, "Most JS engines pass",
                                               output.testbed_id,
                                               output.testbed_location, output.testbed_name))
                elif majority.majority_outcome == "timeout":
                    # Usually, this is not a bug
                    pass
                elif majority.majority_outcome == "crash":
                    bugs_info.append(
                        DifferentialTestResult(self.function_id, self.testcase_id, "Most JS engines crash",
                                               output.testbed_id,
                                               output.testbed_location, output.testbed_name))
                elif majority.majority_outcome == "script_error":
                    bugs_info.append(
                        DifferentialTestResult(self.function_id, self.testcase_id,
                                               "Majority JS engines throw runtime error/exception",
                                               output.testbed_id,
                                               output.testbed_location, output.testbed_name))
            elif output.output_class == "pass" and majority.majority_outcome == output.output_class and \
                    output.stdout != majority.majority_stdout and \
                    majority.stdout_majority_size >= math.ceil(ratio * majority.outcome_majority_size):
                if majority.outcome_majority_size >= math.ceil(ratio * testbed_num):
                    bugs_info.append(
                        DifferentialTestResult(self.function_id, self.testcase_id, "Pass value *** run error",
                                               output.testbed_id,
                                               output.testbed_location, output.testbed_name))
        return bugs_info

    # def save_to_table_result(self):
    #     """
    #     Save the result to the database.
    #     :return:
    #     """
    #
    #     # print(f'存入数据库内容：{type(self.engine_coverage)}')
    #     # print(f'存入数据库内容：{self.engine_coverage}')
    #     table_result = Table_Result()
    #     for output in self.outputs:
    #         table_result.insertDataToTableResult(self.testcase_id, output.testbed_id, output.returncode, output.stdout,
    #                                              output.stderr, output.duration_ms, 0, None)


class Output:
    def __init__(self,
                 testbed_id: int,
                 testbed_location: str,
                 returncode: int,
                 stdout: str,
                 stderr: str,
                 duration_ms: int,
                 event_start_epoch_ms: int,
                 testbed_name: str
                 ):
        self.testbed_id = testbed_id
        self.testbed_location = testbed_location
        self.testbed_name = testbed_name
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.duration_ms = duration_ms
        self.event_start_epoch_ms = event_start_epoch_ms
        self.output_class = self.get_output_class()

    def get_output_class(self) -> str:
        """
        The order in which branches are judged cannot be reversed，
        because Whether the test case has a syntax error or not, chakraCore's returnCode is equal to 0
        """
        # if self.returncode == -9 and self.duration_ms > 30 * 1000:
        if self.returncode == -9:
            return "timeout"
        elif self.returncode < 0 and self.returncode != -9:
            return "crash"
        elif self.returncode > 0 or not self.stderr == "":
            return "script_error"
        else:
            return "pass"

    def serialize(self):
        return {"testbed_id": self.testbed_id,
                "testbed_location": self.testbed_location,
                "returncode": self.returncode,
                "stdout": self.stdout,
                "stderr": self.stderr,
                "duration_ms": self.duration_ms,
                "event_start_epoch_ms": self.event_start_epoch_ms,
                "testbed_name": self.testbed_name
                }

    def __str__(self):
        return json.dumps({"testbed_id": self.testbed_id,
                           "testbed_location": self.testbed_location,
                           "testbed_name": self.testbed_name,
                           "returncode": self.returncode,
                           "stdout": self.stdout,
                           "stderr": self.stderr,
                           "duration_ms": self.duration_ms,
                           "event_start_epoch_ms": self.event_start_epoch_ms},
                          indent=4)


class ThreadLock(Thread):
    def __init__(self, testcase_id, testbed_location, testcase_path, testbed_id, timeout, testbed_name):
        super().__init__()
        self.testcase_id = testcase_id
        self.testbed_id = testbed_id
        self.testbed_name = testbed_name
        self.output = None
        self.testbed_location = testbed_location
        self.testcase_path = testcase_path
        self.returnInfo = None
        self.timeout = timeout
        self.coverage: str = ''



    def run(self):
        try:
            self.output = self.run_test_case(self.testcase_id, self.testbed_location, self.testcase_path,
                                             self.testbed_id,
                                             self.timeout, self.testbed_name)
            # print(type(self.coverage))

        except BaseException as e:
            self.returnInfo = 1

    def run_test_case(self, testcase_id: int, testbed_location: str, testcase_path: pathlib.Path, testbed_id,
                      timeout, testbed_name):
        uniTag = testcase_path.name.split('javascriptTestcase_')[1].split('.')[0]
        cmd = ["timeout", "-s9", timeout]
        # LLVM_PROFILE_FILE = f"{uniTag}.profraw"ls
        # 保存覆盖率文件的文件夹
        LLVM_PROFILE_FILE = f"/root/Comfort_all/data/cov_files/profraws/{testcase_id}.profraw"
        my_env = os.environ.copy()
        my_env['LLVM_PROFILE_FILE'] = LLVM_PROFILE_FILE

        for ob in testbed_location.split():
            cmd.append(ob)
        cmd.append(str(testcase_path))

        start_time = labdate.GetUtcMillisecondsNow()

        pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False, env=my_env,
                               stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = pro.communicate()

        end_time = labdate.GetUtcMillisecondsNow()
        duration_ms = int(round(
            (end_time - start_time).total_seconds() * 1000))
        event_start_epoch_ms = labdate.MillisecondsTimestamp(start_time)

        output = Output(testbed_id=testbed_id, testbed_location=testbed_location, returncode=pro.returncode,
                        stdout=stdout,
                        stderr=stderr,
                        duration_ms=duration_ms, event_start_epoch_ms=event_start_epoch_ms, testbed_name=testbed_name)
        # coverage_stdout_finally: str = ''
        # if 'cov' in testbed_location:
        # cmd_coverage = f'llvm-profdata-10 merge -o {uniTag}.profdata {uniTag}.profraw && llvm-cov-10 export /root/.jsvu/engines/chakra-1.13-cov/ch -instr-profile={uniTag}.profdata && rm /root/Comfort_all/workline/{uniTag}.profdata /root/Comfort_all/workline/{uniTag}.profraw'
        # pro1 = subprocess.Popen(cmd_coverage, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
        #                         stderr=subprocess.PIPE, universal_newlines=True)
        # stdout1, stderr1 = pro1.communicate()
        # print(stderr1)
        # coverage_stdout_finally = self.del_useless_json_info(stdout1)

        # return output, coverage_stdout_finally
        return output


class Harness:

    @staticmethod
    def get_engines():
        table_testbed = Table_Testbed()
        testbed_list = table_testbed.getAllFromTableTestbed()
        return testbed_list

    def __init__(self):
        """
        initialize harness
        :param engines: engines to be test
        """
        self.engines = self.get_engines()

    def run_testcase(self, function_id: int, testcase_id: int, testcase_context: str,
                     timeout: str) -> HarnessResult:
        """
        Execute test cases with multiple engines and return test results after execution of all engines.
        :param timeout: timeout kill process
        :param function_id: executed function Id
        :param testcase_id:  executed Testcases Id
        :param testcase_context: Testcases to be executed
        :return: test results
        """

        result = self.multi_thread(function_id, testcase_id, testcase_context, timeout)
        return result

    def multi_thread(self, function_id: int, testcase_id: int, testcase_context: str,
                     timeout: str):
        """
        Multithreading test execution test cases
        :param timeout: time to kill process
        :param testcase_path: path of the test case
        :return: execution results of all engines
        """

        result = HarnessResult(function_id=function_id, testcase_id=testcase_id, testcase_context=testcase_context)

        with tempfile.NamedTemporaryFile(prefix="javascriptTestcase_", suffix=".js", delete=True) as f:
            testcase_path = pathlib.Path(f.name)
            try:
                # 此处手动转换为bytes类型再存储是为了防止代码中有乱码而无法存储的情况
                testcase_path.write_bytes(bytes(testcase_context, encoding="utf-8"))

                outputs = []
                threads_pool = []
                coverage = ''
                uniTag = testcase_path.name.split('_')[1].split('.')[0]
                # print(uniTag)
                for engine in self.engines:
                    testbed_id = engine.get('id')
                    testbed_location = str(engine.get('Testbed_location'), 'utf-8')
                    engine_testcase =

                    testbed_name = str(engine.get('Testbed_name'), 'utf-8')
                    tmp = ThreadLock(testcase_id=testcase_id, testbed_location=testbed_location,
                                     testcase_path=testcase_path,
                                     testbed_id=testbed_id,
                                     timeout=timeout,
                                     testbed_name=testbed_name)
                    threads_pool.append(tmp)
                    tmp.start()
                for thread in threads_pool:
                    thread.join()
                    if thread.returnInfo:
                        gc.collect()
                    elif thread.output is not None:
                        outputs.append(thread.output)
                    # print(type(thread.coverage))
                    # print(thread.coverage)

                    # if thread.coverage:
                    # print(type(thread.coverage))
                    # coverage.append((thread.coverage))
                    # coverage = thread.coverage
                    # print(type(coverage))
                # print(type(coverage[0]))

                # print(coverage)

                # return outputs, coverage

                result.outputs = outputs
            except Exception as e:
                logging.exception("\nWrite to file failure: ", e)
                # return result
        return result