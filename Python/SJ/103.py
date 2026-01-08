import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error


# 假设已加载数据df_male（男胎数据）
def analyze_y_chromosome_relationship(df_male):
    """分析Y染色体浓度与孕周、BMI的关系"""

    print("=== 问题1：Y染色体浓度关系分析 ===")

    # 1. 数据清洗
    analysis_data = df_male[['孕周数值', 'BMI', 'Y染色体浓度']].dropna()

    print(f"有效样本数: {len(analysis_data)}")
    print(f"Y浓度范围: {analysis_data['Y染色体浓度'].min():.4f} - {analysis_data['Y染色体浓度'].max():.4f}")

    # 2. 描述性统计
    print("\n描述性统计:")
    print(analysis_data.describe())

    # 3. 相关性分析
    print("\n=== 相关性分析 ===")

    # Pearson相关系数
    corr_matrix = analysis_data.corr(method='pearson')
    print("Pearson相关系数矩阵:")
    print(corr_matrix)

    # 显著性检验
    for col in ['孕周数值', 'BMI']:
        corr_coef, p_value = stats.pearsonr(analysis_data[col], analysis_data['Y染色体浓度'])
        print(f"\nY浓度 vs {col}:")
        print(f"  相关系数: {corr_coef:.4f}")
        print(f"  p值: {p_value:.6f}")
        if p_value < 0.05:
            print(f"  结果: 显著相关 (p < 0.05)")
        else:
            print(f"  结果: 不显著相关")

    # 4. 可视化
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 散点图：Y浓度 vs 孕周
    axes[0, 0].scatter(analysis_data['孕周数值'], analysis_data['Y染色体浓度'], alpha=0.5)
    axes[0, 0].set_xlabel('孕周')
    axes[0, 0].set_ylabel('Y染色体浓度')
    axes[0, 0].set_title('Y浓度 vs 孕周')

    # 散点图：Y浓度 vs BMI
    axes[0, 1].scatter(analysis_data['BMI'], analysis_data['Y染色体浓度'], alpha=0.5, color='orange')
    axes[0, 1].set_xlabel('BMI')
    axes[0, 1].set_ylabel('Y染色体浓度')
    axes[0, 1].set_title('Y浓度 vs BMI')

    # 3D散点图
    from mpl_toolkits.mplot3d import Axes3D
    ax = fig.add_subplot(2, 2, 3, projection='3d')
    ax.scatter(analysis_data['孕周数值'], analysis_data['BMI'],
               analysis_data['Y染色体浓度'], alpha=0.6)
    ax.set_xlabel('孕周')
    ax.set_ylabel('BMI')
    ax.set_zlabel('Y染色体浓度')
    ax.set_title('Y浓度 vs 孕周和BMI (3D)')

    # 相关性热图
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                ax=axes[1, 1])
    axes[1, 1].set_title('相关性热图')

    plt.tight_layout()
    plt.savefig('问题1_相关性分析.png', dpi=300, bbox_inches='tight')
    plt.show()

    return analysis_data


def build_regression_models(analysis_data):
    """建立回归模型"""
    print("\n=== 回归模型建立 ===")

    X = analysis_data[['孕周数值', 'BMI']]
    y = analysis_data['Y染色体浓度']

    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 模型1：多元线性回归
    print("\n1. 多元线性回归模型:")
    X_with_const = sm.add_constant(X_scaled)
    model_lr = sm.OLS(y, X_with_const).fit()
    print(model_lr.summary())

    # 模型2：多项式回归
    print("\n2. 多项式回归模型 (二次):")
    from sklearn.preprocessing import PolynomialFeatures

    poly = PolynomialFeatures(degree=2, include_bias=False)
    X_poly = poly.fit_transform(X_scaled)

    model_poly = sm.OLS(y, sm.add_constant(X_poly)).fit()
    print(model_poly.summary())

    # 模型3：交互项回归
    print("\n3. 带交互项的回归模型:")
    X_interaction = X_scaled.copy()
    X_interaction = np.column_stack([X_interaction,
                                     X_interaction[:, 0] * X_interaction[:, 1]])  # 交互项

    model_inter = sm.OLS(y, sm.add_constant(X_interaction)).fit()
    print(model_inter.summary())

    # 模型比较
    models = {
        '线性回归': model_lr,
        '多项式回归': model_poly,
        '交互项回归': model_inter
    }

    print("\n=== 模型比较 ===")
    comparison_df = pd.DataFrame({
        '模型': list(models.keys()),
        'R²': [model.rsquared for model in models.values()],
        '调整R²': [model.rsquared_adj for model in models.values()],
        'AIC': [model.aic for model in models.values()],
        'BIC': [model.bic for model in models.values()]
    })
    print(comparison_df)

    # 选择最佳模型
    best_model_name = comparison_df.loc[comparison_df['调整R²'].idxmax(), '模型']
    print(f"\n最佳模型: {best_model_name}")

    return models[best_model_name], comparison_df