import os
import pandas as pd

# IssueList文件夹路径
folder_path = './IssueList'

# 遍历文件夹中的所有xlsx文件
for filename in os.listdir(folder_path):
    if filename.endswith('.xlsx'):
        file_path = os.path.join(folder_path, filename)
        
        # 读取xlsx文件
        df = pd.read_excel(file_path, engine='openpyxl')        
        # 统计LLM_Answer列中包含"Yes"的行数
        yes_count = df['LLM_Answer'].str.contains('Yes', na=False).sum()
        
        # 输出结果
        print(f'{filename} 包含 "Yes" 的行数: {yes_count}')