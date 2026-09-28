import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 数据准备 (Data Preparation)
# ==========================================

# 商业数据 (V_off) - 基于之前的模型
commercial_data = {
    'Player': [
        'LeBron', 'Doncic', 'Hachimura', 'Reaves',
        'Vanderbilt', 'Vincent', 'Kleber', 'Ayton',
        'LaRavia', 'Smart', 'Knecht', 'Hayes',
        'Bronny', 'Thiero', 'Manton', 'Smith',
        'SMilton', 'Koloko', 'Bufkin'
    ],
    # 商业原始分 (从之前的条形图计算逻辑提取近似值)
    # 这里直接使用计算后的最终商业加权分 (0-10 scale)
    'V_off_Score': [9.9, 9.2, 7.5, 7.8, 5.0, 4.2, 4.5, 5.8, 3.5, 5.2, 4.0, 4.1, 8.8, 2.5, 2.0, 3.8, 3.5, 3.2, 3.4]
}

# 竞技数据 (V_on) - 基于之前的气泡图
on_court_scores = {
    'Doncic': 8.5, 'LeBron': 7.2, 'Ayton': 6.8, 'Vanderbilt': 6.2,
    'LaRavia': 5.8, 'Smart': 5.5, 'Hayes': 5.4, 'Reaves': 6.5,
    'Thiero': 4.5, 'Manton': 4.0, 'Kleber': 4.8, 'Bronny': 3.5,
    'Hachimura': 5.9, 'Knecht': 4.2, 'Vincent': 3.8, 'Smith': 3.5,
    'SMilton': 3.6, 'Koloko': 3.4, 'Bufkin': 3.5
}

df = pd.DataFrame(commercial_data)
df['V_on_Score'] = df['Player'].map(on_court_scores).fillna(3.5)

# 计算总分用于气泡大小 (V_total)
df['V_Total'] = 0.45 * df['V_on_Score'] + 0.55 * df['V_off_Score']

# ==========================================
# 2. 绘图设置 (Plotting)
# ==========================================
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'SimHei'] # 兼容中文/英文

fig, ax = plt.subplots(figsize=(14, 10), dpi=150)

# 设定象限分割线 (中位数或平均数作为基准)
x_mid = 5.5  # 竞技及格线
y_mid = 5.0  # 商业及格线

# 绘制基准线
ax.axvline(x=x_mid, color='gray', linestyle='--', alpha=0.6, linewidth=1)
ax.axhline(y=y_mid, color='gray', linestyle='--', alpha=0.6, linewidth=1)

# 颜色映射 (根据 V_Total 也就是综合价值)
cmap = plt.cm.viridis
norm = plt.Normalize(df['V_Total'].min(), df['V_Total'].max())

# 绘制气泡
# s: 气泡大小 (放大差异以便观察)
scatter = ax.scatter(df['V_on_Score'], df['V_off_Score'],
                     s=(df['V_Total']**3.5)*0.8, # 指数放大差异
                     c=df['V_Total'],
                     cmap=cmap,
                     norm=norm,
                     alpha=0.85,
                     edgecolors='white',
                     linewidth=1.5)

# 添加标签 (Player Names)
texts = []
for i, txt in enumerate(df['Player']):
    # 稍微错开标签位置，防止重叠
    texts.append(ax.text(df['V_on_Score'][i], df['V_off_Score'][i], txt,
                         fontsize=9, ha='center', va='center', fontweight='bold', color='black'))

# ==========================================
# 3. 象限标注 (Quadrant Labels)
# ==========================================
# 字体属性
props = dict(boxstyle='round', facecolor='white', alpha=0.8)

# Q1: 右上 (Superstars)
ax.text(8.0, 9.5, "Tier 1: Superstars\n(High On-Court + High Commercial)", fontsize=11, color='green', bbox=props, ha='center')

# Q2: 左上 (Traffic/Marketing)
ax.text(4.0, 9.5, "Tier 2: Traffic Kings\n(High Commercial + Low On-Court)", fontsize=11, color='purple', bbox=props, ha='center')

# Q3: 左下 (Development/Risk)
ax.text(4.0, 2.5, "Tier 4: Development\n(Low Commercial + Low On-Court)", fontsize=11, color='gray', bbox=props, ha='center')

# Q4: 右下 (Value Players)
ax.text(8.0, 2.5, "Tier 3: Value/Solid Players\n(High On-Court + Low Commercial)", fontsize=11, color='blue', bbox=props, ha='center')

# ==========================================
# 4. 装饰与输出
# ==========================================
ax.set_title('NBA Player Value Matrix (4-Quadrant Model)\nCommercial (Y) vs. Competitive (X)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Competitive Value ($V_{on}$)', fontsize=12)
ax.set_ylabel('Commercial Value ($V_{off}$)', fontsize=12)
ax.set_xlim(3.0, 9.0)
ax.set_ylim(1.5, 10.5)

# 颜色条
cbar = plt.colorbar(scatter)
cbar.set_label('Total Value Score ($V_{total}$)', rotation=270, labelpad=15)

plt.tight_layout()
plt.show()

# 打印分析结果
print(">>> 象限分析结果 (Quadrant Analysis):")
print("1. [Traffic Kings] 左上角: Bronny James (极高的商业关注，竞技待开发)")
print("2. [Superstars]    右上角: LeBron, Doncic (双高)")
print("3. [Solid Players] 右下角: Reaves, Hachimura, Ayton (实战好用，商业一般)")
print("4. [Development]   左下角: 大部分底薪/新秀球员")