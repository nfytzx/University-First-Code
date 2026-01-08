import os
import pandas as pd
import numpy as np
import re
import warnings
from collections import Counter

warnings.filterwarnings('ignore')


def convert_gestational_week(week_str):
    """将孕周转换为数值（处理如'13w+4'的格式）"""
    try:
        if pd.isna(week_str):
            return np.nan

        week_str = str(week_str).strip()

        # 1. 处理 '13w+4' 格式
        if 'w' in week_str.lower():
            week_str = week_str.replace(' ', '')
            if '+' in week_str:
                week_part, day_part = week_str.split('+')
                weeks = float(week_part.lower().replace('w', ''))
                days = float(day_part)
                return weeks + days / 7
            else:
                weeks = float(week_str.lower().replace('w', ''))
                return weeks

        # 2. 处理传统格式 '12+3'
        elif '+' in week_str:
            parts = week_str.split('+')
            if len(parts) == 2:
                weeks = float(parts[0])
                days = float(parts[1])
                return weeks + days / 7

        # 3. 如果是纯数字
        try:
            return float(week_str)
        except:
            numbers = re.findall(r'\d+\.?\d*', week_str)
            if numbers:
                if len(numbers) >= 2:
                    weeks = float(numbers[0])
                    days = float(numbers[1])
                    return weeks + days / 7
                else:
                    return float(numbers[0])

            return np.nan

    except Exception as e:
        return np.nan


def standardize_column_names(df, sheet_name=""):
    """标准化列名，解决重复列名问题"""
    df = df.copy()

    # 检查是否有重复列名
    col_counts = Counter(df.columns)
    duplicate_cols = [col for col, count in col_counts.items() if count > 1]

    if duplicate_cols:
        print(f"  发现重复列名: {duplicate_cols}")
        # 重命名重复列
        new_columns = []
        seen = {}
        for col in df.columns:
            if col in seen:
                seen[col] += 1
                new_name = f"{col}_{seen[col]}"
                new_columns.append(new_name)
            else:
                seen[col] = 1
                new_columns.append(col)
        df.columns = new_columns

    # 标准化列名：移除空格、特殊字符
    df.columns = [str(col).strip().replace(' ', '_').replace('(', '').replace(')', '')
                  for col in df.columns]

    return df


def preprocess_single_sheet(df, sheet_name="未命名工作表"):
    """预处理单个工作表"""
    print(f"\n{'=' * 50}")
    print(f"处理工作表: {sheet_name}")
    print(f"{'=' * 50}")

    # 标准化列名
    df = standardize_column_names(df, sheet_name)

    df_processed = df.copy()

    # 打印列信息
    print(f"数据形状: {df_processed.shape[0]}行 × {df_processed.shape[1]}列")
    print(f"列名示例: {list(df_processed.columns[:10])}")
    if len(df_processed.columns) > 10:
        print(f"          ... 还有 {len(df_processed.columns) - 10} 列")

    # 根据索引映射关键列
    column_mapping = {}

    # 定义关键列的索引映射
    key_columns = {
        0: '序号',
        1: '孕妇代码',
        2: '年龄',
        3: '身高',
        4: '体重',
        5: '未次月经时间',
        6: 'IVF妊娠方式',
        7: '检测时间',
        8: '检测抽血次数',
        9: '孕周',
        10: 'BMI',
        21: 'Y染色体浓度',
        22: 'X染色体浓度',
    }

    # 应用映射
    applied_mappings = {}
    for idx, name in key_columns.items():
        if idx < len(df_processed.columns):
            original_name = df_processed.columns[idx]
            if original_name != name:
                column_mapping[original_name] = name
                applied_mappings[name] = original_name

    if column_mapping:
        print(f"\n重命名 {len(column_mapping)} 个关键列:")
        for new_name, old_name in column_mapping.items():
            print(f"  {old_name} -> {new_name}")

        # 重命名列
        df_processed.rename(columns=column_mapping, inplace=True)

    # 转换孕周数据
    if '孕周' in df_processed.columns:
        # 查看样本数据
        sample_values = df_processed['孕周'].dropna().unique()[:3]
        print(f"孕周样本值: {sample_values}")

        # 转换孕周
        df_processed['孕周数值'] = df_processed['孕周'].apply(convert_gestational_week)

        valid_count = df_processed['孕周数值'].notna().sum()
        print(f"孕周转换: {valid_count}/{len(df_processed)} 行有效")

        if valid_count > 0:
            min_week = df_processed['孕周数值'].min()
            max_week = df_processed['孕周数值'].max()
            print(f"孕周范围: {min_week:.1f} - {max_week:.1f} 周")
    else:
        print("未找到'孕周'列")
        df_processed['孕周数值'] = np.nan

    # 处理Y染色体浓度
    if 'Y染色体浓度' in df_processed.columns:
        df_processed['Y染色体浓度'] = pd.to_numeric(df_processed['Y染色体浓度'], errors='coerce')

        # 分离数据
        df_male = df_processed[df_processed['Y染色体浓度'] > 0].copy()
        df_female = df_processed[df_processed['Y染色体浓度'] == 0].copy()

        print(f"\n数据分离:")
        print(f"  男胎: {len(df_male)} 行")
        print(f"  女胎: {len(df_female)} 行")

        if len(df_male) > 0:
            df_male['达标标志'] = (df_male['Y染色体浓度'] >= 0.04).astype(int)
            达标比例 = df_male['达标标志'].mean()
            print(f"  男胎达标比例: {达标比例:.2%}")

        return df_processed, df_male, df_female
    else:
        print("未找到'Y染色体浓度'列")
        return df_processed, pd.DataFrame(), pd.DataFrame()


