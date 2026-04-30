import pandas as pd
import numpy as np
data = {
    '姓名': ['张三', '李四', '王五'],
    '年龄': [18, 19, 20],
    '科目': ['数学', '英语', '物理']
}
df = pd.DataFrame(data)
print(df)
print('----------')
data2 = np.random.randint(0, 101, (8, 4))
print(data2)
print("***********************")
# 2. 将这个矩阵转换为 Pandas 的 DataFrame (表格)
df2 = pd.DataFrame(data2)

#3. 打印查看结果
print(df2)
print('----------')

#1.生成一个8行4列的随机数矩阵（数值在0到100之间)
data3 = np.random.randint(0, 101, (8, 4))
#2.准备索引列表
my_rows = ['第1组', '第2组', '第3组', '第4组','第5组', '第6组', '第7组', '第8组']  #准备8个行名（对应8行）
my_cols = ['语文', '数学', '英语', '物理']  #准备4个列名对应4列）
#3.将这个矩阵转换为Pandas的DataFrame （表格），并添加索引
df3 = pd.DataFrame(data3, index=my_rows, columns=my_cols)
#4.打印看结果
print(df3)
print('----------')
df3.to_csv('data3.csv', encoding='utf-8')
df3.to_excel('data3.xlsx')
#读取用a.pd.read_csv()

print('----------')
