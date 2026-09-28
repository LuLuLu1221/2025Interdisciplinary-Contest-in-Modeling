import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. 数据准备 (Data Preparation)
# ==========================================
# 来源于你上传的表格图片 (Rank, Player, Minutes, G)
# 假设 Von (竞技价值) 和 V_comm (商业价值) 基于之前的上下文估算
player_data = [
    {'Player': 'Luka Doncic',       'G': 38, 'Minutes': 1380, 'Von': 6.8, 'V_comm': 9.0}, # 超级巨星
    {'Player': 'Jake LaRavia',      'G': 46, 'Minutes': 1261, 'Von': 4.5, 'V_comm': 1.5},
    {'Player': 'Deandre Ayton',     'G': 41, 'Minutes': 1161, 'Von': 5.0, 'V_comm': 4.9},
    {'Player': 'Rui Hachimura',     'G': 36, 'Minutes': 1084, 'Von': 4.2, 'V_comm': 6.8},
    {'Player': 'Marcus Smart',      'G': 37, 'Minutes': 1056, 'Von': 3.7, 'V_comm': 5.1},
    {'Player': 'LeBron James',      'G': 29, 'Minutes': 962,  'Von': 4.9, 'V_comm': 9.2}, # 流量之王
    {'Player': 'Austin Reaves',     'G': 23, 'Minutes': 812,  'Von': 5.4, 'V_comm': 6.6},
    {'Player': 'Jarred Vanderbilt', 'G': 37, 'Minutes': 720,  'Von': 4.1, 'V_comm': 4.4},
    {'Player': 'Jaxson Hayes',      'G': 38, 'Minutes': 671,  'Von': 4.8, 'V_comm': 2.5},
    {'Player': 'Gabe Vincent',      'G': 26, 'Minutes': 507,  'Von': 3.3, 'V_comm': 3.3},
    {'Player': 'Dalton Knecht',     'G': 37, 'Minutes': 458,  'Von': 3.9, 'V_comm': 3.2},
    {'Player': 'Bronny James',      'G': 25, 'Minutes': 173,  'Von': 3.6, 'V_comm': 8.8}, # 流量高但竞技低
]

df = pd.DataFrame(player_data)

# 计算资源分配系数 x_i (Resource Allocation)
# 假设一场比赛48分钟，计算每场平均上场时间占比
df['MPG'] = df['Minutes'] / df['G']
df['xi'] = df['MPG'] / 48.0

# 计算基础贡献 (Raw Contribution)
df['Raw_Comp_Contrib'] = df['Von'] * df['xi']   # Si * xi
df['Raw_Comm_Contrib'] = df['V_comm'] * df['xi'] # Fi * xi

# ==========================================
# 2. 定义模型函数 (Model Functions)
# ==========================================

def calculate_t_perf(raw_sum, lambda_friction):
    """
    计算竞技表现 T_perf
    公式: Sum(Si*xi) - Lambda * (Sum(Si*xi))^2
    """
    friction_loss = lambda_friction * (raw_sum ** 2)
    return raw_sum - friction_loss

def calculate_revenue(t_perf, comm_sum, alpha, beta, base_media):
    """
    计算总收入 R_total
    公式: alpha * ln(1 + T_perf) + beta * Sum(Fi*xi) + theta * E_media
    """
    # 避免 log(负数)
    valid_t_perf = max(0, t_perf)
    rev_competitive = alpha * np.log(1 + valid_t_perf)
    rev_commercial = beta * comm_sum
    return rev_competitive + rev_commercial + base_media

# ==========================================
# 3. 模拟计算 (Simulation)
# ==========================================

# 设置模型参数 (Model Parameters)
lambda_current = 0.015  # 当前体系的摩擦系数
lambda_high = 0.035     # 球权冲突严重的摩擦系数
alpha = 50.0            # 赢球奖金系数
beta = 8.0              # 流量变现系数
theta_media = 100.0     # 基础媒体转播费