def align_dataframes(df_list):
    """对齐多个DataFrame的列结构"""
    if not df_list:
        return pd.DataFrame()

    # 获取所有列名的并集
    all_columns = set()
    for df in df_list:
        all_columns.update(df.columns)

    all_columns = sorted(list(all_columns))
    print(f"所有列名的并集: {len(all_columns)} 列")

    # 对齐每个DataFrame
    aligned_dfs = []
    for i, df in enumerate(df_list):
        # 添加缺失的列
        for col in all_columns:
            if col not in df.columns:
                df[col] = np.nan

        # 按统一顺序排列列
        df = df[all_columns]
        aligned_dfs.append(df)

    return aligned_dfs


def load_and_preprocess_all_sheets(file_path):
    """加载并预处理所有工作表"""
    print(f"{'=' * 60}")
    print(f"开始处理文件: {file_path}")
    print(f"{'=' * 60}")

    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件不存在 - {file_path}")
        # 尝试在当前目录下查找
        current_dir = os.getcwd()
        files = [f for f in os.listdir(current_dir) if f.endswith(('.xlsx', '.xls', '.csv'))]
        if files:
            print(f"当前目录下的数据文件: {files}")
        return None

    try:
        # 读取Excel文件
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"找到 {len(sheet_names)} 个工作表: {sheet_names}")

        # 读取所有工作表
        all_sheets = {}
        for sheet_name in sheet_names:
            print(f"\n读取工作表: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"  原始形状: {df.shape[0]}行 × {df.shape[1]}列")
            all_sheets[sheet_name] = df

    except Exception as e:
        print(f"读取Excel文件时出错: {e}")
        # 尝试作为CSV读取
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            all_sheets = {'CSV数据': df}
        else:
            print("无法读取文件，请检查文件格式")
            return None

    # 处理每个工作表
    processed_sheets = {}
    male_sheets = {}
    female_sheets = {}

    all_male_data = []
    all_female_data = []

    for sheet_name, df in all_sheets.items():
        df_proc, df_male, df_female = preprocess_single_sheet(df, sheet_name)

        # 保存各个工作表的结果
        processed_sheets[sheet_name] = df_proc
        male_sheets[sheet_name] = df_male
        female_sheets[sheet_name] = df_female

        # 收集数据用于合并
        if len(df_male) > 0:
            df_male['来源工作表'] = sheet_name
            all_male_data.append(df_male)

        if len(df_female) > 0:
            df_female['来源工作表'] = sheet_name
            all_female_data.append(df_female)

    print(f"\n{'=' * 60}")
    print("合并所有工作表数据")
    print(f"{'=' * 60}")

    # 对齐并合并数据
    if processed_sheets:
        # 对齐列结构
        aligned_processed = align_dataframes(list(processed_sheets.values()))
        if aligned_processed:
            all_processed = pd.concat(aligned_processed, ignore_index=True)
            print(f"合并后总数据: {len(all_processed)} 行")
        else:
            all_processed = pd.DataFrame()
            print("无处理后的数据")
    else:
        all_processed = pd.DataFrame()
        print("无处理后的数据")

    # 合并男胎数据
    if all_male_data:
        aligned_male = align_dataframes(all_male_data)
        if aligned_male:
            all_male = pd.concat(aligned_male, ignore_index=True)
            print(f"合并后男胎数据: {len(all_male)} 行")
        else:
            all_male = pd.DataFrame()
            print("无男胎数据")
    else:
        all_male = pd.DataFrame()
        print("无男胎数据")

    # 合并女胎数据
    if all_female_data:
        aligned_female = align_dataframes(all_female_data)
        if aligned_female:
            all_female = pd.concat(aligned_female, ignore_index=True)
            print(f"合并后女胎数据: {len(all_female)} 行")
        else:
            all_female = pd.DataFrame()
            print("无女胎数据")
    else:
        all_female = pd.DataFrame()
        print("无女胎数据")

    # 保存结果
    print(f"\n{'=' * 60}")
    print("保存处理结果")
    print(f"{'=' * 60}")

    output_file = '处理后数据.xlsx'

    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 保存每个工作表的原始处理数据
            for sheet_name, df_proc in processed_sheets.items():
                safe_sheet_name = str(sheet_name)[:31]
                df_proc.to_excel(writer, sheet_name=f'{safe_sheet_name}_处理后', index=False)
                print(f"  已保存: {safe_sheet_name}_处理后 ({len(df_proc)}行)")

            # 保存合并数据
            if len(all_processed) > 0:
                all_processed.to_excel(writer, sheet_name='全部数据_合并', index=False)
                print(f"  已保存: 全部数据_合并 ({len(all_processed)}行)")

            if len(all_male) > 0:
                all_male.to_excel(writer, sheet_name='男胎数据_合并', index=False)
                print(f"  已保存: 男胎数据_合并 ({len(all_male)}行)")

            if len(all_female) > 0:
                all_female.to_excel(writer, sheet_name='女胎数据_合并', index=False)
                print(f"  已保存: 女胎数据_合并 ({len(all_female)}行)")

        print(f"\n✓ 所有数据已保存到: {output_file}")

    except Exception as e:
        print(f"保存文件时出错: {e}")
        # 尝试保存为多个CSV文件
        print("尝试保存为CSV文件...")

        if len(all_processed) > 0:
            all_processed.to_csv('全部数据_合并.csv', index=False, encoding='utf-8-sig')
            print("  已保存: 全部数据_合并.csv")

        if len(all_male) > 0:
            all_male.to_csv('男胎数据_合并.csv', index=False, encoding='utf-8-sig')
            print("  已保存: 男胎数据_合并.csv")

        if len(all_female) > 0:
            all_female.to_csv('女胎数据_合并.csv', index=False, encoding='utf-8-sig')
            print("  已保存: 女胎数据_合并.csv")

        output_file = 'CSV文件'

    return {
        'all_processed': all_processed,
        'all_male': all_male,
        'all_female': all_female,
        'by_sheet': {
            'processed': processed_sheets,
            'male': male_sheets,
            'female': female_sheets
        }
    }


def main():
    """主函数"""
    # 获取文件路径
    import sys

    # 如果有命令行参数，使用第一个参数作为文件路径
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 查找当前目录下的数据文件
        current_dir = os.getcwd()
        data_files = []

        for file in os.listdir(current_dir):
            if file.lower().endswith(('.xlsx', '.xls', '.csv')):
                # 排除临时文件
                if not file.startswith('~$') and not file.startswith('.'):
                    data_files.append(file)

        if data_files:
            print("找到以下数据文件:")
            for i, file in enumerate(data_files, 1):
                print(f"{i}. {file}")

            if len(data_files) == 1:
                file_path = data_files[0]
            else:
                try:
                    choice = int(input("\n请选择文件编号: "))
                    if 1 <= choice <= len(data_files):
                        file_path = data_files[choice - 1]
                    else:
                        file_path = data_files[0]
                except:
                    file_path = data_files[0]
        else:
            print("当前目录下未找到数据文件")
            print("请将数据文件放在当前目录下，或使用命令行参数指定路径")
            print("用法: python script.py 文件路径")
            return

    # 处理数据
    result = load_and_preprocess_all_sheets(file_path)

    if result:
        # 显示总结信息
        print(f"\n{'=' * 60}")
        print("处理完成总结")
        print(f"{'=' * 60}")

        all_processed = result['all_processed']
        all_male = result['all_male']
        all_female = result['all_female']

        print(f"总数据行数: {len(all_processed)}")
        print(f"男胎数据行数: {len(all_male)}")
        print(f"女胎数据行数: {len(all_female)}")

        if len(all_male) > 0:
            print(f"\n男胎数据统计:")
            print(f"  达标比例: {all_male['达标标志'].mean():.2%}")

            if '孕周数值' in all_male.columns:
                print(f"  平均孕周: {all_male['孕周数值'].mean():.1f}周")
                print(f"  孕周范围: {all_male['孕周数值'].min():.1f} - {all_male['孕周数值'].max():.1f}周")

        # 显示列结构
        if len(all_processed) > 0:
            print(f"\n数据列结构 ({len(all_processed.columns)}列):")
            # 只显示前15列
            for i, col in enumerate(all_processed.columns[:15]):
                print(f"  {i + 1:2d}. {col}")
            if len(all_processed.columns) > 15:
                print(f"  ... 还有 {len(all_processed.columns) - 15} 列")


if __name__ == "__main__":
    main()