import os
import subprocess

COV_PATH = "./"
profraws = []
for file in os.listdir(COV_PATH):  # file 表示的是文件名
    if file.endswith('.profraw'):
        profraws.append(file)

PROFDATA_PATH = f"/root/fuzzopt/experiments/totalFiles/cov/prodata/jitfunfuzz.prodata"
COV_ENGHINES_PATH = '/root/engine/ch'

profraws_cmd = ''
for fraws in profraws:
    profraws_cmd += f'{fraws} '
# print(profraws_cmd)
cmd_coverage = f'llvm-profdata merge -o {PROFDATA_PATH} {profraws_cmd}'
# print(cmd_coverage)
pro = subprocess.Popen(cmd_coverage, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, stderr=subprocess.PIPE,
                       universal_newlines=True)
# print(cmd_coverage)
