import numpy as np
import pandas as pd

# 1. 数据生成：使用numpy生成一个5行3列的随机整数矩阵，数值范围为60到100
np.random.seed(42)  # 设置随机种子，确保结果可重复
scores_data = np.random.randint(60, 101, size=(5, 3))

# 2. DataFrame构建
students = ['张三', '李四', '王五', '赵六', '孙七']
subjects = ['数学', '英语', '物理']

df = pd.DataFrame(scores_data, index=students, columns=subjects)

print("=" * 50)
print("学生成绩表：")
print("=" * 50)
print(df)
print()

# 3. 计算各科成绩的平均值和总分
# 各科平均值（按列计算）
subject_mean = df.mean()
# 各科总分（按列计算）
subject_sum = df.sum()
# 每个学生的总分（按行计算）
student_sum = df.sum(axis=1)
# 每个学生的平均分（按行计算）
student_mean = df.mean(axis=1)

print("=" * 50)
print("各科成绩统计：")
print("=" * 50)
print("各科平均分：")
print(subject_mean)
print("\n各科总分：")
print(subject_sum)
print()

print("=" * 50)
print("学生个人成绩统计：")
print("=" * 50)
print("学生总分：")
print(student_sum)
print("\n学生平均分：")
print(student_mean)
print()

# 4. 文件保存
# 保存为CSV文件（解决中文乱码问题）
# encoding='utf-8-sig' 可以让Excel正确打开带中文的CSV文件
df.to_csv('class_scores.csv', encoding='utf-8-sig')

# 保存为Excel文件
df.to_excel('class_scores.xlsx', sheet_name='学生成绩')

print("=" * 50)
print("文件保存成功！")
print("=" * 50)
print("已生成文件：")
print("1. class_scores.csv (UTF-8编码，支持中文)")
print("2. class_scores.xlsx")