import pandas as pd
import numpy as np
import io
import matplotlib.pyplot as plt
import seaborn as sns


# ==========================================
# 1. 设置湖人队配色主题
# ==========================================
def set_lakers_theme():
    """设置 matplotlib/seaborn 为湖人队紫金配色主题"""
    # 湖人队核心颜色代码
    lakers_purple = '#552583'  # 湖人紫
    lakers_gold = '#FDB927'  # 湖人金/黄
    lakers_black = '#000000'  # 辅助黑
    lakers_white = '#FFFFFF'  # 辅助白

    # 设置基础风格
    sns.set_theme(style="whitegrid")

    # 自定义颜色循环 (用于多类别绘图)
    # 首选紫色和金色，第三色用黑色
    custom_palette = [lakers_purple, lakers_gold, lakers_black, '#9e7ec9', '#ffe082']
    sns.set_palette(custom_palette)

    # 自定义 matplotlib 参数以匹配主题
    plt.rcParams.update({
        'figure.facecolor': lakers_white,
        'axes.facecolor': lakers_white,
        'axes.edgecolor': lakers_purple,
        'axes.labelcolor': lakers_purple,
        'axes.titlecolor': lakers_purple,
        'xtick.color': lakers_purple,
        'ytick.color': lakers_purple,
        'grid.color': '#e0e0e0',  # 浅灰色网格，不抢戏
        'text.color': lakers_black,
        'font.weight': 'bold',
        'axes.titleweight': 'bold',
        'axes.labelweight': 'bold',
    })
    return lakers_purple, lakers_gold


# 应用主题并获取主色调变量
PURPLE, GOLD = set_lakers_theme()

# ==========================================
# 2. 数据加载与预处理 (保持原样，稍作整理)
# ==========================================
try:
    # 尝试读取本地 CSV 文件
    df = pd.read_csv('raw_data.csv')
    print("成功读取本地 raw_data.csv 文件。")
except FileNotFoundError:
    print("未找到本地 raw_data.csv 文件，使用内置示例数据。")
    # 内置示例数据 (为了确保代码可以直接运行)
    csv_data = """
id,isco08_1r,sex_dic,age_dic,edu_dic,income
1,1,1,2,3,50000
2,1,1,2,3,52000
3,1,2,1,2,48000
4,1,2,3,4,60000
5,2,1,2,3,40000
6,2,1,1,2,35000
7,2,2,3,4,45000
8,2,2,2,3,42000
9,3,1,2,2,30000
10,3,1,1,1,25000
11,3,2,3,3,35000
12,3,2,2,2,32000
13,1,1,2,3,51000
14,1,2,3,4,62000
15,2,1,1,2,36000
16,3,2,2,2,33000
17,9,1,1,1,15000
18,9,2,2,2,18000
19,9,1,3,1,16000
20,9,2,1,2,17000
"""
    csv_file = io.StringIO(csv_data)
    df = pd.read_csv(csv_file)

# 清理列名，移除可能的空格
df.columns = df.columns.str.strip()

# 填充缺失值
categorical_cols = ['isco08_1r', 'sex_dic', 'age_dic', 'edu_dic']
for col in categorical_cols:
    if col in df.columns:
        df[col] = df[col].fillna('Unknown')

if 'income' in df.columns:
    df['income'] = df['income'].fillna(0)

# 筛选需要的列
required_cols = ['isco08_1r', 'sex_dic', 'age_dic', 'edu_dic', 'income']
plot_data = df[required_cols].copy()

# 确保收入列是数值型
plot_data['income'] = pd.to_numeric(plot_data['income'], errors='coerce').fillna(0)

# 移除收入为0或负数的行（Theil指数计算需要正收入）
plot_data = plot_data[plot_data['income'] > 0].copy()

print(f"预处理完成，用于分析的数据行数: {len(plot_data)}")
print("-" * 30)


# ==========================================
# 3. 定义指标计算函数 (保持原样)
# ==========================================
def calculate_theil_t(incomes):
    """计算 Theil T 指数 (GE(1))"""
    incomes = np.array(incomes)
    n = len(incomes)
    if n == 0: return 0
    mean_income = np.mean(incomes)
    if mean_income == 0: return 0
    # 避免对数中的零或负值
    incomes = incomes[incomes > 0]
    n = len(incomes)
    if n == 0: return 0

    term = (incomes / mean_income) * np.log(incomes / mean_income)
    theil_t = np.sum(term) / n
    return theil_t


def calculate_theil_l(incomes):
    """计算 Theil L 指数 (GE(0), 平均对数偏差)"""
    incomes = np.array(incomes)
    # 避免对数中的零或负值
    incomes = incomes[incomes > 0]
    n = len(incomes)
    if n == 0: return 0
    mean_income = np.mean(incomes)
    if mean_income == 0: return 0

    term = np.log(mean_income / incomes)
    theil_l = np.sum(term) / n
    return theil_l


def calculate_entropy(labels):
    """计算香农熵 (Shannon Entropy)"""
    labels = np.array(labels)
    n = len(labels)
    if n == 0: return 0

    # 计算每个类别的概率
    _, counts = np.unique(labels, return_counts=True)
    probs = counts / n

    # 计算熵，使用以2为底的对数 (单位: bits)
    # 避免概率为0的情况
    probs = probs[probs > 0]
    entropy = -np.sum(probs * np.log2(probs))
    return entropy


