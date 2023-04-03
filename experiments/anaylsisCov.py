import os
import subprocess

COV_PATH = "/root/fuzzopt/experiments/totalFiles/cov/profraw/fuzzilli/"
profraws = []
for file in os.listdir(COV_PATH):  # file 表示的是文件名
    if file.endswith('.profraw'):
        profraws.append('COV_PATH' + file)

PROFDATA_PATH = f"/root/fuzzopt/experiments/totalFiles/cov/prodata/fuzzilli.prodata"
COV_ENGHINES_PATH = '/root/engine/ch'

profraws_cmd = ''
for fraws in profraws:
    profraws_cmd += f'{fraws} '
# print(profraws_cmd)
cmd_coverage = f'llvm-profdata merge -o {PROFDATA_PATH} {profraws_cmd} '
# && llvm-cov export {COV_ENGHINES_PATH} -instr-profile={PROFDATA_PATH}
pro = subprocess.Popen(cmd_coverage, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE,
                       universal_newlines=True)
# print(cmd_coverage)
