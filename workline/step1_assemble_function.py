import os
import sys
from pathlib import Path

BASE_DIR = str(Path(__file__).resolve().parent.parent)
sys.path.append(BASE_DIR)

from dbConnecttion.Table_Operation import Table_Function
from workline.table_to_class.Table_Function_Class import Function_Object

Function_content = Table_Function().selectOneFromTableFunction(1)
FUNCTION = Function_Object(Function_content)
for function in FUNCTION.assemble_to_testcase(3):
    print(function)
