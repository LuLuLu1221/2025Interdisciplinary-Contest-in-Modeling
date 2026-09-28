import matplotlib.pyplot as plt
import numpy as np

# ==========================================
# 1. 模型参数计算 (基于 PDF 公式与湖人数据)
# ==========================================
# 竞技参数
T_perf = 24.94
Wins = 47.3
N_stars = 3
Jersey_Index = 9.5

# PDF 模型系数
alpha = 18.2
theta = 192.0
m = 18.15

# 计算各组件 (单位: Million USD)
# R_total_comp = alpha * ln(1 + T_perf)
r_comp = alpha * np.log(1 + T_perf)
# R_total_star (基于之前分析的球星总分加权)
r_star = 350.9
# Ecosystem (Fixed Media)
r_ecosystem = theta
# R_playoff = 5 * max(0, Wins - 42) + 20 (assume 1 round)
r_playoff = 5 * (Wins - 42) + 20

# 总年营收
total_revenue = r_comp + r_star + r_ecosystem + r_playoff

# 倍数效应 (m-1) * Total_Revenue (单位转为Billion)
multiplier_effect = (m - 1) * total_revenue / 1000

# Brand Premium (单位转为Billion)
# P_brand = 500 + 50*N_stars + 10*Jersey_Index
p_brand = (500 + 50 * N_stars + 10 * Jersey_Index) / 1000

# 基础营收转换 (Million to Billion)
base_rev_b = total_revenue / 1000

# ==========================================
# 2. 准备瀑布图数据
# ==========================================
labels = [
    'Competitive Rev',
    'Ecosystem Rev',
    'Star Influence',
    'Playoff Bonus',
    'Market Multiplier',
    'Brand Premium',
    'TOTAL VALUE'
]

# 每个阶段的增量 (Billion USD)
changes = [
    r_comp / 1000,
    r_ecosystem / 1000,
    r_star / 1000,
    r_playoff / 1000,
    multiplier_effect,
    p_brand
]

# 计算累计值
values = np.cumsum(changes)
total_val = values[-1]

# ==========================================
# 3. 绘图 (湖人配色 + 白底)
# ==========================================
purple = '#552583'
gold = '#FDB927'

fig, ax = plt.subplots(figsize=(12, 8), facecolor='white')

# 绘制柱状图
for i in range(len(changes)):
    bottom = values[i - 1] if i > 0 else 0
    color = purple if i < 4 else (gold if i < 6 else purple)
    ax.bar(labels[i], changes[i], bottom=bottom, color=color, edgecolor='black', alpha=0.9)

    # 标注增量
    ax.text(i, bottom + changes[i] / 2, f'+${changes[i]:.2f}B',
            ha='center', va='center', color='white' if i != 5 else 'black', fontweight='bold')

# 绘制最终总计柱
ax.bar(labels[-1], total_val, color=purple, edgecolor=gold, linewidth=2)
ax.text(6, total_val / 2, f'${total_val:.2f}B', ha='center', va='center', color='white', fontsize=14, fontweight='bold')

# 辅助线
for i in range(len(changes)):
    ax.plot([i, i + 1], [values[i], values[i]], color='gray', linestyle='--', linewidth=1, alpha=0.5)

# 样式美化
ax.set_facecolor('white')
ax.set_ylabel('Franchise Value ($ Billion)', fontsize=12, fontweight='bold')
ax.set_title('Lakers Franchise Valuation Waterfall (Based on Comprehensive Model)',
             fontsize=16, fontweight='bold', color=purple, pad=20)
ax.grid(axis='y', linestyle=':', alpha=0.7)
plt.xticks(rotation=15, fontweight='bold')

plt.tight_layout()
plt.savefig('Valuation_Waterfall.png', dpi=150)
plt.show()