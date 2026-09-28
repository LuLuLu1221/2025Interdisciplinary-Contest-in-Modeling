import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 数据准备 (融合最新竞技排名 + 原商业价值评分)
# ==========================================
# 最新竞技价值数据 (从你的Complete Player Ranking提取，Von为竞技核心分，统一球员名)
on_court_data = {
    'Player': ['Donkic', 'Reaves', 'Ayton', 'Hayes', 'LaRavia', 'Manon',
               'Vanderbilt', 'Knecht', 'Hachimura', 'Timme', 'Smart', 'James',
               'Thiero', 'JrSmith', 'Bronny', 'Vincent', 'Kleber'],
    'V_on_Score': [6.544, 5.541, 5.026, 4.817, 4.552, 4.446,
                   4.110, 4.047, 3.997, 3.961, 3.844, 3.833,
                   3.832, 3.784, 3.678, 3.586, 3.132]
}

# 原商业价值数据 (保留你提供的评分，对齐球员名，补充匹配最新竞技名单)
commercial_data = {
    'Player': ['Donkic', 'Reaves', 'Ayton', 'Hayes', 'LaRavia', 'Manon',
               'Vanderbilt', 'Knecht', 'Hachimura', 'Timme', 'Smart', 'James',
               'Thiero', 'JrSmith', 'Bronny', 'Vincent', 'Kleber'],
    'V_off_Score': [9.2, 7.8, 5.8, 4.1, 3.5, 2.0,
                    5.0, 4.0, 7.5, 3.4, 5.2, 9.9,
                    2.5, 3.8, 8.8, 4.2, 4.5]
}

# 合并竞技+商业数据，确保1:1匹配
df = pd.merge(pd.DataFrame(on_court_data), pd.DataFrame(commercial_data), on='Player', how='inner')

# 计算综合价值总分 (用于气泡大小，权重：商业55% + 竞技45%，保留原逻辑)
df['V_Total'] = 0.45 * df['V_on_Score'] + 0.55 * df['V_off_Score']

# 按综合价值降序排序，生成完整排名
df = df.sort_values(by='V_Total', ascending=False).reset_index(drop=True)

# ==========================================
# 2. 四象限气泡图绘制 (完全保留原绘图逻辑，适配新数据)
# ==========================================
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei']  # 兼容中英文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 创建画布，保持原尺寸和分辨率
fig, ax = plt.subplots(figsize=(14, 10), dpi=150)

# 设定象限分割基准线 (适配新数据的合理及格线，竞技4.0 + 商业4.5)
x_mid = 4.0  # 竞技价值及格线
y_mid = 4.5  # 商业价值及格线

# 绘制象限分割虚线
ax.axvline(x=x_mid, color='gray', linestyle='--', alpha=0.6, linewidth=1)
ax.axhline(y=y_mid, color='gray', linestyle='--', alpha=0.6, linewidth=1)

# 颜色映射 (按综合价值V_Total渐变，保留原viridis配色)
cmap = plt.cm.viridis
norm = plt.Normalize(df['V_Total'].min(), df['V_Total'].max())

# 绘制气泡图 (保留原大小放大逻辑、透明度、边框样式)
scatter = ax.scatter(df['V_on_Score'], df['V_off_Score'],
                     s=(df['V_Total']**3.5)*0.8,  # 指数放大综合价值差异，便于观察
                     c=df['V_Total'],
                     cmap=cmap,
                     norm=norm,
                     alpha=0.85,
                     edgecolors='white',
                     linewidth=1.5)

# 添加球员名标签 (居中对齐，加粗，防重叠)
for i, txt in enumerate(df['Player']):
    ax.text(df['V_on_Score'][i], df['V_off_Score'][i], txt,
            fontsize=9, ha='center', va='center', fontweight='bold', color='black')

# ==========================================
# 3. 四象限等级标注 (保留原层级命名，适配新数据位置)
# ==========================================
# 标注样式 (白色圆角背景，半透明)
props = dict(boxstyle='round', facecolor='white', alpha=0.8)

