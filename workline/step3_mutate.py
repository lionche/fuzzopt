import subprocess
import tempfile

from dbConnecttion.Table_Operation import Table_Testcase
from workline.table_to_class.Table_Testcase_Class import Testcase_Object

table_Testcase = Table_Testcase()
testcase_object = table_Testcase.selectIdFromTableTestcase(7)
Testcase_Object(testcase_object).mutation_jit()
