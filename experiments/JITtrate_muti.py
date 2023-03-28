import os
import subprocess
import sys
from multiprocessing.pool import ThreadPool

from tqdm import tqdm


def Accuractrate(cmd):
    # 使用v8执行用例，其中return值为0的用例是没有语法错误的用例。 判断数量

    global testPassRateSet

    try:
        pro = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True,
                               stderr=subprocess.PIPE, universal_newlines=True)
        stdout, stderr = pro.communicate()
        # pbar.update(1)
        if pro.returncode == 0 :
            print(stdout)
            # if 'completed compiling' in stdout:
            #     jitPassRateSet.add(cmd)
            # if 'bailout' in stdout:
            #     bailoutRate.add(cmd)
            # else:
            #     print(stdout)
        # else:
        #
        #     pass
    except:
        pass


if __name__ == '__main__':
    v8_cmd = 'timeout -s9 60 /root/engine/v8-debug/v8-debug --allow-natives-syntax --trace-opt --trace-deopt '
    # 考虑内存溢出

    # for name in ['montage','comfort', 'die', 'fuzzilli', 'codealchemist']:
    for name in ['codealchemist']:
        jitPassRateSet = set()
        bailoutRate = set()
        cmdlist = []
        count = 0
        # path = f"/root/fuzzopt/experiments/corpus/{name}/"
        path = f"/root/fuzzopt/experiments/codeCoverage/totalFiles/{name}_generate/"
        for file in os.listdir(path):  # file 表示的是文件名
            cmd = v8_cmd + path + file
            if file.endswith('.js'):
                cmdlist.append(cmd)
                count += 1;
        pbar = tqdm(total=count)
        pool = ThreadPool()
        pool.map(Accuractrate, cmdlist)
        pool.close()
        pool.join()
        # print("处理了" + str(count) + "个函数文件！")
        print(name + "生成的用例jit编译率正确率为{:.2%},".format(len(jitPassRateSet) / count))
        print(name + f"中bailout的数量为{len(bailoutRate)}")
        pbar.close()
