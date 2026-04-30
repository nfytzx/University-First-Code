import pandas as pd
import numpy as np
data = np.random.randint(0, 101, (8, 4))
my_rows = ['第1组', '第2组', '第3组', '第4组', '第5组', '第6组', '第7组', '第8组']
my_cols = ['语文', '数学', '英语', '物理']
df = pd.DataFrame(data, index=my_rows, columns=my_cols)
df['班级'] = ['A班', 'A班', 'A班', 'A班', 'B班', 'B班', 'B班', 'B班'] # 假设 第1-4组 属于 "A班"，第5-8组 属于 "B班"
print(df)
d1 = df[:4]  # 获取前4行 (第1组到第4组)
d2 = df[4:]  # 获取第4行之后的数据 (第5组到第8组)
print(d1)
print(d2)
s1 = df.groupby('班级').mean() # 计算 A班和 B班 在 各科上的平均分
s2 = df.groupby('班级').sum() # 计算 A班和 B班 在 各科上的总分
print("按班级分组求平均分：")
print(s1)
print("按班级分组求总分：")
print(s2)
