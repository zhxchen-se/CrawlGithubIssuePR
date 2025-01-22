import os
import pandas as pd

# IssueList文件夹路径
folder_path = './IssueList'

total_yes_count = 0
total_row_count = 0
# 遍历文件夹中的所有xlsx文件
for filename in os.listdir(folder_path):
    if filename.endswith('.xlsx'):
        file_path = os.path.join(folder_path, filename)
        
        # 读取xlsx文件
        df = pd.read_excel(file_path, engine='openpyxl')        
        # 统计LLM_Answer列中包含"Yes"的行数
        yes_count = df['LLM_Answer'].str.contains('Yes', na=False).sum()
        row_count = len(df) - 1

        total_yes_count += yes_count
        total_row_count += row_count

        # 输出结果
        print(f'{filename} 包含 "Yes" 的行数: {yes_count}, 总Bug数量: {row_count}')

print(f'所有文件中包含 "Yes" 的总行数: {total_yes_count}, 总Bug数量: {total_row_count}')    