import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 读取数据
df = pd.read_excel('附件.xlsx')

# 1. 处理缺失值
print("缺失值统计：")
print(df.isnull().sum())

# 2. 处理重复检测（同一孕妇多次检测）
# 按孕妇代码分组，保留最早或最合适的检测
df['检测日期'] = pd.to_datetime(df['检测日期'])
df_sorted = df.sort_values(['孕妇代码', '检测日期'])

# 3. 过滤无效数据
# 女胎Y染色体浓度应为空/0，男胎应有值
df_male = df[df['Y染色体浓度'].notna() & (df['Y染色体浓度'] > 0)]
df_female = df[df['Y染色体浓度'].isna() | (df['Y染色体浓度'] == 0)]

# 4. 孕周转换（如"12+3"转为12.43周）
def convert_gestational_week(week_str):
    if pd.isna(week_str):
        return np.nan
    if '+' in str(week_str):
        weeks, days = str(week_str).split('+')
        return float(weeks) + float(days)/7
    else:
        return float(week_str)

df['孕周数值'] = df['孕妇本次检测时的孕周'].apply(convert_gestational_week)

# 检查Y染色体浓度分布
plt.figure(figsize=(12, 4))
plt.subplot(131)
sns.histplot(df_male['Y染色体浓度'], kde=True)
plt.title('男胎Y染色体浓度分布')

plt.subplot(132)
sns.scatterplot(data=df_male, x='孕周数值', y='Y染色体浓度', hue='K_孕妇BMI指标')
plt.title('孕周vsY浓度')

plt.subplot(133)
sns.boxplot(data=df_male, x=pd.cut(df_male['K_孕妇BMI指标'], bins=[20,28,32,36,40,50]), y='Y染色体浓度')
plt.title('BMI分组vsY浓度')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

