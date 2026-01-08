import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, classification_report, roc_auc_score
import statsmodels.api as sm
from scipy.optimize import minimize
from scipy.stats import pearsonr, f_oneway
import os

warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


# 第一部分：数据加载与预处理

def load_and_preprocess_data(file_path='附件.xlsx'):
    """加载并预处理数据"""
    print("=" * 60)
    print("数据加载与预处理")
    print("=" * 60)

    # 1. 读取数据
    try:
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"找到 {len(sheet_names)} 个工作表: {sheet_names}")

        # 合并所有工作表
        all_data = []
        for sheet_name in sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df['来源工作表'] = sheet_name
            all_data.append(df)

        df = pd.concat(all_data, ignore_index=True)
        print(f"合并后总数据量: {df.shape[0]}行 × {df.shape[1]}列")

    except Exception as e:
        print(f"读取文件出错: {e}")
        return None

    # 2. 数据清洗和重命名
    # 根据附录重命名列
    column_mapping = {}
    for idx, col in enumerate(df.columns):
        if idx == 0:
            column_mapping[col] = '序号'
        elif idx == 1:
            column_mapping[col] = '孕妇代码'
        elif idx == 2:
            column_mapping[col] = '年龄'
        elif idx == 3:
            column_mapping[col] = '身高'
        elif idx == 4:
            column_mapping[col] = '体重'
        elif idx == 5:
            column_mapping[col] = '未次月经时间'
        elif idx == 6:
            column_mapping[col] = 'IVF妊娠方式'
        elif idx == 7:
            column_mapping[col] = '检测时间'
        elif idx == 8:
            column_mapping[col] = '检测抽血次数'
        elif idx == 9:
            column_mapping[col] = '孕周'
        elif idx == 10:
            column_mapping[col] = 'BMI'
        elif idx == 11:
            column_mapping[col] = '总读数'
        elif idx == 12:
            column_mapping[col] = '比对比例'
        elif idx == 13:
            column_mapping[col] = '重复读数比例'
        elif idx == 14:
            column_mapping[col] = '唯一比对读数'
        elif idx == 15:
            column_mapping[col] = 'GC含量'
        elif idx == 16:
            column_mapping[col] = '13号染色体Z值'
        elif idx == 17:
            column_mapping[col] = '18号染色体Z值'
        elif idx == 18:
            column_mapping[col] = '21号染色体Z值'
        elif idx == 19:
            column_mapping[col] = 'X染色体Z值'
        elif idx == 20:
            column_mapping[col] = 'Y染色体Z值'
        elif idx == 21:
            column_mapping[col] = 'Y染色体浓度'
        elif idx == 22:
            column_mapping[col] = 'X染色体浓度'
        elif idx == 23:
            column_mapping[col] = '13号染色体GC含量'
        elif idx == 24:
            column_mapping[col] = '18号染色体GC含量'
        elif idx == 25:
            column_mapping[col] = '21号染色体GC含量'
        elif idx == 26:
            column_mapping[col] = '过滤读数比例'
        elif idx == 27:
            column_mapping[col] = '染色体非整倍体'
        elif idx == 28:
            column_mapping[col] = '怀孕次数'
        elif idx == 29:
            column_mapping[col] = '生产次数'
        elif idx == 30:
            column_mapping[col] = '胎儿是否健康'

    df.rename(columns=column_mapping, inplace=True)

    # 3. 处理孕周数据
    def convert_gestational_week(week_str):
        """转换孕周格式为数值"""
        try:
            if pd.isna(week_str):
                return np.nan

            week_str = str(week_str).strip()

            # 处理'13w+4'格式
            if 'w' in week_str.lower():
                week_str = week_str.lower().replace('w', '').replace('周', '')
                if '+' in week_str:
                    weeks, days = week_str.split('+')
                    return float(weeks) + float(days) / 7
                else:
                    return float(week_str)

            # 处理'12+3'格式
            elif '+' in week_str:
                weeks, days = week_str.split('+')
                return float(weeks) + float(days) / 7

            # 纯数字
            return float(week_str)

        except:
            return np.nan

    df['孕周数值'] = df['孕周'].apply(convert_gestational_week)

    # 4. 分离男女胎数据
    # 转换为数值类型
    df['Y染色体浓度'] = pd.to_numeric(df['Y染色体浓度'], errors='coerce')

    # 男胎: Y染色体浓度 > 0
    df_male = df[df['Y染色体浓度'] > 0].copy()
    # 女胎: Y染色体浓度为0或空
    df_female = df[df['Y染色体浓度'] == 0].copy()

    print(f"\n数据分离结果:")
    print(f"  男胎数据: {len(df_male)} 行")
    print(f"  女胎数据: {len(df_female)} 行")
    print(f"  其他/无效数据: {len(df) - len(df_male) - len(df_female)} 行")

    # 5. 标记男胎达标情况
    df_male['达标标志'] = (df_male['Y染色体浓度'] >= 0.04).astype(int)

    # 6. 标记女胎异常情况
    # 根据染色体非整倍体列判断
    df_female['异常标志'] = df_female['染色体非整倍体'].notna().astype(int)

    # 7. 基本统计
    print(f"\n男胎数据统计:")
    print(f"  达标比例: {df_male['达标标志'].mean():.2%}")
    print(f"  平均孕周: {df_male['孕周数值'].mean():.1f}周")
    print(f"  平均BMI: {df_male['BMI'].mean():.1f}")
    print(f"  平均年龄: {df_male['年龄'].mean():.1f}岁")

    if len(df_female) > 0:
        print(f"\n女胎数据统计:")
        print(f"  异常比例: {df_female['异常标志'].mean():.2%}")
        print(f"  平均孕周: {df_female['孕周数值'].mean():.1f}周")

    return df, df_male, df_female


# 问题1：Y染色体浓度与孕周、BMI的关系模型

