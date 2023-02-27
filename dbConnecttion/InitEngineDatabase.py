from MySqlConn import MyPymysqlPool

mysql = MyPymysqlPool()


sql = 'insert into Table_Testbed (Testbed_name, Testbed_version,Testbed_location,Remark) VALUES (%s,%s,%s,%s);'

args = [('v8', '9.9.1','/root/.jsvu/v8',None),
        ('spiderMonkey', 'JavaScript-C96.0', '/root/.jsvu/spidermonkey', None),
        ('chakra', 'ch version 1.11.24.0', '/root/.jsvu/ch', None),
        ('jsc', 'v286936', '/root/.jsvu/javascriptcore', None),
        ('chakra', 'ch version 1.13.0.0-beta', '/root/.jsvu/engines/chakra-1.13-cov/ch', None)]
#
# ('quickjs', 'v2021-03-27', '/root/.jsvu/quickjs', None),
# ('jerryscript', 'Version: 3.0.0 (fea10bb7)', '/root/.jsvu/jerry', None),
# ('graaljs', '21.3.0', '/root/.jsvu/graaljs', None),
# ('hermes', '0.10.0', '/root/.jsvu/hermes', None),
result = mysql.insertMany(sql,args)
# print(result)

# 释放资源
mysql.dispose()