# 当前球队的汇总数据
current_raw_comp_sum = df['Raw_Comp_Contrib'].sum()
current_comm_sum = df['Raw_Comm_Contrib'].sum()

# 计算当前 T_perf
current_t_perf = calculate_t_perf(current_raw_comp_sum, lambda_current)

# 生成模拟曲线数据 (用于绘图)
x_range = np.linspace(0, 35, 100) # 模拟不同的阵容强度总和
y_low_friction = calculate_t_perf(x_range, lambda_current)
y_high_friction = calculate_t_perf(x_range, lambda_high)

# ==========================================
# 4. 绘图 (Visualization)
# ==========================================
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei'] # 尝试兼容中文，失败则回退Arial
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")

fig = plt.figure(figsize=(18, 12))

# --- 图表 1: 竞技表现摩擦曲线 (Team Performance Model) ---
ax1 = plt.subplot(2, 2, 1)
ax1.plot(x_range, y_low_friction, label=f'Optimized System (lambda={lambda_current})', color='green', linewidth=3)
ax1.plot(x_range, y_high_friction, label=f'High Friction (lambda={lambda_high})', color='red', linestyle='--')

# 标记当前球队位置
ax1.scatter([current_raw_comp_sum], [current_t_perf], color='blue', s=200, zorder=5, label='Lakers Current')
ax1.annotate(f'Current\nRaw Sum: {current_raw_comp_sum:.1f}\nReal Perf: {current_t_perf:.1f}',
             xy=(current_raw_comp_sum, current_t_perf),
             xytext=(current_raw_comp_sum-8, current_t_perf-3),
             arrowprops=dict(facecolor='black', shrink=0.05))

ax1.set_title('Model A: Team Performance & Friction Effect', fontsize=14, weight='bold')
ax1.set_xlabel('Sum of Individual Skill (Sum Si * xi)', fontsize=12)
ax1.set_ylabel('Realized Team Performance (T_perf)', fontsize=12)
ax1.legend()
ax1.grid(True, alpha=0.3)

# --- 图表 2: 收入结构模型 (Revenue Model) ---
ax2 = plt.subplot(2, 2, 2)

# 计算收入组成
rev_win = alpha * np.log(1 + current_t_perf)
rev_star = beta * current_comm_sum
rev_media = theta_media

components = ['Winning (Comp)', 'Star Power (Comm)', 'Media/Base']
values = [rev_win, rev_star, rev_media]
colors = ['#4c72b0', '#c44e52', '#55a868']

ax2.bar(components, values, color=colors, alpha=0.8)
for i, v in enumerate(values):
    ax2.text(i, v + 2, f"${v:.1f}M", ha='center', weight='bold')

total_rev = sum(values)
ax2.set_title(f'Model B: Total Revenue Structure (Total: ${total_rev:.1f}M)', fontsize=14, weight='bold')
ax2.set_ylabel('Projected Revenue (Millions)', fontsize=12)

# --- 图表 3: 球员价值矩阵 (Player Matrix) ---
ax3 = plt.subplot(2, 1, 2)
sns.scatterplot(
    data=df, x='Raw_Comp_Contrib', y='Raw_Comm_Contrib',
    size='MPG', sizes=(100, 1000), hue='Von', palette='viridis', ax=ax3
)

for i in range(df.shape[0]):
    ax3.text(df.Raw_Comp_Contrib[i]+0.02, df.Raw_Comm_Contrib[i], df.Player[i], fontsize=10, weight='bold')

ax3.set_title('Player Contribution Matrix: Winning (X) vs. Earning (Y)', fontsize=14, weight='bold')
ax3.set_xlabel('Weighted Competitive Contribution (Si * xi)', fontsize=12)
ax3.set_ylabel('Weighted Commercial Contribution (Fi * xi)', fontsize=12)

# 辅助线
ax3.axhline(y=df['Raw_Comm_Contrib'].mean(), color='gray', linestyle='--', alpha=0.5)
ax3.axvline(x=df['Raw_Comp_Contrib'].mean(), color='gray', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()