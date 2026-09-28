import plotly.graph_objects as go
import numpy as np
import pandas as pd
import os

print("正在初始化数据...")


# ==========================================
# 第一部分：生成 3D 交互图 (.html)
# ==========================================
def generate_3d_html():
    print("正在生成 3D 优化曲面图...")

    # 1. 模拟网格数据
    # X轴: 薪资 (1.4亿 - 3.0亿)
    payroll_range = np.linspace(140, 300, 50)
    # Y轴: 竞技分 (30 - 100)
    perf_range = np.linspace(30, 100, 50)
    X, Y = np.meshgrid(payroll_range, perf_range)

    # 2. 参数 (基于 PDF)
    m = 18.0  # 市值倍数
    alpha = 150.0  # 竞技收入系数
    theta = 200.0  # 生态基座
    base_brand = 500.0  # 品牌基础

    # 3. 计算 Z (综合价值)
    # 假设薪资越高，球星商业价值(Star Power)越高
    star_power_est = (X - 100) * 0.15

    # 收入 R
    R_total = alpha * np.log(1 + Y) + 20.0 * star_power_est + theta

    # 成本 Cost (含奢侈税悬崖)
    tax_threshold = 170.0
    excess = np.maximum(0, X - tax_threshold)
    tax_penalty = excess * (1.5 + (excess / 50.0) * 1.5)  # 阶梯税率
    total_cost = X + tax_penalty + 50

    # 目标函数 Z
    Profit = R_total - total_cost
    Valuation = m * R_total + (base_brand + 50 * (star_power_est / 8))
    Z_score = 0.45 * Profit + 0.55 * (Valuation * 0.05)

    # 4. 绘图
    fig = go.Figure(data=[
        go.Surface(
            z=Z_score, x=X, y=Y,
            colorscale='Viridis',
            opacity=0.9,
            colorbar=dict(title='Global Value (Z)'),
        )
    ])

    # 标记当前湖人位置
    fig.add_trace(go.Scatter3d(
        x=[197.8], y=[65.0], z=[np.max(Z_score)],
        mode='markers+text',
        marker=dict(size=8, color='red', symbol='diamond'),
        text=['Current Roster<br>(High Cost)'],
        textposition='top center'
    ))

    fig.update_layout(
        title='Global Objective Function (Profit vs. Wins)',
        scene=dict(
            xaxis_title='Payroll ($M)',
            yaxis_title='Win Score',
            zaxis_title='Global Value (Z)',
        ),
        width=1200, height=800
    )

    # 保存为 HTML
    filename = "3D_Model_Optimization.html"
    fig.write_html(filename)
    print(f"✅ 3D图已保存为: {os.path.abspath(filename)}")


# ==========================================
# 第二部分：生成双轨堆叠图 (.png)
# ==========================================
def generate_dual_track_png():
    print("正在生成双轨收入增长图...")

    years = [2025, 2026, 2027, 2028, 2029, 2030]

    # 数据模拟
    rev_ecosystem = [200, 210, 220, 230, 240, 250]
    perf_scores = [70, 75, 60, 50, 65, 80]
    rev_competitive = [150 * np.log(1 + p) * 0.6 for p in perf_scores]

    star_scores = [26, 26, 17, 18, 20, 22]  # 模拟LBJ退役后的下降
    rev_star_power = [20 * s for s in star_scores]

    fig = go.Figure()

    # 层1: 生态
    fig.add_trace(go.Scatter(
        x=years, y=rev_ecosystem, mode='lines', name='Ecosystem (Media)',
        stackgroup='one', line=dict(width=0.5, color='lightgray'), fillcolor='lightgray'
    ))

    # 层2: 竞技
    fig.add_trace(go.Scatter(
        x=years, y=rev_competitive, mode='lines', name='Competitive (Wins)',
        stackgroup='one', line=dict(width=0.5, color='#FDB927'), fillcolor='rgba(253, 185, 39, 0.7)'
    ))

    # 层3: 商业
    fig.add_trace(go.Scatter(
        x=years, y=rev_star_power, mode='lines', name='Star Power (Luka/LBJ)',
        stackgroup='one', line=dict(width=0.5, color='#552583'), fillcolor='rgba(85, 37, 131, 0.8)'
    ))

    fig.update_layout(
        title='Dual-Track Revenue Growth (2025-2030)',
        xaxis_title='Year',
        yaxis_title='Revenue ($M)',
        width=1000, height=600,
        legend=dict(orientation="h", y=1.02, x=1)
    )

    # 保存为 PNG (需要 kaleido)
    png_name = "Dual_Track_Revenue.png"
    try:
        fig.write_image(png_name, scale=2)  # scale=2 让图片更清晰
        print(f"✅ 双轨图已保存为: {os.path.abspath(png_name)}")
    except Exception as e:
        print(f"⚠️ 无法直接生成PNG (缺少kaleido库). 正在保存为HTML作为备用...")
        print(f"   错误详情: {e}")
        fig.write_html("Dual_Track_Revenue.html")
        print(f"✅ 已保存为 HTML: {os.path.abspath('Dual_Track_Revenue.html')} (请打开并截图)")


# ==========================================
# 执行
# ==========================================
if __name__ == "__main__":
    generate_3d_html()
    generate_dual_track_png()
    print("\n所有任务完成！请在您的文件夹中查看生成的文件。")