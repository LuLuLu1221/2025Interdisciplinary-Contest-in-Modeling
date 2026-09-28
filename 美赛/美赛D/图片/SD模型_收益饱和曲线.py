import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# ==========================================
# 1. 配置参数与数据
# ==========================================
class Config:
    PURPLE = '#552583'
    GOLD = '#FDB927'
    LAMBDA = 0.004
    AVG_OPPONENT = 20.0
    SENSITIVITY_K = 0.35
    # 营收模型参数
    FIXED_REVENUE = 192.0
    ALPHA = 120.0  # 对数增长系数


data = {
    'Player': ['Doncic', 'LeBron', 'Reaves', 'Ayton', 'Hachimura', 'Vanderbilt', 'Hayes', 'Smart', 'Vincent', 'Knecht',
               'Bronny'],
    'Si': [7.41, 4.65, 6.16, 5.34, 4.34, 4.44, 4.26, 4.11, 3.43, 3.65, 3.39],
    'Salary': [46.0, 52.6, 13.9, 8.1, 18.3, 11.6, 3.4, 5.1, 11.5, 4.0, 2.0],
    # 商业价值数据 (用于估算基准线高度)
    'Commercial': [8.98, 9.18, 6.57, 4.92, 6.78, 4.44, 2.51, 5.13, 3.29, 3.23, 8.76]
}
df = pd.DataFrame(data)

# ==========================================
# 2. 计算逻辑
# ==========================================
weights = (df['Si'] / df['Si'].max()) * 0.7 + (df['Salary'] / df['Salary'].max()) * 0.3
minutes = (weights / weights.sum()) * 240.0
minutes = minutes.clip(8, 37.5)
minutes = minutes * (240.0 / minutes.sum())
xi = minutes / 48.0

# 战力与胜场
lakers_raw = (df['Si'] * xi).sum()
lakers_perf = lakers_raw - Config.LAMBDA * (lakers_raw ** 2)
win_prob = 1 / (1 + np.exp(-Config.SENSITIVITY_K * (lakers_perf - Config.AVG_OPPONENT)))
lakers_wins = win_prob * 82

# 营收计算
# 估算商业收入常数 (仅用于画图定位)
avg_xi = xi.mean()
comm_score = (df['Commercial'] * (xi / avg_xi)).sum()
comm_revenue_est = comm_score * 5.5

# 总营收点
lakers_rev = Config.ALPHA * np.log(lakers_wins - 10) + comm_revenue_est + Config.FIXED_REVENUE


# ==========================================
# 3. 绘图逻辑
# ==========================================
def plot_revenue_curve():
    # 生成对数曲线数据 (从11胜开始)
    x = np.linspace(11, 75, 100)
    # y = Performance_Rev + Fixed + Commercial_Base
    y_rev = Config.ALPHA * np.log(x - 10) + Config.FIXED_REVENUE + comm_revenue_est

    plt.figure(figsize=(10, 6), facecolor='white')

    # 绘制曲线
    plt.plot(x, y_rev, color=Config.GOLD, linewidth=3, label='Revenue Growth')

    # 填充下方区域
    plt.fill_between(x, y_rev, Config.FIXED_REVENUE, color=Config.PURPLE, alpha=0.1)

    # 标记湖人位置
    plt.scatter([lakers_wins], [lakers_rev], color=Config.PURPLE, s=200, edgecolors='white', linewidth=2, zorder=10)

    # 添加注释
    plt.annotate(
        f"High Commercial Value\n({lakers_wins:.1f} Wins, ${lakers_rev:.1f}M)",
        xy=(lakers_wins, lakers_rev),
        xytext=(lakers_wins - 25, lakers_rev - 50),
        arrowprops=dict(facecolor='black', shrink=0.05),
        fontsize=12, fontweight='bold', color=Config.PURPLE,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=Config.PURPLE, alpha=0.9)
    )

    plt.title('3. Revenue Saturation Curve\n(Logarithmic Growth)', fontsize=16, fontweight='bold', color=Config.PURPLE,
              pad=15)
    plt.xlabel('Season Wins', fontsize=12, fontweight='bold')
    plt.ylabel('Total Projected Revenue ($M)', fontsize=12, fontweight='bold')
    plt.legend(loc='lower right')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    filename = '3_Revenue_Curve.png'
    plt.savefig(filename, dpi=150)
    print(f"图表已生成: {filename}")
    plt.show()


if __name__ == "__main__":
    plot_revenue_curve()