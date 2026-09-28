import plotly.graph_objects as go
import numpy as np
import os

# ==========================================
# 1. 数据准备
# ==========================================
years = [2025, 2026, 2027, 2028, 2029, 2030]

# --- 模拟数据 ---
rev_ecosystem = [200, 210, 220, 230, 240, 250]
t_scores = [75, 72, 55, 60, 70, 80]
rev_competitive = [150 * np.log(1 + t) * 0.6 for t in t_scores]
star_scores = [27.0, 26.5, 17.8, 18.5, 20.0, 22.0]
rev_star_power = [20 * s for s in star_scores]

# ==========================================
# 2. 绘图：堆叠区域
# ==========================================
fig = go.Figure()

# 1. 灰色底层
fig.add_trace(go.Scatter(
    x=years, y=rev_ecosystem, mode='lines', name='1. Ecosystem Base (Media)',
    stackgroup='one', line=dict(width=0.5, color='rgb(180, 180, 180)'), fillcolor='rgba(200, 200, 200, 0.5)'
))
# 2. 金色中层
fig.add_trace(go.Scatter(
    x=years, y=rev_competitive, mode='lines', name='2. Competitive Value (Wins)',
    stackgroup='one', line=dict(width=0.5, color='#FDB927'), fillcolor='rgba(253, 185, 39, 0.8)'
))
# 3. 紫色顶层
fig.add_trace(go.Scatter(
    x=years, y=rev_star_power, mode='lines', name='3. Star Power (Traffic)',
    stackgroup='one', line=dict(width=0.5, color='#552583'), fillcolor='rgba(85, 37, 131, 0.85)'
))

# ==========================================
# 3. 核心修饰：垂直黑线 + 详细注释
# ==========================================

# A. 添加垂直黑色虚线 (Vertical Dashed Lines)
fig.add_vline(x=2025, line_width=2, line_dash="dash", line_color="black", opacity=0.8)
fig.add_vline(x=2027, line_width=2, line_dash="dash", line_color="black", opacity=0.8)

# B. 添加详细注释 (恢复了之前的详细文本)

# 注释 1: 2027 詹姆斯悬崖 (详细版)
fig.add_annotation(
    x=2027, y=880,
    text="<b>The 'LeBron Cliff'</b><br>Star Power drops linearly here,<br>but Ecosystem (Gray) protects the downside.", # 恢复了详细解释
    showarrow=True,
    arrowhead=2,
    arrowsize=1.5,
    arrowwidth=2,
    arrowcolor="black", # 黑色箭头
    ax=0, ay=-90,       # 引线向上拉长，避开曲线
    bgcolor="white",
    bordercolor="black",
    align="center"
)

# 注释 2: 2025 巅峰期 (详细版)
fig.add_annotation(
    x=2025, y=1050,
    text="<b>Peak Revenue Phase</b><br>(Luka + LeBron + Bronny)<br>Maximized Commercial Value.", # 恢复了详细解释
    showarrow=True,
    arrowhead=2,
    arrowsize=1.5,
    arrowwidth=2,
    arrowcolor="black", # 黑色箭头
    ax=70, ay=-30,      # 引线向右拉
    bgcolor="white",
    bordercolor="black",
    align="left"
)

# ==========================================
# 4. 布局优化
# ==========================================
fig.update_layout(
    title=dict(
        text='<b>Dual-Track Revenue Growth Model (2025-2030)</b><br><i>Visualizing the Logic of Formula (4) in PDF</i>',
        font=dict(size=20),
        y=0.96
    ),
    xaxis=dict(
        title='Season Year',
        tickmode='array',
        tickvals=years,
        showgrid=False # 隐藏网格，突出黑线
    ),
    yaxis=dict(
        title='Total Projected Revenue ($ Million)',
        showgrid=True,
        gridcolor='lightgray',
        range=[0, 1350] # 留出顶部空间给注释
    ),
    width=1000, height=650,
    legend=dict(
        orientation="h",
        y=-0.15, x=0.5, xanchor="center", # 图例在下方居中
        bgcolor='rgba(255,255,255,0.9)',
        bordercolor='black',
        borderwidth=1
    ),
    template="plotly_white",
    margin=dict(t=100, b=100)
)

# 保存
file_name = "Dual_Track_Detailed_Annotations.html"
fig.write_html(file_name)
print(f"✅ 图表已生成 (含垂直黑线 + 详细注释): {os.path.abspath(file_name)}")