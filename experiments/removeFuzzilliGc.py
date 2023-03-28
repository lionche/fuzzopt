
import os
import subprocess
import sys
from multiprocessing.pool import ThreadPool

from tqdm import tqdm


def removegc(path):
    # 使用v8执行用例，其中return值为0的用例是没有语法错误的用例。 判断数量
    with open(path, 'r') as f:
        lines = f.readlines()

    # 删除最后两行
    lines = lines[:-2]

    with open(path, 'w') as f:
        f.writelines(lines)



if __name__ == '__main__':
    # 考虑内存溢出

    cmdlist = []
    count = 0
    path = f"/root/fuzzopt/experiments/corpus/fuzzilli/"
    for file in os.listdir(path):  # file 表示的是文件名
        cmd = path + file
        if file.endswith('.js'):
            cmdlist.append(cmd)
            count += 1;
            print(cmd)
    pbar = tqdm(total=count)
    for i in cmdlist:
        # print(i)
        removegc(i)
        pbar.update()

    # print("处理了" + str(count) + "个函数文件！")
    # pbar.close()


