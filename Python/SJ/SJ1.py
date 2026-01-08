import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, roc_auc_score
import warnings

warnings.filterwarnings('ignore')

# 读取xlsx文件
xlsx_file = '附件.xlsx'
df = pd.read_excel(xlsx_file)
# 转换并保存为csv文件
csv_file = '附件.csv'
df.to_csv(csv_file, index=False)
# 读取数据
df = pd.read_csv('附件.csv')

# 查看数据基本信息
print("数据形状:", df.shape)
print("\n列名:", df.columns.tolist())
print("\n前5行数据:")
print(df.head())

# 分离男女胎数据
male_df = df[df['Y染色体浓度'].notna()].copy()  # 男胎数据
female_df = df[df['Y染色体浓度'].isna()].copy()  # 女胎数据

print(f"男胎样本数: {len(male_df)}")
print(f"女胎样本数: {len(female_df)}")


def clean_data(df):
    # 转换孕周为数值 - 处理多种格式
    def convert_pregnancy_week(x):
        try:
            # 处理NaN或空值
            if pd.isna(x):
                return np.nan

            x_str = str(x).strip().lower()  # 转换为字符串并清理

            # 情况1: '11w' 格式
            if x_str.endswith('w'):
                return float(x_str.replace('w', ''))

            # 情况2: '11+3' 格式
            elif '+' in x_str:
                parts = x_str.split('+')
                return float(parts[0]) + float(parts[1]) / 7

            # 情况3: 纯数字字符串
            else:
                return float(x_str)

        except Exception as e:
            print(f"转换孕周时出错: {x}, 错误: {e}")
            return np.nan

    df['孕周数值'] = df['检测孕周'].apply(convert_pregnancy_week)

    # 处理异常值
    df = df[(df['Y染色体浓度'] >= 0) & (df['Y染色体浓度'] <= 1)]
    df = df[(df['BMI指标'] >= 15) & (df['BMI指标'] <= 50)]
    df = df[(df['孕周数值'] >= 10) & (df['孕周数值'] <= 25)]

    return df

# 数据清洗
def clean_data(df):
    # 转换孕周为数值
    df['孕周数值'] = df['检测孕周'].apply(lambda x:
                                                    float(str(x).split('+')[0]) + float(str(x).split('+')[1]) / 7
                                                      if '+' in str(x) else float(x))

    # 处理异常值
    df = df[(df['Y染色体浓度'] >= 0) & (df['Y染色体浓度'] <= 1)]
    df = df[(df['BMI指标'] >= 15) & (df['BMI指标'] <= 50)]
    df = df[(df['孕周数值'] >= 10) & (df['孕周数值'] <= 25)]

    return df


male_df = clean_data(male_df)