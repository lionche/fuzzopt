import pandas as pd

# 读取第一个表格文本文件到数据框df1中，指定分隔符为多个空格
df1 = pd.read_table(f'/root/fuzzopt/experiments/totalFiles/cov/prodata/alljit.log', sep='\s+')

# 读取第二个表格文本文件到数据框df2中，指定分隔符为多个空格
df2 = pd.read_table(f'/root/fuzzopt/experiments/totalFiles/cov/prodata/nojit.log', sep='\s+')

# 对两个数据框按照'Filename'列进行合并，并计算'lines'列之间的差异
merged_df = pd.merge(df1, df2, on='Filename', suffixes=['_1', '_2'])
# print(merged_df.columns)
diff_df = merged_df[merged_df['Missed_Lines_1'] != merged_df['Missed_Lines_2']]
pd.set_option('display.max_rows', 1000)
#
# print(diff_df['Filename'])
# for name in ['montage', 'comfort', 'die', 'fuzzilli', 'codealchemist', 'jitfunfuzz']:

df3 = pd.read_table(f'/root/fuzzopt/experiments/totalFiles/cov/prodata/jitfunfuzz.log', sep='\s+')
merged_df1 = pd.merge(diff_df, df3, on='Filename', suffixes=['_1', '_2'])

if merged_df1['Regions_1'] is not None:
    merged_df1 = merged_df1.dropna(subset=['Missed_Lines'])
    merged_df1['Missed_Lines'] = pd.to_numeric(merged_df1['Missed_Lines'], errors='coerce')
    print(merged_df1.loc[merged_df1['Missed_Lines'].notnull(), ['Filename', 'Missed_Lines']])
    # print(merged_df1[['Filename', 'Lines']])
