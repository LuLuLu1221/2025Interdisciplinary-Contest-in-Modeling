import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# 1. 数据准备
data = {
    'Player': ['Doncic', 'LeBron', 'Reaves', 'Bronny', 'Hachimura',
               'Ayton', 'Smart', 'Vanderbilt', 'Knecht', 'Vincent',
               'Hayes', 'Kleber', 'LaRavia', 'Smith', 'Thiero', 'Manon'],
    'V_on': [7.41, 4.65, 6.16, 3.39, 4.34, 5.34, 4.11, 4.44, 3.65, 3.43, 4.26, 3.07, 4.65, 3.69, 3.39, 3.18],
    'V_off': [8.98, 9.18, 6.57, 8.76, 6.78, 4.92, 5.13, 4.44, 3.23, 3.29, 2.51, 3.19, 1.53, 1.56, 0.66, 0.00]
}

df = pd.DataFrame(data)

# 2. 计算总价值
w_on = 0.45
w_off = 0.55
df['V_total'] = df['V_on'] * w_on + df['V_off'] * w_off

# 3. 设置绘图风格
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.weight'] = 'bold'

# 4. 创建图表
fig, ax = plt.subplots(figsize=(14, 10), dpi=150)
ax.set_facecolor('#F9F9F9')

# 绘制辅助线
mean_on = df['V_on'].mean()
mean_off = df['V_off'].mean()
ax.axvline(x=mean_on, color='gray', linestyle='--', alpha=0.6, zorder=1)
ax.axhline(y=mean_off, color='gray', linestyle='--', alpha=0.6, zorder=1)

# 绘制散点 (zorder=5, 位于文字下方)
sizes = (df['V_total'] ** 2.3) * 12
scatter = ax.scatter(df['V_on'], df['V_off'],
                     s=sizes,
                     c=df['V_total'],
                     cmap=sns.light_palette(LAKERS_PURPLE, as_cmap=True),
                     edgecolors=LAKERS_GOLD,
                     linewidth=2.5,
                     alpha=0.9,
                     zorder=5)

# 5. 添加标签 (严格居中对齐圆心)
for i, row in df.iterrows():
    # ha='center', va='center' 确保文字中心与坐标点(row['V_on'], row['V_off'])重合
    # zorder=10 确保文字在气泡之上
    ax.text(row['V_on'], row['V_off'],
            f"{row['Player']}\n{row['V_total']:.2f}",
            ha='center', va='center',
            fontsize=5, fontweight='bold', color='black',
            zorder=10)

# 6. 象限说明 (固定在四角)
ax.text(0.99, 0.99, 'SUPERSTAR\n(High On / High Off)',
        transform=ax.transAxes, ha='right', va='top',
        fontsize=14, fontweight='bold', color=LAKERS_PURPLE, alpha=0.5, zorder=1)

ax.text(0.01, 0.99, 'COMMERCIAL ASSET\n(Low On / High Off)',
        transform=ax.transAxes, ha='left', va='top',
        fontsize=14, fontweight='bold', color=LAKERS_GOLD, alpha=1.0, zorder=1)

ax.text(0.99, 0.01, 'ROTATION\n(High On / Low Off)',
        transform=ax.transAxes, ha='right', va='bottom',
        fontsize=14, fontweight='bold', color='gray', alpha=0.6, zorder=1)

ax.text(0.01, 0.01, 'DEVELOPMENTAL\n(Low On / Low Off)',
        transform=ax.transAxes, ha='left', va='bottom',
        fontsize=14, fontweight='bold', color='gray', alpha=0.6, zorder=1)

# 标题和坐标轴
plt.title('NBA Player Value Matrix (Lakers Model)',
          fontsize=20, fontweight='bold', color=LAKERS_PURPLE, pad=20)
plt.xlabel(f'Athletic Value ($V_{{on}}$) - Weight {w_on}', fontsize=12, fontweight='bold')
plt.ylabel(f'Commercial Value ($V_{{off}}$) - Weight {w_off}', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('Lakers_Player_Value_Centered.png', bbox_inches='tight')
plt.show()