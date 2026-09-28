import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


# ==========================================
# 1. 配置参数与数据
# ==========================================
class Config:
    PURPLE = '#552583'
    GOLD = '#FDB927'
    # 内耗系数 (校准值)
    LAMBDA = 0.004


# 球员数据
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
# 分配时间权重
weights = (df['Si'] / df['Si'].max()) * 0.7 + (df['Salary'] / df['Salary'].max()) * 0.3
minutes = (weights / weights.sum()) * 240.0
minutes = minutes.clip(8, 37.5)
minutes = minutes * (240.0 / minutes.sum())
xi = minutes / 48.0

# 计算湖人点坐标
lakers_raw = (df['Si'] * xi).sum()
lakers_loss = Config.LAMBDA * (lakers_raw ** 2)
lakers_perf = lakers_raw - lakers_loss


# ==========================================
# 3. 绘图逻辑
# ==========================================
def plot_friction_curve():
    # 生成曲线数据
    x = np.linspace(0, 40, 100)
    y_eff = x - Config.LAMBDA * (x ** 2)

    plt.figure(figsize=(10, 6), facecolor='white')

    # 绘制无内耗理想线 (y=x)
    plt.plot(x, x, color='gray', linestyle='--', alpha=0.5, label='Theoretical Max (No Friction)')

    # 绘制实际曲线
    plt.plot(x, y_eff, color=Config.PURPLE, linewidth=3, label='Actual Performance')

    # 填充损失区域
    plt.fill_between(x, y_eff, 0, color=Config.PURPLE, alpha=0.1)

    # 标记湖人位置
    plt.scatter([lakers_raw], [lakers_perf], color=Config.GOLD, s=200, edgecolors='black', zorder=10)

    # 添加注释
    plt.annotate(
        f"Efficiency Loss: -{lakers_loss:.1f}\n(Star Overlap)",
        xy=(lakers_raw, lakers_perf),
        xytext=(lakers_raw - 12, lakers_perf + 2),
        arrowprops=dict(facecolor='black', shrink=0.05),
        fontsize=12, fontweight='bold', color='#D40000',
        bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#D40000", alpha=0.9)
    )

    plt.title('1. Superteam Friction Curve\n(Diminishing Returns)', fontsize=16, fontweight='bold', color=Config.PURPLE,
              pad=15)
    plt.xlabel('Nominal Talent Sum (Raw Power)', fontsize=12, fontweight='bold')
    plt.ylabel('Effective Performance (After Friction)', fontsize=12, fontweight='bold')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.tight_layout()

    filename = '1_Friction_Curve.png'
    plt.savefig(filename, dpi=150)
    print(f"图表已生成: {filename}")
    plt.show()


if __name__ == "__main__":
    plot_friction_curve()