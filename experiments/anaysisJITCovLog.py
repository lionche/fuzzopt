import pandas as pd


def method_name(name):
    # 读取文本文件，指定分隔符为制表符（'\t'）
    df = pd.read_table(f'/root/fuzzopt/experiments/totalFiles/cov/prodata/{name}.log', sep='\s+')
    filtered_df = df[df['Filename'].str.startswith('lib/Backend')]
    # print(df.columns)
    # print(filtered_df)
    # 统计符合条件的行数
    # count = len(filtered_df)
    total_lines_sum = (filtered_df['Lines'].sum())
    total_Regions_sum = (filtered_df['Regions'].sum())
    total_Functions_sum = (filtered_df['Functions'].sum())
    total_Branches_sum = (filtered_df['Branches'].sum())
    miss_lines_sum = (filtered_df['Missed_Lines'].sum())
    miss_Regions_sum = (filtered_df['Missed_Regions'].sum())
    miss_Functions_sum = (filtered_df['Missed_Functions'].sum())
    miss_Branches_sum = (filtered_df['Missed_Branches'].sum())
    # print(total_Functions_sum)
    print(name,'line:', 1 - miss_lines_sum / total_lines_sum)
    # print(name, 1 - miss_Regions_sum / total_Regions_sum)
    # print(name, 1 - miss_Functions_sum / total_Functions_sum)
    print(name,'branch:', 1 - miss_Branches_sum / total_Branches_sum)
    # 打印统计结果
    # print(f"共有{count}行的Filename以'lib/Backend'开头")


if __name__ == '__main__':
    for name in ['montage', 'comfort', 'die', 'fuzzilli', 'codealchemist', 'jitfunfuzz']:
        method_name(name)