def solve_problem1(df_male):
    """问题1：分析Y染色体浓度与孕周、BMI的关系"""
    print("\n" + "=" * 60)
    print("问题1：Y染色体浓度与孕周、BMI的关系分析")
    print("=" * 60)

    # 1. 相关性分析
    print("\n1. 相关性分析:")

    # 计算相关系数
    corr_matrix = df_male[['Y染色体浓度', '孕周数值', 'BMI', '年龄', '体重']].corr()

    plt.figure(figsize=(8, 6))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.3f')
    plt.title('变量间相关系数矩阵')
    plt.tight_layout()
    plt.savefig('问题1_相关系数矩阵.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 显著性检验
    print("\n2. 显著性检验 (Pearson相关系数):")
    variables = ['孕周数值', 'BMI', '年龄', '体重']
    for var in variables:
        if var in df_male.columns:
            corr, p_value = pearsonr(df_male[var].dropna(),
                                     df_male['Y染色体浓度'].dropna())
            print(f"  Y浓度 vs {var}: r = {corr:.4f}, p = {p_value:.6f}")
            if p_value < 0.05:
                print(f"    → 相关性显著 (p < 0.05)")

    # 2. 回归模型
    print("\n3. 多元线性回归模型:")

    # 准备数据
    X = df_male[['孕周数值', 'BMI', '年龄']].dropna()
    y = df_male.loc[X.index, 'Y染色体浓度']

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 添加常数项
    X_sm = sm.add_constant(X_scaled)

    # OLS回归
    model_ols = sm.OLS(y, X_sm).fit()
    print(model_ols.summary())

    # 3. 可视化关系
    print("\n4. 可视化分析:")

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Y浓度 vs 孕周
    axes[0, 0].scatter(df_male['孕周数值'], df_male['Y染色体浓度'], alpha=0.6)
    # 添加回归线
    z = np.polyfit(df_male['孕周数值'].dropna(),
                   df_male['Y染色体浓度'].dropna(), 1)
    p = np.poly1d(z)
    axes[0, 0].plot(sorted(df_male['孕周数值'].dropna()),
                    p(sorted(df_male['孕周数值'].dropna())),
                    "r--", alpha=0.8)
    axes[0, 0].set_xlabel('孕周')
    axes[0, 0].set_ylabel('Y染色体浓度')
    axes[0, 0].set_title('Y染色体浓度 vs 孕周')
    axes[0, 0].axhline(y=0.04, color='g', linestyle='--', alpha=0.5, label='4%阈值')
    axes[0, 0].legend()

    # Y浓度 vs BMI
    axes[0, 1].scatter(df_male['BMI'], df_male['Y染色体浓度'], alpha=0.6)
    z = np.polyfit(df_male['BMI'].dropna(),
                   df_male['Y染色体浓度'].dropna(), 1)
    p = np.poly1d(z)
    axes[0, 1].plot(sorted(df_male['BMI'].dropna()),
                    p(sorted(df_male['BMI'].dropna())),
                    "r--", alpha=0.8)
    axes[0, 1].set_xlabel('BMI')
    axes[0, 1].set_ylabel('Y染色体浓度')
    axes[0, 1].set_title('Y染色体浓度 vs BMI')
    axes[0, 1].axhline(y=0.04, color='g', linestyle='--', alpha=0.5)

    # 达标比例 vs 孕周 (修正部分)
    达标_by_week = df_male.groupby(pd.cut(df_male['孕周数值'], bins=range(10, 27, 2)))['达标标志'].mean()

    axes[1, 0].bar(range(len(达标_by_week)), 达标_by_week.values)
    axes[1, 0].set_xticks(range(len(达标_by_week)))
    axes[1, 0].set_xticklabels([f"{i}-{i + 2}" for i in range(10, 26, 2)], rotation=45)
    axes[1, 0].set_xlabel('孕周区间')
    axes[1, 0].set_ylabel('达标比例')
    axes[1, 0].set_title('不同孕周区间达标比例')
    axes[1, 0].axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='50%达标线')
    axes[1, 0].legend()

    # 达标比例 vs BMI (修正部分)
    达标_by_bmi = df_male.groupby(pd.cut(df_male['BMI'], bins=[20, 28, 32, 36, 40, 50]))['达标标志'].mean()

    axes[1, 1].bar(range(len(达标_by_bmi)), 达标_by_bmi.values)
    axes[1, 1].set_xticks(range(len(达标_by_bmi)))
    axes[1, 1].set_xticklabels(['20-28', '28-32', '32-36', '36-40', '40+'], rotation=45)
    axes[1, 1].set_xlabel('BMI区间')
    axes[1, 1].set_ylabel('达标比例')
    axes[1, 1].set_title('不同BMI区间达标比例')
    axes[1, 1].axhline(y=0.5, color='r', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig('问题1_可视化分析.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 4. 非线性模型尝试（多项式回归）
    print("\n5. 非线性模型（多项式回归）:")

    from sklearn.preprocessing import PolynomialFeatures
    from sklearn.pipeline import make_pipeline

    poly_model = make_pipeline(
        PolynomialFeatures(degree=2, include_bias=False),
        StandardScaler(),
        LinearRegression()
    )

    X_poly = df_male[['孕周数值', 'BMI']].dropna()
    y_poly = df_male.loc[X_poly.index, 'Y染色体浓度']

    poly_model.fit(X_poly, y_poly)
    y_pred_poly = poly_model.predict(X_poly)

    r2_poly = r2_score(y_poly, y_pred_poly)
    mse_poly = mean_squared_error(y_poly, y_pred_poly)

    print(f"  多项式回归R²: {r2_poly:.4f}")
    print(f"  多项式回归MSE: {mse_poly:.6f}")

    return {
        'correlation_matrix': corr_matrix,
        'regression_model': model_ols,
        'poly_model': poly_model,
        '达标_by_week': 达标_by_week,
        '达标_by_bmi': 达标_by_bmi
    }

# 问题2：基于BMI分组的最佳NIPT时点

def solve_problem2(df_male):
    """问题2：基于BMI分组的最佳NIPT时点"""
    print("\n" + "=" * 60)
    print("问题2：基于BMI分组的最佳NIPT时点")
    print("=" * 60)

    # 1. BMI分组策略
    print("\n1. BMI分组分析:")

    # 使用题目建议的分组
    bmi_bins = [20, 28, 32, 36, 40, 100]  # 40以上
    bmi_labels = ['20-28', '28-32', '32-36', '36-40', '40+']

    # 修正：创建新的BMI分组列
    df_male['BMI分组_str'] = pd.cut(df_male['BMI'], bins=bmi_bins, labels=bmi_labels)
    df_male['BMI分组'] = pd.cut(df_male['BMI'], bins=bmi_bins)

    # 统计各组样本量
    group_stats = df_male.groupby('BMI分组_str').agg({
        'BMI': ['count', 'min', 'max', 'mean'],
        'Y染色体浓度': 'mean',
        '达标标志': 'mean',
        '孕周数值': 'mean'
    }).round(3)

    print("BMI分组统计:")
    print(group_stats)

    # 2. 计算每组最早达标时间
    print("\n2. 计算各组最早达标时间:")

    def find_earliest达标_time(group_data):
        """找到组内达到4%阈值的最早孕周"""
        # 筛选达标样本
        达标_samples = group_data[group_data['达标标志'] == 1]

        if len(达标_samples) > 0:
            # 找到最早达标孕周
            earliest_week = 达标_samples['孕周数值'].min()

            # 计算该孕周的达标比例
            if len(group_data) > 0:
                达标_at_time = len(group_data[group_data['孕周数值'] <= earliest_week]) / len(group_data)
            else:
                达标_at_time = 0

            return earliest_week, 达标_at_time
        else:
            return None, 0

    optimal_times = {}
    for group in bmi_labels:
        group_data = df_male[df_male['BMI分组_str'] == group]  # 修正：使用字符串标签
        earliest_week, 达标_prop = find_earliest达标_time(group_data)

        if earliest_week is not None:
            optimal_times[group] = {
                'BMI范围': group,
                '样本量': len(group_data),
                '最早达标孕周': earliest_week,
                '达标比例': 达标_prop,
                '建议检测时点': earliest_week  # 最早达标时间即为建议时点
            }
        else:
            optimal_times[group] = {
                'BMI范围': group,
                '样本量': len(group_data),
                '最早达标孕周': None,
                '达标比例': 0,
                '建议检测时点': None
            }

    optimal_df = pd.DataFrame(optimal_times).T
    print("\n各组最佳检测时点:")
    print(optimal_df[['BMI范围', '样本量', '最早达标孕周', '达标比例', '建议检测时点']])

    # 3. 风险分析
    print("\n3. 风险分析:")

    def calculate_risk(detection_week):
        """计算检测时点的风险"""
        if detection_week is None:
            return np.nan
        elif detection_week <= 12:
            return 0.1  # 低风险
        elif detection_week <= 27:
            return 0.5  # 高风险
        else:
            return 0.9  # 极高风险

    # 计算各组风险
    for group in optimal_df.index:
        week = optimal_df.loc[group, '建议检测时点']
        risk = calculate_risk(week)
        optimal_df.loc[group, '风险评分'] = risk

    print("\n包含风险评分的建议时点:")
    print(optimal_df[['BMI范围', '建议检测时点', '风险评分', '达标比例']])

    # 4. 检测误差影响分析
    print("\n4. 检测误差影响分析:")

    def analyze_error_impact(group_data, error_levels=[0.01, 0.02, 0.03, 0.05]):
        """分析检测误差对结果的影响"""
        results = {}

        original_week, _ = find_earliest达标_time(group_data)

        for error in error_levels:
            # 模拟有误差的数据
            np.random.seed(42)
            errors = np.random.normal(0, error, len(group_data))
            simulated_concentration = group_data['Y染色体浓度'].values * (1 + errors)

            # 创建模拟数据
            sim_data = group_data.copy()
            sim_data['Y染色体浓度_模拟'] = simulated_concentration
            sim_data['达标标志_模拟'] = (simulated_concentration >= 0.04).astype(int)

            # 找到最早达标时间
            达标_samples_sim = sim_data[sim_data['达标标志_模拟'] == 1]
            if len(达标_samples_sim) > 0:
                earliest_week_sim = 达标_samples_sim['孕周数值'].min()
                time_diff = abs(earliest_week_sim - original_week) if original_week else np.nan
            else:
                earliest_week_sim = None
                time_diff = np.nan

            results[f'误差{int(error * 100)}%'] = {
                '模拟最早达标孕周': earliest_week_sim,
                '时间差异(周)': time_diff
            }

        return results

    # 对每个BMI组进行误差分析
    error_analysis = {}
    for group in bmi_labels:
        group_data = df_male[df_male['BMI分组_str'] == group]  # 修正：使用字符串标签
        if len(group_data) > 10:  # 只分析有足够样本的组
            error_results = analyze_error_impact(group_data)
            error_analysis[group] = error_results

    print("\n检测误差对最早达标时间的影响:")
    for group, results in error_analysis.items():
        print(f"\nBMI组 {group}:")
        for error_level, result in results.items():
            print(f"  {error_level}: 模拟最早达标孕周 = {result['模拟最早达标孕周']:.1f}, " +
                  f"时间差异 = {result['时间差异(周)']:.2f}周")

    # 5. 可视化
    plt.figure(figsize=(12, 5))

    # 子图1：各组的达标曲线
    plt.subplot(121)
    for group in bmi_labels:
        group_data = df_male[df_male['BMI分组_str'] == group]  # 修正：使用字符串标签
        if len(group_data) > 0:
            # 计算每个孕周的达标比例
            达标_curve = []
            weeks_range = np.arange(10, 26, 0.5)
            for week in weeks_range:
                达标_samples = group_data[group_data['孕周数值'] <= week]
                if len(达标_samples) > 0:
                    达标_prop = 达标_samples['达标标志'].mean()
                else:
                    达标_prop = 0
                达标_curve.append(达标_prop)

            plt.plot(weeks_range, 达标_curve, label=f'BMI {group}', linewidth=2)

    plt.axhline(y=0.5, color='gray', linestyle='--', alpha=0.5, label='50%达标线')
    plt.axvline(x=12, color='green', linestyle='--', alpha=0.5, label='早期截止(12周)')
    plt.axvline(x=27, color='red', linestyle='--', alpha=0.5, label='中期截止(27周)')
    plt.xlabel('孕周')
    plt.ylabel('累积达标比例')
    plt.title('不同BMI组的累积达标曲线')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)

    # 子图2：最佳检测时点与风险
    plt.subplot(122)
    groups = optimal_df.index
    weeks = optimal_df['建议检测时点'].fillna(0)  # 处理空值
    risks = optimal_df['风险评分']

    bars = plt.bar(range(len(groups)), weeks)
    plt.xticks(range(len(groups)), groups, rotation=45)
    plt.xlabel('BMI分组')
    plt.ylabel('建议检测孕周')
    plt.title('各BMI组的最佳检测时点')

    # 添加风险颜色指示
    for i, (bar, risk) in enumerate(zip(bars, risks)):
        if pd.isna(risk):
            bar.set_color('gray')
        elif risk <= 0.1:
            bar.set_color('green')
        elif risk <= 0.5:
            bar.set_color('orange')
        else:
            bar.set_color('red')

        # 标注风险等级
        if not pd.isna(risk):
            plt.text(i, bar.get_height() + 0.2, f'风险:{risk:.1f}',
                     ha='center', va='bottom', fontsize=9)

    plt.axhline(y=12, color='green', linestyle='--', alpha=0.5, label='低风险区')
    plt.axhline(y=27, color='red', linestyle='--', alpha=0.5, label='高风险区')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('问题2_最佳检测时点.png', dpi=300, bbox_inches='tight')
    plt.show()

    return {
        'optimal_times': optimal_df,
        'error_analysis': error_analysis,
        'group_stats': group_stats
    }


# 问题3：多因素综合考虑的最佳NIPT时点

def solve_problem3(df_male):
    """问题3：多因素综合考虑的最佳NIPT时点"""
    print("\n" + "=" * 60)
    print("问题3：多因素综合考虑的最佳NIPT时点")
    print("=" * 60)

    # 1. 多因素聚类分组
    print("\n1. 多因素聚类分组:")

    # 选择用于聚类的特征
    clustering_features = ['BMI', '年龄', '体重', '孕周数值']
    clustering_data = df_male[clustering_features].dropna()

    # 标准化
    scaler_cluster = StandardScaler()
    X_cluster_scaled = scaler_cluster.fit_transform(clustering_data)

    # 使用K-means聚类
    # 寻找最佳聚类数
    inertia = []
    silhouette_scores = []
    k_range = range(2, 8)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_cluster_scaled)
        inertia.append(kmeans.inertia_)

        from sklearn.metrics import silhouette_score
        if len(set(labels)) > 1:  # 需要至少2个聚类
            score = silhouette_score(X_cluster_scaled, labels)
            silhouette_scores.append(score)
        else:
            silhouette_scores.append(0)

    # 可视化选择聚类数
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].plot(k_range, inertia, 'o-')
    axes[0].set_xlabel('聚类数k')
    axes[0].set_ylabel('SSE（簇内平方和）')
    axes[0].set_title('肘部法则')
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(k_range, silhouette_scores, 'o-')
    axes[1].set_xlabel('聚类数k')
    axes[1].set_ylabel('轮廓系数')
    axes[1].set_title('轮廓系数法')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('问题3_聚类数选择.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 选择最佳聚类数（这里选择轮廓系数最高的）
    best_k = k_range[np.argmax(silhouette_scores)]
    print(f"  选择聚类数: k = {best_k} (轮廓系数最高)")

    # 进行聚类
    kmeans_final = KMeans(n_clusters=best_k, random_state=42, n_init=10)
    cluster_labels = kmeans_final.fit_predict(X_cluster_scaled)

    # 将聚类结果添加到数据中
    df_male.loc[clustering_data.index, '综合分组'] = cluster_labels

    # 2. 分析各组的特征
    print("\n2. 综合分组特征分析:")

    group_features = df_male.groupby('综合分组').agg({
        'BMI': ['mean', 'std', 'count'],
        '年龄': ['mean', 'std'],
        '体重': ['mean', 'std'],
        '孕周数值': ['mean', 'std'],
        'Y染色体浓度': 'mean',
        '达标标志': 'mean'
    }).round(3)

    print("各综合分组的特征统计:")
    print(group_features)

    # 3. 确定各组的最佳检测时点（考虑风险最小化）
    print("\n3. 确定各组的最佳检测时点（风险最小化）:")

    def calculate_combined_risk(detection_week, group_data):
        """计算综合风险"""
        # 1. 时间风险（基于孕周）
        if detection_week <= 12:
            time_risk = 0.1
        elif detection_week <= 27:
            time_risk = 0.5
        else:
            time_risk = 0.9

        # 2. 未达标风险
        # 估计在该孕周检测的达标概率
        达标_samples = group_data[group_data['孕周数值'] <= detection_week]
        if len(达标_samples) > 0:
            达标_prob = 达标_samples['达标标志'].mean()
        else:
            达标_prob = 0

        unqualified_risk = 1 - 达标_prob

        # 3. 综合风险（加权平均）
        combined_risk = 0.6 * time_risk + 0.4 * unqualified_risk

        return combined_risk

    optimal_times_multi = {}

    for group in sorted(df_male['综合分组'].dropna().unique()):
        group_data = df_male[df_male['综合分组'] == group]

        # 找到风险最小的检测时点
        week_range = np.arange(10, 26, 0.5)  # 10-25周，步长0.5周

        risks = []
        for week in week_range:
            risk = calculate_combined_risk(week, group_data)
            risks.append(risk)

        # 找到最小风险对应的孕周
        min_risk_idx = np.argmin(risks)
        optimal_week = week_range[min_risk_idx]
        min_risk = risks[min_risk_idx]

        # 计算该时点的达标比例
        if len(group_data) > 0:
            达标_at_optimal = len(group_data[group_data['孕周数值'] <= optimal_week]) / len(group_data)
        else:
            达标_at_optimal = 0

        optimal_times_multi[group] = {
            '样本量': len(group_data),
            '平均BMI': group_data['BMI'].mean(),
            '平均年龄': group_data['年龄'].mean(),
            '最佳检测孕周': optimal_week,
            '最小风险': min_risk,
            '达标比例': 达标_at_optimal,
            '时间风险': calculate_combined_risk(optimal_week, group_data)
        }

    optimal_multi_df = pd.DataFrame(optimal_times_multi).T
    print("\n各综合分组的最佳检测时点:")
    print(optimal_multi_df[['样本量', '平均BMI', '平均年龄', '最佳检测孕周', '最小风险', '达标比例']])

    # 4. 可视化
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 子图1：各组特征雷达图（简化版）
    groups = sorted(df_male['综合分组'].dropna().unique())
    n_groups = len(groups)

    # 准备特征数据
    features = ['平均BMI', '平均年龄', '平均孕周', '达标比例']
    feature_data = []

    for group in groups:
        group_data = df_male[df_male['综合分组'] == group]
        feature_values = [
            group_data['BMI'].mean(),
            group_data['年龄'].mean(),
            group_data['孕周数值'].mean(),
            group_data['达标标志'].mean()
        ]
        feature_data.append(feature_values)

    # 转换为DataFrame方便绘制
    feature_df = pd.DataFrame(feature_data, columns=features, index=[f'组{i}' for i in groups])

    # 标准化特征用于比较
    feature_df_normalized = (feature_df - feature_df.min()) / (feature_df.max() - feature_df.min())

    # 绘制条形图代替雷达图
    x = np.arange(len(features))
    width = 0.8 / n_groups

    for i, group in enumerate(groups):
        axes[0, 0].bar(x + i * width - width * (n_groups - 1) / 2,
                       feature_df_normalized.iloc[i],
                       width, label=f'组{group}')

    axes[0, 0].set_xlabel('特征')
    axes[0, 0].set_ylabel('标准化值')
    axes[0, 0].set_title('各综合分组特征比较')
    axes[0, 0].set_xticks(x)
    axes[0, 0].set_xticklabels(features, rotation=45)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 子图2：最佳检测时点与风险
    axes[0, 1].scatter(optimal_multi_df['最佳检测孕周'],
                       optimal_multi_df['最小风险'],
                       s=optimal_multi_df['样本量'] * 10,  # 点大小表示样本量
                       alpha=0.7)

    for i, row in optimal_multi_df.iterrows():
        axes[0, 1].text(row['最佳检测孕周'], row['最小风险'],
                        f"组{i}", fontsize=9, ha='center', va='bottom')

    axes[0, 1].set_xlabel('最佳检测孕周')
    axes[0, 1].set_ylabel('最小风险')
    axes[0, 1].set_title('最佳检测时点与风险')
    axes[0, 1].axvline(x=12, color='green', linestyle='--', alpha=0.5, label='12周')
    axes[0, 1].axvline(x=27, color='red', linestyle='--', alpha=0.5, label='27周')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3)

    # 子图3：达标曲线对比
    axes[1, 0].set_title('各综合分组的累积达标曲线')
    axes[1, 0].set_xlabel('孕周')
    axes[1, 0].set_ylabel('累积达标比例')

    for group in groups[:4]:  # 最多显示4组
        group_data = df_male[df_male['综合分组'] == group]
        if len(group_data) > 0:
            达标_curve = []
            weeks_range = np.arange(10, 26, 0.5)
            for week in weeks_range:
                达标_samples = group_data[group_data['孕周数值'] <= week]
                if len(达标_samples) > 0:
                    达标_prop = 达标_samples['达标标志'].mean()
                else:
                    达标_prop = 0
                达标_curve.append(达标_prop)

            axes[1, 0].plot(weeks_range, 达标_curve, label=f'组{group}', linewidth=2)

    axes[1, 0].axhline(y=0.5, color='gray', linestyle='--', alpha=0.5)
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # 子图4：风险与达标比例的关系
    axes[1, 1].scatter(optimal_multi_df['达标比例'],
                       optimal_multi_df['最小风险'],
                       s=optimal_multi_df['样本量'] * 10,  # 点大小表示样本量
                       alpha=0.7)

    for i, row in optimal_multi_df.iterrows():
        axes[1, 1].text(row['达标比例'], row['最小风险'],
                        f"组{i}", fontsize=9, ha='center', va='bottom')

    axes[1, 1].set_xlabel('达标比例')
    axes[1, 1].set_ylabel('最小风险')
    axes[1, 1].set_title('达标比例与风险的关系')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('问题3_综合分组分析.png', dpi=300, bbox_inches='tight')
    plt.show()

    return {
        'optimal_times': optimal_multi_df,
        'group_features': group_features,
        'kmeans_model': kmeans_final,
        'feature_df': feature_df
    }

