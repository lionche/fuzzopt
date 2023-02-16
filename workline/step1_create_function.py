import subprocess
import sys
import tempfile
import time

from dbConnecttion.Table_Operation import Table_Function
from model.step3_generationTextPipe import generationTextPipe
from workline.table_to_class.Table_Function_Class import Function_Object


def jshint_check_function(all_functions):
    """
    使用jshint对生成的用例进行检查\n
    过滤掉语法错误的用例\n
    保留正确的，再用于替换代码块变异\n
    去掉用例中最后一行的print
    :param all_functions: 所有方法的list
    :return:
    """
    start_time = time.time()
    # print("正在对生成的用例使用jshint进行语法检查")
    all_testcases_pass = set()
    for testcase in all_functions:
        testcase_jshint = 'var func =' + testcase
        # print(testcase)

        with tempfile.NamedTemporaryFile(delete=True) as tmpfile:
            temp_file_path = tmpfile.name
            tmpfile.write(testcase_jshint.encode())
            tmpfile.seek(0)
            # tmpTxt = tmpfile.read().decode()
            # print(tmpTxt)
            result = cmd_jshint(temp_file_path)
            if result:
                all_testcases_pass.add(testcase)

    end_time = time.time()

    # print(
    #     f"共组装了{len(all_testcases)}个用例，其中语法正确的用例共{len(all_testcases_pass)}个，检测总耗时{int(end_time - start_time)}秒.")
    return all_testcases_pass


def cmd_jshint(temp_file_path):
    """
    使用jshint对生成的function进行检查\n
    :param temp_file_path: 临时文件位置
    :return: 语法正确返回true,语法错误返回false
    """
    # cmd = ['timeout', '60s', 'jshint', temp_file_path]
    cmd = ['timeout', '60s', 'jshint', '-c', '/root/fuzzopt/data/.jshintrc', temp_file_path]
    if sys.platform.startswith('win'):  # 假如是windows
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    else:  # 假如是linux
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    # if stdout:
    #     print("stdout")
    #     print(stdout)
    # if stderr:
    #     print("error")
    #     print(stderr)
    if stdout.__len__() > 0:
        jshint_flag = False
    else:  # 通过了检查，此时 test_file_name中就是美化后的代码
        jshint_flag = True
        # print(f"{temp_file_path}right!")
    return jshint_flag


functions = generationTextPipe()
all_testcases_pass = jshint_check_function(functions)

function_to_write = []

for func in all_testcases_pass:
    SourceFun_id = 0
    Mutation_method = 0
    Mutation_times = 0
    Remark = None
    function_to_write.append((func, SourceFun_id, Mutation_method, Mutation_times, Remark))

Table_Function().insertManyDataToTableFunction(function_to_write)
print(len(function_to_write))
#
# code = """var func = function(d) {
#     return +d;}"""

# 1.gpt生成function，存入数据库

# 2.组装调用加循环
# 3.变异
# 4.执行