# 右上：超级巨星 (高竞技+高商业)
ax.text(5.8, 9.0, "Tier 1: Superstars\n(High On-Court + High Commercial)",
        fontsize=11, color='green', bbox=props, ha='center')
# 左上：流量核心 (低竞技+高商业)
ax.text(3.8, 9.0, "Tier 2: Traffic Kings\n(Low On-Court + High Commercial)",
        fontsize=11, color='purple', bbox=props, ha='center')
# 左下：培养型球员 (低竞技+低商业)
ax.text(3.8, 3.0, "Tier 4: Development\n(Low On-Court + Low Commercial)",
        fontsize=11, color='gray', bbox=props, ha='center')
# 右下：实用型球员 (高竞技+低商业)
ax.text(5.8, 3.0, "Tier 3: Value Players\n(High On-Court + Low Commercial)",
        fontsize=11, color='blue', bbox=props, ha='center')

# ==========================================
# 4. 图表装饰与输出 (保留原样式，完善标签)
# ==========================================
ax.set_title('NBA Player Value Matrix (4-Quadrant Model)\nCommercial Value (Y) vs. Competitive Value (X)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Competitive Value ($V_{on}$)', fontsize=12)
ax.set_ylabel('Commercial Value ($V_{off}$)', fontsize=12)

# 适配数据范围的坐标轴限制
ax.set_xlim(df['V_on_Score'].min() - 0.2, df['V_on_Score'].max() + 0.2)
ax.set_ylim(df['V_off_Score'].min() - 0.2, df['V_off_Score'].max() + 0.2)

# 添加综合价值颜色条
cbar = plt.colorbar(scatter)
cbar.set_label('Total Value Score ($V_{total}$)', rotation=270, labelpad=15)

# 自动调整布局，防止标签重叠
plt.tight_layout()

# 保存高清图表 (可选，注释掉则仅显示)
plt.savefig('Player_4Quadrant_Value_Matrix.png', dpi=300, bbox_inches='tight', facecolor='white')
plt.show()

# ==========================================
# 5. 打印完整排名结果 (竞技+商业+综合，保留3位小数)
# ==========================================
print("="*80)
print("📊 NBA Player Complete Ranking (Competitive + Commercial Value)")
print("="*80)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.width', None)  # 自适应打印宽度
# ==========================================
# 5. 打印完整排名结果 (竞技+商业+综合，保留3位小数，适配所有pandas版本)
# ==========================================
print("="*80)
print("📊 NBA Player Complete Ranking (Competitive + Commercial Value)")
print("="*80)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
pd.set_option('display.width', None)  # 自适应打印宽度
# 兼容低版本pandas的索引标签写法
print(df[['Player', 'V_on_Score', 'V_off_Score', 'V_Total']].rename_axis('Rank').to_string(index=True))

# ==========================================
# 6. 四象限球员分布分析
# ==========================================
print("\n" + "="*80)
print("📈 4-Quadrant Player Distribution Analysis")
print("="*80)
# 按象限分类
q1 = df[(df['V_on_Score'] >= x_mid) & (df['V_off_Score'] >= y_mid)]  # 超级巨星
q2 = df[(df['V_on_Score'] < x_mid) & (df['V_off_Score'] >= y_mid)]   # 流量核心
q3 = df[(df['V_on_Score'] >= x_mid) & (df['V_off_Score'] < y_mid)]   # 实用型球员
q4 = df[(df['V_on_Score'] < x_mid) & (df['V_off_Score'] < y_mid)]    # 培养型球员

print(f"🏆 Tier 1 (Superstars) - {len(q1)} players: {', '.join(q1['Player'].tolist())}")
print(f"📣 Tier 2 (Traffic Kings) - {len(q2)} players: {', '.join(q2['Player'].tolist())}")
print(f"💪 Tier 3 (Value Players) - {len(q3)} players: {', '.join(q3['Player'].tolist())}")
print(f"🌱 Tier 4 (Development) - {len(q4)} players: {', '.join(q4['Player'].tolist())}")
print("="*80)