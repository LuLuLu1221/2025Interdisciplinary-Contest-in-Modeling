import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import os

# ==========================================
# 1. Data Loading with Absolute Paths (读取数据)
# ==========================================
# 获取当前目录下文件的绝对路径
# 注意：如果您在本地运行，请确保这些文件在您的当前工作目录中，或者修改为您本地的实际绝对路径
abs_path_avg = os.path.abspath('全联盟场均.xlsx - Worksheet.csv')
abs_path_adv = os.path.abspath('全联盟球队高阶数据.xlsx - Worksheet.csv')

print(f"Loading data from:\n1. {abs_path_avg}\n2. {abs_path_adv}")

# 读取文件
# 注意：高阶数据表的表头在第2行 (header=1)
df_avg = pd.read_csv(abs_path_avg)
df_adv = pd.read_csv(abs_path_adv, header=1)

# 数据清洗：去除 "League Average" 行，确保只包含30支球队的真实数据
df_adv = df_adv[df_adv['Team'] != 'League Average']
df_avg = df_avg[df_avg['Team'] != 'League Average']

# 合并数据：基于 'Team' 列
df_merged = pd.merge(df_avg, df_adv, on='Team', how='inner', suffixes=('_avg', '_adv'))

# ==========================================
# 2. Define PD-RAD Metrics (定义评估维度 - 英文)
# ==========================================
# 格式: (显示标签, 列名, 方向: 1=越高越好, -1=越低越好)
metrics_config = [
    ('OFF RATING\n(Efficiency)', 'ORtg', 1),  # 进攻效率
    ('TRUE SHOOTING\n(Shot Quality)', 'TS%', 1),  # 真实命中率
    ('SPACING\n(3P%)', '3P%', 1),  # 三分命中率
    ('PLAYMAKING\n(AST)', 'AST', 1),  # 助攻
    ('BALL SECURITY\n(Low TOV%)', 'TOV%', -1),  # 失误率 (越低越好)
    ('DEF RATING\n(Stops/100)', 'DRtg', -1),  # 防守效率 (越低越好)
    ('RIM PROTECT\n(BLK)', 'BLK', 1),  # 盖帽
    ('REBOUNDING\n(TRB)', 'TRB', 1)  # 篮板
]

# 确保所有涉及的列都是数值型
for _, col, _ in metrics_config:
    df_merged[col] = pd.to_numeric(df_merged[col], errors='coerce')

# ==========================================
# 3. Calculate Real Z-Scores (计算真实标准分)
# ==========================================
# 提取湖人队数据
lakers_row = df_merged[df_merged['Team'] == 'Los Angeles Lakers'].iloc[0]

values = []  # 用于绘图的 Z-Score
raw_values = []  # 用于显示的原始数值
labels = []  # 轴标签

for label, col, direction in metrics_config:
    # 实时计算全联盟的均值 (mu) 和 标准差 (sigma)
    mu = df_merged[col].mean()
    sigma = df_merged[col].std()

    val = lakers_row[col]

    # Z-Score 公式: 方向 * (数值 - 均值) / 标准差
    z = direction * (val - mu) / sigma

    values.append(z)
    raw_values.append(val)
    labels.append(label)

# ==========================================
# 4. Plotting the PD-RAD Octagon (绘制雷达图)
# ==========================================
# 数据闭环
values_plot = values + [values[0]]
N = len(labels)
angles = [n / float(N) * 2 * pi for n in range(N)]
angles += angles[:1]

# 设置画布
fig = plt.figure(figsize=(12, 12), dpi=150, facecolor='white')
ax = plt.subplot(111, polar=True)

# 设置起始角度 (正上方)
ax.set_theta_offset(pi / 2)
ax.set_theta_direction(-1)

# 绘制轴标签 (粗体，深灰色)
plt.xticks(angles[:-1], labels, size=10, fontweight='bold', color='#333333')

# 设置Y轴刻度和网格
plt.ylim(-2.5, 2.5)
ax.set_rlabel_position(0)
# 添加自定义刻度标签
plt.yticks([-2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0],
           ["-2.0", "", "CRITICAL GAP", "", "AVG", "", "ELITE", "", "+2.0"],
           color="grey", size=8, fontweight='bold')
ax.grid(True, color='#E0E0E0', linestyle='-', linewidth=0.8)

# --- 绘制主数据 (湖人紫) ---
ax.plot(angles, values_plot, linewidth=3, linestyle='solid', color='#552583', label='Lakers 2026 (Real Data)')
ax.fill(angles, values_plot, '#552583', alpha=0.35)

# --- 绘制阈值线 ---
# 1. 联盟平均线 (0.0)
ax.plot(angles, [0] * len(angles), linewidth=1.2, linestyle='--', color='#555555', label='League Average (0.0)')

# 2. 致命缺陷线 (-1.0) - 红色高亮区域
ax.fill_between(angles, -2.5, -1.0, color='#D40000', alpha=0.1)  # 红色背景区
ax.plot(angles, [-1.0] * len(angles), linewidth=2, linestyle='--', color='#D40000',
        label='Critical Gap Threshold (-1.0)')

# 3. 精英线 (+1.0) - 金色
ax.plot(angles, [1.0] * len(angles), linewidth=1.5, linestyle='--', color='#FDB927', label='Elite Threshold (+1.0)')

# --- 添加数据标签 ---
for angle, z, val, config in zip(angles[:-1], values, raw_values, metrics_config):
    col = config[1]
    # 格式化数值
    if col in ['TS%', '3P%', 'TOV%']:
        val_str = f"{val * 100:.1f}%"
    else:
        val_str = f"{val:.1f}"

    # 动态样式
    text_color = 'white'
    # 正数为紫色背景，负数为红色背景
    bbox_color = '#552583' if z >= 0 else '#D40000'

    # 添加带背景框的标签
    ax.text(angle, z + (0.5 if z >= 0 else -0.6), f"{val_str}\n(Z={z:.1f})",
            ha='center', va='center', fontsize=9, fontweight='bold', color=text_color,
            bbox=dict(facecolor=bbox_color, alpha=0.8, edgecolor='none', boxstyle='round,pad=0.3'))

# 标题与图例
plt.title('Lakers Team DNA: PD-RAD Octagon Diagnosis\n(Based on 2026 Real League Data)',
          size=18, color='#552583', y=1.08, fontweight='bold')

legend = plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), frameon=True, facecolor='white', framealpha=1)
plt.setp(legend.get_texts(), fontweight='bold')

plt.tight_layout()
# 保存高清图片
plt.savefig('Lakers_PD_RAD_Octagon_Pro_AbsPath.png', bbox_inches='tight', dpi=200)
plt.show()

# 打印简报表
print("--- PD-RAD DIAGNOSIS SUMMARY (Real Data Z-Scores) ---")
summary_df = pd.DataFrame({
    'Metric': [x[0].replace('\n', ' ') for x in metrics_config],
    'Raw Value': raw_values,
    'Z-Score': values
})
summary_df['Status'] = summary_df['Z-Score'].apply(
    lambda x: 'CRITICAL GAP' if x <= -1.0 else ('ELITE' if x >= 1.0 else 'AVERAGE'))
print(summary_df.round(3).to_markdown(index=False))