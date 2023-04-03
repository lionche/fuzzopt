# my_env['LLVM_PROFILE_FILE'] = LLVM_PROFILE_FILE

import os
import subprocess
import sys
from multiprocessing.pool import ThreadPool

from tqdm import tqdm


def Accuractrate(i,cmd,name):
    # 使用v8执行用例，其中return值为0的用例是没有语法错误的用例。 判断数量

    global testPassRateSet
    LLVM_PROFILE_FILE = f"/root/fuzzopt/experiments/totalFiles/cov/profraw/{name}/{i}.profraw"
    my_env = os.environ.copy()
    my_env['LLVM_PROFILE_FILE'] = LLVM_PROFILE_FILE

    try:
        pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True, env=my_env,
                               stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = pro.communicate()
        pbar.update(1)
        # if pro.returncode == 0:
        #     pass
        #     # print(cmd + "<|end|>\n")
        #     # print(stdout)
        # else:
        #     print(i)
        #
        #     pass
    except:
        pass


if __name__ == '__main__':
    v8_cmd = 'timeout -s9 30 /root/engine/ch --maxinterpretcount:20 --maxsimplejitruncount:100 --bgjit --oopjit '
    # 考虑内存溢出

    # for name in ['montage','comfort', 'die', 'fuzzilli', 'codealchemist','jitfunfuzz']:
    for name in ['jitfunfuzz']:
        cmdlist = []
        count = 0
        # path = f"/root/fuzzopt/experiments/corpus/{name}/"
        path = f"/root/fuzzopt/experiments/totalFiles/{name}_generate/"
        for file in os.listdir(path):  # file 表示的是文件名
            cmd = v8_cmd + path + file
            if file.endswith('.js'):
                cmdlist.append(cmd)
                count += 1;
        pbar = tqdm(total=count)

        for index, cmd in enumerate(cmdlist):
            Accuractrate(index,cmd,name)
        # print("处理了" + str(count) + "个函数文件！")
        pbar.close()
