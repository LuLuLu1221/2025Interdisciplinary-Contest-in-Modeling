import numpy as np
import plotly.graph_objects as go


# ==========================================
# 1. 定义综合价值模型 (Valuation Model)
# ==========================================
def calculate_valuation(win_pct, comm_score):
    """
    根据胜率和商业值计算球队市值 (单位: Billion $)。
    模型公式: V = m * [ alpha * ln(Wins - 10) + beta * Comm + theta ]
    """
    # 核心参数 (基于大球市模型校准)
    m = 18.15  # 市值倍数 (Market Multiple)
    alpha = 120.0  # 赢球收入系数 (Win Coefficient)
    beta = 5.5  # 商业价值系数 (Commercial Coefficient)
    theta = 192.0  # 固定收入基数 (Fixed Revenue)

    # 将胜率转换为胜场 (82场常规赛)
    wins = win_pct * 82

    # 设定有效胜场下限 (避免 Log 负数异常)
    wins_safe = np.maximum(wins, 11)

    # 计算总营收 (Million $)
    revenue = alpha * np.log(wins_safe - 10) + beta * comm_score + theta

    # 计算总市值 (Billion $)
    valuation = (revenue * m) / 1000
    return valuation


# ==========================================
# 2. 准备绘图数据 (Data Preparation)
# ==========================================
# A. 生成 3D 曲面网格数据
x_wins = np.linspace(0.25, 0.90, 50)  # X轴: 胜率范围 25% - 90%
y_comm = np.linspace(20, 100, 50)  # Y轴: 商业值范围 20 - 100
X, Y = np.meshgrid(x_wins, y_comm)  # 生成网格
Z = calculate_valuation(X, Y)  # 计算对应的市值 Z

# B. 设定湖人队当前数据点 (Lakers Specific Data)
lakers_win_pct = 0.577  # 胜率 57.7%
lakers_wins = lakers_win_pct * 82  # 约为 47.3 胜
lakers_comm_val = 63.79  # 商业价值总分 (基于球员名单)

# 计算湖人当前市值
lakers_val = calculate_valuation(lakers_win_pct, lakers_comm_val)

print(f"Lakers Data Point -> Wins: {lakers_wins:.1f}, Comm: {lakers_comm_val:.1f}, Val: ${lakers_val:.2f}B")

# ==========================================
# 3. 创建 3D 交互图 (White Theme)
# ==========================================
fig = go.Figure()

# --- 图层 A: 3D 价值曲面 (Surface) ---
fig.add_trace(go.Surface(
    z=Z, x=X * 82, y=Y,  # X轴显示为具体胜场数
    colorscale=[[0, '#552583'], [1, '#FDB927']],  # 湖人紫到金渐变
    opacity=0.9,
    name='Valuation Model',
    hovertemplate='Wins: %{x:.1f}<br>Comm Value: %{y:.1f}<br>Valuation: $%{z:.2f}B<extra></extra>'
))

# --- 图层 B: 湖人队数据点 (Red Marker) ---
fig.add_trace(go.Scatter3d(
    x=[lakers_wins],
    y=[lakers_comm_val],
    z=[lakers_val],
    mode='markers+text',
    marker=dict(
        size=15,
        color='#D40000',  # 🔴 设置为鲜红色
        line=dict(color='#FFFFFF', width=2),
        symbol='diamond'  # 菱形图标
    ),
    text=[f"LAKERS 2026<br>${lakers_val:.2f}B"],  # 标注文字
    textposition="top center",
    textfont=dict(
        color='#D40000',  # 🔴 文字颜色也为红色
        size=14,
        family="Arial Black"
    ),
    name='Lakers Current Status'
))

# --- 图层 C: 垂直投影线 (Drop Line) ---
# 画一条从数据点垂直落到地面的虚线，增强空间感
fig.add_trace(go.Scatter3d(
    x=[lakers_wins, lakers_wins],
    y=[lakers_comm_val, lakers_comm_val],
    z=[0, lakers_val],
    mode='lines',
    line=dict(color='gray', width=4, dash='dash'),  # 灰色虚线适配白底
    name='Projection'
))

# ==========================================
# 4. 布局美化 (Layout Customization)
# ==========================================
fig.update_layout(
    title=dict(
        text="Lakers Comprehensive Value Model (3D Interactive)",
        font=dict(size=24, color='#552583', family="Impact"),  # 紫色标题
        y=0.95
    ),
    scene=dict(
        # X轴设置 (白底黑字)
        xaxis=dict(
            title='Season Wins (Performance)',
            backgroundcolor='white',
            gridcolor='#E0E0E0',
            zerolinecolor='#E0E0E0',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        # Y轴设置
        yaxis=dict(
            title='Commercial Power (Star Impact)',
            backgroundcolor='white',
            gridcolor='#E0E0E0',
            zerolinecolor='#E0E0E0',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        # Z轴设置
        zaxis=dict(
            title='Franchise Value ($ Billion)',
            backgroundcolor='white',
            gridcolor='#E0E0E0',
            zerolinecolor='#E0E0E0',
            title_font=dict(color='black'),
            tickfont=dict(color='black')
        ),
        # 初始视角
        camera=dict(
            eye=dict(x=1.6, y=-1.6, z=0.8)
        ),
        bgcolor='white'  # ⚪ 3D场景背景纯白
    ),
    paper_bgcolor='white',  # ⚪ 画布背景纯白
    font=dict(color='black'),  # 全局字体黑色
    margin=dict(l=0, r=0, b=0, t=50)  # 减少边距
)

# ==========================================
# 5. 保存并输出
# ==========================================
file_name = "Lakers_3D_Valuation_White.html"
fig.write_html(file_name)

print(f"✅ 成功生成交互式图表: {file_name}")
print("请在文件浏览器中找到该文件，并使用 Chrome/Edge/Safari 打开。")