def calculate_between_within_theil_t(df, group_col, income_col='income'):
    """分解 Theil T 为组间 (Between) 和组内 (Within) 部分"""
    overall_mean = df[income_col].mean()
    if overall_mean == 0: return 0, 0
    N = len(df)

    groups = df.groupby(group_col)

    between_group_t = 0
    within_group_t_weighted = 0

    for name, group_df in groups:
        n_k = len(group_df)
        mean_k = group_df[income_col].mean()
        income_share_k = group_df[income_col].sum() / df[income_col].sum()

        # 组间部分计算
        if mean_k > 0:
            between_group_t += (n_k / N) * (mean_k / overall_mean) * np.log(mean_k / overall_mean)

        # 组内部分计算
        theil_k = calculate_theil_t(group_df[income_col])
        within_group_t_weighted += income_share_k * theil_k

    return between_group_t, within_group_t_weighted


# ==========================================
# 4. 主计算循环与数据收集 (核心修改部分)
# ==========================================
# 按职业大类 (isco08_1r) 分组
plot_data_grouped = plot_data.groupby('isco08_1r')

# 用于存储绘图数据的列表
plot_results = []

print("开始计算各职业类别的指标...\n")

for name, group in plot_data_grouped:
    # 1. 计算整体指标
    incomes = group['income']
    theil_t_val = calculate_theil_t(incomes)
    theil_l_val = calculate_theil_l(incomes)

    # 计算多样性熵 (这里以 edu_dic 为例，代表教育背景的多样性)
    entropy_val = calculate_entropy(group['edu_dic'])

    # 2. 计算分解指标 (组间 Theil T)
    # 性别
    theil_t_between_sex, _ = calculate_between_within_theil_t(group, 'sex_dic')
    # 年龄
    theil_t_between_age, _ = calculate_between_within_theil_t(group, 'age_dic')
    # 教育
    theil_t_between_edu, _ = calculate_between_within_theil_t(group, 'edu_dic')

    # 收集数据用于绘图
    plot_results.append({
        'Occupation': str(name),  # 确保职业代码是字符串
        'Theil T (Overall)': theil_t_val,
        'Theil L (Overall)': theil_l_val,
        'Entropy (Education)': entropy_val,
        'Between-Group (Sex)': theil_t_between_sex,
        'Between-Group (Age)': theil_t_between_age,
        'Between-Group (Edu)': theil_t_between_edu
    })

    # 打印文本结果 (保留原有功能)
    print(f"=== 职业类别: {name} (样本数: {len(group)}) ===")
    print(f"  总体 Income Theil T: {theil_t_val:.4f}")
    print(f"  总体 Income Theil L: {theil_l_val:.4f}")
    print(f"  教育多样性 Entropy: {entropy_val:.4f}")
    print("-" * 20)
    print(f"  [性别分解] Between: {theil_t_between_sex:.4f}")
    print(f"  [年龄分解] Between: {theil_t_between_age:.4f}")
    print(f"  [教育分解] Between: {theil_t_between_edu:.4f}")
    print("\n")

# 将结果列表转换为 DataFrame
results_df = pd.DataFrame(plot_results)

# ==========================================
# 5. 数据可视化 (新增部分)
# ==========================================

if not results_df.empty:
    # --- 图表 1: 整体不平等与多样性指标对比 ---
    plt.figure(figsize=(12, 6))

    # 将数据转换为长格式以便于 seaborn 分组绘图
    melted_overall = results_df.melt(
        id_vars=['Occupation'],
        value_vars=['Theil T (Overall)', 'Theil L (Overall)', 'Entropy (Education)'],
        var_name='Metric',
        value_name='Value'
    )

    # 创建柱状图
    # 使用自定义的湖人配色盘：紫、金、黑
    ax1 = sns.barplot(
        data=melted_overall,
        x='Occupation',
        y='Value',
        hue='Metric',
        palette=[PURPLE, GOLD, '#333333']
    )

    plt.title('LAKERS ANALYTICS: Inequality & Diversity Metrics by Occupation', fontsize=14, color=PURPLE)
    plt.ylabel('Metric Value')
    plt.xlabel('Occupation Category (ISCO-08)')
    plt.xticks(rotation=0)  # 如果类别太多，可以改为 45
    plt.legend(title='Metrics')
    plt.tight_layout()
    print("正在显示图表 1...")
    plt.show()

    # --- 图表 2: 组间不平等贡献因素分析 (Between-Group Theil T) ---
    plt.figure(figsize=(12, 6))

    # 将数据转换为长格式
    melted_between = results_df.melt(
        id_vars=['Occupation'],
        value_vars=['Between-Group (Sex)', 'Between-Group (Age)', 'Between-Group (Edu)'],
        var_name='Driver',
        value_name='Theil T Contribution'
    )

    # 创建柱状图
    # 使用自定义配色：紫、金、浅紫
    ax2 = sns.barplot(
        data=melted_between,
        x='Occupation',
        y='Theil T Contribution',
        hue='Driver',
        palette=[PURPLE, GOLD, '#9E7EC9']
    )

    plt.title('LAKERS ANALYTICS: Drivers of Between-Group Inequality', fontsize=14, color=PURPLE)
    plt.ylabel('Between-Group Theil T Contribution')
    plt.xlabel('Occupation Category (ISCO-08)')
    plt.xticks(rotation=0)
    plt.legend(title='Demographic Driver')
    plt.tight_layout()
    print("正在显示图表 2...")
    plt.show()

else:
    print("没有足够的数据生成图表。")

print("\n分析与绘图完成。Go Lakers!")