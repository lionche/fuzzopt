import os

from MySqlConn import MyPymysqlPool

mysql = MyPymysqlPool()


sql = 'insert into Table_Function (Function_content, SourceFun_id,Mutation_method,Mutation_times,Remark) VALUES (%s,%s,%s,%s,%s);'


args = []

dir = r"/root/fuzzopt/data/JStestcases"
current = 0

def readFileAll(path):
    with open(path, 'r', encoding='utf-8') as f:
        code = f.read()
    return code

for root, dirs, files in os.walk(dir):

    files.sort(key=lambda x: int(x[:-3]))
    # -3是后缀名，需要去掉后，按数字大小排序
    # folderList是列表

    for file in files:
        file_path = os.path.join(root, file)
        Function_content = readFileAll(file_path)
        SourceFun_id = 0
        Mutation_method = 0
        Mutation_times = 0
        Remark = None
        args.append((Function_content, SourceFun_id, Mutation_method,Mutation_times, Remark))

result = mysql.insertMany(sql,args)

# 释放资源
mysql.dispose()
