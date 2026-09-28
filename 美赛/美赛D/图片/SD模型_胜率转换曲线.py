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
    # 胜率模型参数
    AVG_OPPONENT = 20.0
    SENSITIVITY_K = 0.35


data = {
    'Player': ['Doncic', 'LeBron', 'Reaves', 'Ayton', 'Hachimura', 'Vanderbilt', 'Hayes', 'Smart', 'Vincent', 'Knecht',
               'Bronny'],
    'Si': [7.41, 4.65, 6.16, 5.34, 4.34, 4.44, 4.26, 4.11, 3.43, 3.65, 3.39],
    'Salary': [46.0, 52.6, 13.9, 8.1, 18.3, 11.6, 3.4, 5.1, 11.5, 4.0, 2.0]
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

lakers_raw = (df['Si'] * xi).sum()
lakers_perf = lakers_raw - Config.LAMBDA * (lakers_raw ** 2)

# 计算胜场
win_prob = 1 / (1 + np.exp(-Config.SENSITIVITY_K * (lakers_perf - Config.AVG_OPPONENT)))
lakers_wins = win_prob * 82


# ==========================================
# 3. 绘图逻辑
# ==========================================
def plot_win_curve():
    # 生成 S 型曲线数据
    x = np.linspace(10, 30, 100)
    y_wins = 82 / (1 + np.exp(-Config.SENSITIVITY_K * (x - Config.AVG_OPPONENT)))

    plt.figure(figsize=(10, 6), facecolor='white')

    # 绘制曲线
    plt.plot(x, y_wins, color=Config.PURPLE, linewidth=3, label='Win Probability Model')

    # 填充下方区域
    plt.fill_between(x, y_wins, 0, color=Config.GOLD, alpha=0.15)

    # 标记湖人位置
    plt.scatter([lakers_perf], [lakers_wins], color=Config.GOLD, s=200, edgecolors='black', zorder=10)

    # 绘制基准线
    plt.axvline(Config.AVG_OPPONENT, color='gray', linestyle=':', label='League Average')
    plt.axhline(41, color='gray', linestyle=':', alpha=0.5)

    # 添加注释
    plt.annotate(
        f"Dominant Zone\n({lakers_perf:.1f}, {lakers_wins:.1f} Wins)",
        xy=(lakers_perf, lakers_wins),
        xytext=(lakers_perf + 2, lakers_wins - 15),
        arrowprops=dict(facecolor='black', shrink=0.05),
        fontsize=12, fontweight='bold', color=Config.PURPLE,
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec=Config.PURPLE, alpha=0.9)
    )

    plt.title('2. Win Transformation Curve\n(Logistic S-Curve)', fontsize=16, fontweight='bold', color=Config.PURPLE,
              pad=15)
    plt.xlabel('Effective Team Performance (T_perf)', fontsize=12, fontweight='bold')
    plt.ylabel('Projected Season Wins', fontsize=12, fontweight='bold')
    plt.legend(loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    filename = '2_Win_Curve.png'
    plt.savefig(filename, dpi=150)
    print(f"图表已生成: {filename}")
    plt.show()


if __name__ == "__main__":
    plot_win_curve()