# 问题4：女胎异常判定方法

def solve_problem4(df_female):
    """问题4：女胎异常判定方法"""
    print("\n" + "=" * 60)
    print("问题4：女胎异常判定方法")
    print("=" * 60)

    if len(df_female) == 0:
        print("警告: 无女胎数据，无法进行异常判定")
        return None

    # 1. 数据准备
    print("\n1. 数据准备与特征工程:")

    # 确保关键列存在
    required_cols = ['21号染色体Z值', '18号染色体Z值', '13号染色体Z值',
                     'X染色体Z值', '21号染色体GC含量', '18号染色体GC含量',
                     '13号染色体GC含量', 'X染色体浓度', 'BMI', '年龄', '总读数',
                     '唯一比对读数', 'GC含量', '过滤读数比例', '染色体非整倍体']

    # 检查并处理缺失列
    available_cols = [col for col in required_cols if col in df_female.columns]
    missing_cols = [col for col in required_cols if col not in df_female.columns]

    if missing_cols:
        print(f"  缺失列: {missing_cols}")
        print("  将使用可用列进行分析")

    # 创建目标变量
    # 方法1：使用染色体非整倍体列
    if '染色体非整倍体' in df_female.columns:
        df_female['异常标志'] = df_female['染色体非整倍体'].notna().astype(int)
        print(f"  使用染色体非整倍体作为异常标志，异常比例: {df_female['异常标志'].mean():.2%}")
    # 方法2：如果AE列（胎儿是否健康）存在
    elif '胎儿是否健康' in df_female.columns:
        # 假设1为健康，0或不健康为异常
        df_female['异常标志'] = (df_female['胎儿是否健康'] != 1).astype(int)
        print(f"  使用胎儿是否健康作为异常标志，异常比例: {df_female['异常标志'].mean():.2%}")
    else:
        # 方法3：使用Z值阈值判断
        print("  使用Z值阈值判断异常")
        # 根据Z值绝对值>3判断异常
        z_cols = ['21号染色体Z值', '18号染色体Z值', '13号染色体Z值']
        z_cols_available = [col for col in z_cols if col in df_female.columns]

        if z_cols_available:
            z_abnormal = df_female[z_cols_available].abs().max(axis=1) > 3
            df_female['异常标志'] = z_abnormal.astype(int)
            print(f"  使用Z值阈值判断，异常比例: {df_female['异常标志'].mean():.2%}")
        else:
            print("  无法创建异常标志，跳过问题4分析")
            return None

    # 2. 特征选择与处理
    print("\n2. 特征选择与处理:")

    # 特征列表（根据题目要求）
    feature_candidates = {
        'Z值特征': ['21号染色体Z值', '18号染色体Z值', '13号染色体Z值', 'X染色体Z值'],
        'GC含量特征': ['21号染色体GC含量', '18号染色体GC含量', '13号染色体GC含量', 'GC含量'],
        '浓度特征': ['X染色体浓度'],
        '测序质量特征': ['总读数', '唯一比对读数', '过滤读数比例', '比对比例', '重复读数比例'],
        '孕妇特征': ['BMI', '年龄', '体重', '身高']
    }

    # 收集所有可用特征
    all_features = []
    feature_groups = {}

    for group_name, features in feature_candidates.items():
        available_features = [f for f in features if f in df_female.columns]
        if available_features:
            all_features.extend(available_features)
            feature_groups[group_name] = available_features
            print(f"  {group_name}: {len(available_features)}个特征")

    print(f"\n  总共选择 {len(all_features)} 个特征用于建模")

    # 3. 数据预处理
    print("\n3. 数据预处理:")

    # 创建特征矩阵
    X = df_female[all_features].copy()
    y = df_female['异常标志']

    # 处理缺失值
    print(f"  缺失值处理前: {X.shape[0]}行 × {X.shape[1]}列")
    X = X.fillna(X.median())
    print(f"  缺失值处理后: {X.shape[0]}行 × {X.shape[1]}列")

    # 检查类别平衡
    class_distribution = y.value_counts()
    print(f"  类别分布: 正常={class_distribution.get(0, 0)}, 异常={class_distribution.get(1, 0)}")
    print(f"  异常比例: {y.mean():.2%}")

    # 4. 构建分类模型
    print("\n4. 构建分类模型:")

    # 划分训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    print(f"  训练集: {X_train.shape[0]}个样本")
    print(f"  测试集: {X_test.shape[0]}个样本")

    # 特征标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 4.1 随机森林模型
    print("\n4.1 随机森林模型:")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced',
        n_jobs=-1
    )

    rf_model.fit(X_train_scaled, y_train)
    y_pred_rf = rf_model.predict(X_test_scaled)
    y_pred_proba_rf = rf_model.predict_proba(X_test_scaled)[:, 1]

    # 评估
    print("  分类报告:")
    print(classification_report(y_test, y_pred_rf))
    print(f"  AUC分数: {roc_auc_score(y_test, y_pred_proba_rf):.4f}")

    # 4.2 逻辑回归模型
    print("\n4.2 逻辑回归模型:")
    lr_model = LogisticRegression(
        max_iter=1000,
        random_state=42,
        class_weight='balanced',
        solver='liblinear'
    )

    lr_model.fit(X_train_scaled, y_train)
    y_pred_lr = lr_model.predict(X_test_scaled)
    y_pred_proba_lr = lr_model.predict_proba(X_test_scaled)[:, 1]

    print("  分类报告:")
    print(classification_report(y_test, y_pred_lr))
    print(f"  AUC分数: {roc_auc_score(y_test, y_pred_proba_lr):.4f}")

    # 5. 特征重要性分析
    print("\n5. 特征重要性分析:")

    # 随机森林特征重要性
    feature_importance = pd.DataFrame({
        '特征': all_features,
        '重要性': rf_model.feature_importances_
    }).sort_values('重要性', ascending=False)

    print("\n  随机森林特征重要性 Top 10:")
    print(feature_importance.head(10))

    # 可视化特征重要性
    plt.figure(figsize=(12, 6))
    top_n = min(15, len(feature_importance))
    plt.barh(range(top_n), feature_importance['重要性'].head(top_n)[::-1])
    plt.yticks(range(top_n), feature_importance['特征'].head(top_n)[::-1])
    plt.xlabel('特征重要性')
    plt.title('女胎异常判定的特征重要性 (随机森林)')
    plt.tight_layout()
    plt.savefig('问题4_特征重要性.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 6. 综合判定规则
    print("\n6. 综合判定规则:")

    # 修改 comprehensive_judgment 函数中的这部分代码：

    def comprehensive_judgment(row, rf_model, lr_model, scaler, threshold_rf=0.5, threshold_lr=0.5):
        """综合判定女胎是否异常"""
        results = {}

        # 规则1：染色体Z值异常（绝对值>3）
        z_score_abnormal = False
        z_details = []

        z_cols = ['21号染色体Z值', '18号染色体Z值', '13号染色体Z值']
        for col in z_cols:
            if col in row and not pd.isna(row[col]):
                if abs(row[col]) > 3:
                    z_score_abnormal = True
                    z_details.append(f"{col}: {row[col]:.2f}")

        results['Z值异常'] = z_score_abnormal
        results['Z值异常详情'] = z_details

        # 规则2：GC含量异常
        gc_abnormal = False
        gc_details = []

        gc_cols = ['21号染色体GC含量', '18号染色体GC含量', '13号染色体GC含量', 'GC含量']
        for col in gc_cols:
            if col in row and not pd.isna(row[col]):
                if row[col] < 40 or row[col] > 60:
                    gc_abnormal = True
                    gc_details.append(f"{col}: {row[col]:.1f}%")

        results['GC含量异常'] = gc_abnormal
        results['GC含量异常详情'] = gc_details

        # 规则3：模型预测
        # 准备特征向量 - 修正这部分
        feature_dict = {}
        for feature in all_features:
            if feature in row:
                feature_dict[feature] = row[feature]
            else:
                feature_dict[feature] = np.nan

        feature_vector = pd.DataFrame([feature_dict])

        if not feature_vector.empty:
            # 处理缺失值
            feature_vector_filled = feature_vector.fillna(feature_vector.median())

            # 确保特征顺序一致
            feature_vector_filled = feature_vector_filled[all_features]

            # 标准化
            feature_vector_scaled = scaler.transform(feature_vector_filled)

            # 随机森林预测
            rf_prob = rf_model.predict_proba(feature_vector_scaled)[0, 1]
            rf_judgment = rf_prob > threshold_rf

            # 逻辑回归预测
            lr_prob = lr_model.predict_proba(feature_vector_scaled)[0, 1]
            lr_judgment = lr_prob > threshold_lr

            results['RF概率'] = rf_prob
            results['RF判定'] = rf_judgment
            results['LR概率'] = lr_prob
            results['LR判定'] = lr_judgment

            # 综合模型判定（投票）
            model_votes = sum([rf_judgment, lr_judgment])
            results['模型投票'] = model_votes
            results['模型综合判定'] = model_votes >= 1  # 至少一个模型判定为异常
        else:
            results['RF概率'] = 0
            results['RF判定'] = False
            results['LR概率'] = 0
            results['LR判定'] = False
            results['模型投票'] = 0
            results['模型综合判定'] = False

        # 规则4：X染色体浓度异常
        x_conc_abnormal = False
        if 'X染色体浓度' in row and not pd.isna(row['X染色体浓度']):
            # X染色体浓度通常应为正值，负值或极端值可能异常
            if row['X染色体浓度'] < 0 or row['X染色体浓度'] > 0.2:
                x_conc_abnormal = True
                results['X染色体浓度异常'] = f"{row['X染色体浓度']:.4f}"

        results['X染色体浓度异常标志'] = x_conc_abnormal

        # 最终综合判定
        # 权重：Z值异常(0.4) + 模型判定(0.3) + GC异常(0.2) + X浓度异常(0.1)
        final_score = 0
        if z_score_abnormal:
            final_score += 0.4
        if results.get('模型综合判定', False):
            final_score += 0.3
        if gc_abnormal:
            final_score += 0.2
        if x_conc_abnormal:
            final_score += 0.1

        results['综合评分'] = final_score
        results['最终判定'] = final_score >= 0.5  # 阈值设为0.5

        # 风险等级
        if final_score >= 0.7:
            results['风险等级'] = '高风险'
        elif final_score >= 0.5:
            results['风险等级'] = '中风险'
        elif final_score >= 0.3:
            results['风险等级'] = '低风险'
        else:
            results['风险等级'] = '正常'

        return results

    # 测试综合判定规则
    print("\n  综合判定规则测试:")
    test_samples = X_test.head(5).copy()

    for idx, (sample_idx, row) in enumerate(test_samples.iterrows()):
        # 将Series转换为字典
        row_dict = row.to_dict()
        # 添加真实标签
        row_dict['真实标签'] = y_test.loc[sample_idx] if sample_idx in y_test.index else 0

        # 进行综合判定
        judgment = comprehensive_judgment(row_dict, rf_model, lr_model, scaler)

        print(f"\n  样本 {idx + 1}:")
        print(f"    真实标签: {'异常' if row_dict['真实标签'] == 1 else '正常'}")
        print(f"    综合评分: {judgment['综合评分']:.2f}")
        print(f"    最终判定: {'异常' if judgment['最终判定'] else '正常'}")
        print(f"    风险等级: {judgment['风险等级']}")

        if judgment['Z值异常']:
            print(f"    Z值异常: {', '.join(judgment['Z值异常详情'])}")
        if judgment['GC含量异常']:
            print(f"    GC含量异常: {', '.join(judgment['GC含量异常详情'])}")

    # 7. 模型性能可视化
    print("\n7. 模型性能可视化:")

    from sklearn.metrics import roc_curve, confusion_matrix

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # 子图1：ROC曲线
    # 随机森林ROC
    fpr_rf, tpr_rf, _ = roc_curve(y_test, y_pred_proba_rf)
    axes[0, 0].plot(fpr_rf, tpr_rf, label=f'随机森林 (AUC={roc_auc_score(y_test, y_pred_proba_rf):.3f})')

    # 逻辑回归ROC
    fpr_lr, tpr_lr, _ = roc_curve(y_test, y_pred_proba_lr)
    axes[0, 0].plot(fpr_lr, tpr_lr, label=f'逻辑回归 (AUC={roc_auc_score(y_test, y_pred_proba_lr):.3f})')

    axes[0, 0].plot([0, 1], [0, 1], 'k--', alpha=0.5)
    axes[0, 0].set_xlabel('假阳性率')
    axes[0, 0].set_ylabel('真阳性率')
    axes[0, 0].set_title('ROC曲线')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3)

    # 子图2：混淆矩阵（随机森林）
    cm_rf = confusion_matrix(y_test, y_pred_rf)
    sns.heatmap(cm_rf, annot=True, fmt='d', cmap='Blues', ax=axes[0, 1])
    axes[0, 1].set_xlabel('预测标签')
    axes[0, 1].set_ylabel('真实标签')
    axes[0, 1].set_title('随机森林混淆矩阵')

    # 子图3：特征重要性条形图
    top_features = feature_importance.head(10)
    axes[1, 0].barh(range(len(top_features)), top_features['重要性'])
    axes[1, 0].set_yticks(range(len(top_features)))
    axes[1, 0].set_yticklabels(top_features['特征'])
    axes[1, 0].set_xlabel('重要性')
    axes[1, 0].set_title('Top 10特征重要性')
    axes[1, 0].invert_yaxis()

    # 子图4：异常样本特征分布
    normal_samples = df_female[df_female['异常标志'] == 0]
    abnormal_samples = df_female[df_female['异常标志'] == 1]

    if len(abnormal_samples) > 0 and len(normal_samples) > 0:
        # 选择一个关键特征进行对比
        key_feature = '21号染色体Z值' if '21号染色体Z值' in df_female.columns else all_features[0]

        axes[1, 1].hist(normal_samples[key_feature].dropna(), alpha=0.5, label='正常', bins=30)
        axes[1, 1].hist(abnormal_samples[key_feature].dropna(), alpha=0.5, label='异常', bins=30)
        axes[1, 1].set_xlabel(key_feature)
        axes[1, 1].set_ylabel('频数')
        axes[1, 1].set_title(f'{key_feature}的分布对比')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('问题4_模型性能分析.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 8. 阈值优化
    print("\n8. 阈值优化:")

    def find_optimal_threshold(y_true, y_pred_proba):
        """寻找最佳分类阈值"""
        fpr, tpr, thresholds = roc_curve(y_true, y_pred_proba)

        # 计算Youden指数
        youden_index = tpr - fpr
        optimal_idx = np.argmax(youden_index)
        optimal_threshold = thresholds[optimal_idx]

        return optimal_threshold, youden_index[optimal_idx]

    # 随机森林阈值优化
    optimal_threshold_rf, youden_rf = find_optimal_threshold(y_test, y_pred_proba_rf)
    print(f"  随机森林最佳阈值: {optimal_threshold_rf:.3f} (Youden指数: {youden_rf:.3f})")

    # 逻辑回归阈值优化
    optimal_threshold_lr, youden_lr = find_optimal_threshold(y_test, y_pred_proba_lr)
    print(f"  逻辑回归最佳阈值: {optimal_threshold_lr:.3f} (Youden指数: {youden_lr:.3f})")

    # 9. 输出判定流程图
    print("\n9. 女胎异常判定流程图:")
    print("""
    ┌─────────────────────────────────────────────┐
    │          女胎异常判定流程                     │
    ├─────────────────────────────────────────────┤
    │ 1. 数据预处理                                │
    │    - 检查关键特征缺失                        │
    │    - 处理缺失值                              │
    │    - 特征标准化                              │
    ├─────────────────────────────────────────────┤
    │ 2. 多规则综合判定                            │
    │    (1) Z值异常检测: |Z| > 3                 │
    │    (2) GC含量异常: GC < 40% 或 GC > 60%     │
    │    (3) X染色体浓度异常: 负值或极端值         │
    │    (4) 机器学习模型预测                      │
    ├─────────────────────────────────────────────┤
    │ 3. 综合评分计算                              │
    │    权重: Z值(0.4) + 模型(0.3) + GC(0.2) + X(0.1) │
    ├─────────────────────────────────────────────┤
    │ 4. 风险等级划分                              │
    │    - 综合评分 ≥ 0.7: 高风险                 │
    │    - 0.5 ≤ 评分 < 0.7: 中风险               │
    │    - 0.3 ≤ 评分 < 0.5: 低风险               │
    │    - 评分 < 0.3: 正常                       │
    └─────────────────────────────────────────────┘
    """)

    return {
        'rf_model': rf_model,
        'lr_model': lr_model,
        'scaler': scaler,
        'feature_importance': feature_importance,
        'optimal_thresholds': {
            'rf': optimal_threshold_rf,
            'lr': optimal_threshold_lr
        },
        'comprehensive_judgment_func': comprehensive_judgment,
        'all_features': all_features
    }

# 执行主程序

if __name__ == "__main__":
    print("开始运行C5.py")
    print("=" * 60)

    try:
        # 1. 加载数据
        result = load_and_preprocess_data('附件.xlsx')

        if result is not None:
            df, df_male, df_female = result

            print("\n" + "=" * 60)
            print("开始分析问题")
            print("=" * 60)

            # 2. 解决问题1
            if len(df_male) > 0:
                result1 = solve_problem1(df_male)

                # 3. 解决问题2
                result2 = solve_problem2(df_male)

                # 4. 解决问题3
                result3 = solve_problem3(df_male)

                # 5. 解决问题4
                result4 = solve_problem4(df_male)

                print("\n" + "=" * 60)
                print("所有问题分析完成！")
                print("=" * 60)

                # 打印关键结果摘要
                print("\n关键结果摘要：")
                print(f"1. 男胎样本数：{len(df_male)}")
                print(f"2. 女胎样本数：{len(df_female)}")

                if 'optimal_times' in result2:
                    print("\n问题2结果：")
                    print(result2['optimal_times'])

                if 'optimal_times' in result3:
                    print("\n问题3结果：")
                    print(result3['optimal_times'])

            else:
                print("没有足够的男胎数据进行分析!!!")
        else:
            print("数据加载失败，请检查文件路径!!!")

    except Exception as e:
        print(f"程序执行出错：{e}")
        import traceback

        traceback.print_exc()