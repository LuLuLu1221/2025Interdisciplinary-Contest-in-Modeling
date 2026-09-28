import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 初始化数据 (Initialize Data)
# ==========================================
initial_data = {
    'Player': ['Luka Doncic', 'Austin Reaves', 'Deandre Ayton', 'LeBron James', 'Jaxson Hayes',
               'Chris Manon', 'Jake LaRavia', 'Rui Hachimura', 'Jarred Vanderbilt', 'Dalton Knecht'],
    'Age': [26, 27, 27, 41, 25, 24, 24, 27, 26, 24],
    'G': [38, 23, 41, 29, 38, 4, 46, 36, 37, 37],
    'Minutes': [1380, 812, 1161, 962, 671, 14, 1261, 1084, 720, 458],
    # S_i: 竞技能力 (Athletic), F_i: 商业号召力 (Commercial)
    'S_i': [6.57, 5.40, 4.92, 4.89, 4.76, 4.60, 4.50, 4.18, 4.08, 3.93],
    'F_i': [8.04, 6.90, 5.55, 9.18, 5.41, 3.62, 5.03, 5.06, 4.33, 4.43]
}

df_roster = pd.DataFrame(initial_data)
# x_i: 资源分配变量 (归一化时间)
df_roster['MPG'] = df_roster['Minutes'] / df_roster['G']
df_roster['x_i'] = df_roster['MPG'] / 48.0

# ==========================================
# 2. 全局参数 (Global Parameters) - 包含新模型参数
# ==========================================
W1 = 0.60  # 利润权重
W2 = 0.40  # 估值增量权重
GAMMA = 0.90  # 时间折现率
T_YEARS = 5  # 模拟年限

SALARY_CAP = 180.0
TAX_RATE = 1.5

# --- Franchise Value Model 特定参数 ---
VALUATION_M = 18.0  # m: Revenue Multiple (湖人特定倍数)
BRAND_BASE = 500.0  # P_brand 基础值 ($M)
STAR_THRESHOLD = 7.0  # F_i 大于此值视为"超级球星" (LeBron=9.18, Luka=8.04)

# --- 收入模型参数 ---
ALPHA = 150.0  # 竞技收入系数
BETA = 8.0  # 球星收入系数
THETA = 1.0  # 外部环境系数
E_MEDIA = 120.0
LAMBDA = 0.005

np.random.seed(42)


# ==========================================
# 3. 核心计算模型 (Core Calculation Models)
# ==========================================

def get_performance_metrics(current_df):
    """
    辅助函数：计算 T_perf 并转化为 胜场(Wins) 和 季后赛轮次
    """
    raw_talent = np.sum(current_df['S_i'] * current_df['x_i'])
    friction = LAMBDA * (raw_talent ** 2)
    t_perf = raw_talent - friction

    # 将抽象的 t_perf 转化为胜率 (Sigmoid映射)，再转为胜场
    # 假设 t_perf=20 是 50% 胜率
    win_prob = 1 / (1 + np.exp(-0.3 * (t_perf - 20.0)))
    est_wins = win_prob * 82.0

    # 估算季后赛轮次 (简单规则)
    if est_wins < 42:
        rounds = 0
    elif est_wins < 48:
        rounds = 1  # 附加赛/首轮
    elif est_wins < 56:
        rounds = 2  # 次轮
    elif est_wins < 65:
        rounds = 3  # 决
    else:
        rounds = 4  # 总决赛

    return t_perf, est_wins, rounds


def calculate_revenue_profit(current_df):
    """
    计算当期利润 (Pi_t) 和 总常规赛收入 (R_total)
    """
    t_perf, _, _ = get_performance_metrics(current_df)

    # 1. Dual-Track Revenue (R_total)
    # R_total = alpha * ln(1+T) + beta * sum(F*x) + theta * E
    rev_comp = ALPHA * np.log(1 + max(0, t_perf))
    rev_star = BETA * np.sum(current_df['F_i'] * current_df['x_i'])
    rev_media = THETA * E_MEDIA

    r_total = rev_comp + rev_star + rev_media

    # 2. 成本计算 (含随机薪资波动)
    fluctuation = np.random.uniform(0.90, 1.25)
    total_salary = SALARY_CAP * fluctuation

    tax = 0
    if total_salary > SALARY_CAP:
        tax = (total_salary - SALARY_CAP) * TAX_RATE

    total_cost = total_salary + tax + 50.0  # Ops Cost

    # 3. 净利润
    profit = r_total - total_cost

    return profit, r_total, total_salary, tax


def calculate_franchise_value_refined(current_df, r_total):
    """
    🔥 核心修改：使用新的 Franchise Value 公式
    Vt = m * (R_total + R_playoff) + P_brand
    """
    # 1. 获取竞技指标
    _, wins, rounds = get_performance_metrics(current_df)

    # 2. 计算 R_playoff (季后赛额外收入)
    # 公式: 5 * (Wins - 42) + 20 * Rounds
    # 注意：如果胜场少于42，第一项为0 (不扣钱，只算增量)
    win_bonus = 5.0 * max(0, wins - 42.0)
    round_bonus = 20.0 * rounds
    r_playoff = win_bonus + round_bonus

    # 3. 计算 P_brand (品牌溢价)
    # 公式: 500 + 50 * N_stars + 10 * Jersey_Index

    # a. N_stars: 统计 F_i > 阈值的球员
    stars = current_df[current_df['F_i'] >= STAR_THRESHOLD]
    n_stars = len(stars)

    # b. Jersey_Index: 0-10 标准化指数
    # 这里我们假设球衣销量与全队 F_i 总和正相关，最大映射到 10
    total_f = np.sum(current_df['F_i'])
    jersey_index = min(10.0, (total_f / 50.0) * 10.0)  # 假设50是满分基准

    p_brand = BRAND_BASE + (50.0 * n_stars) + (10.0 * jersey_index)

    # 4. 最终估值 V_t
    # Vt = 18 * (R_total + R_playoff) + P_brand
    v_t = VALUATION_M * (r_total + r_playoff) + p_brand

    return v_t, wins, rounds


def apply_aging(df, year):
    """简单的老化模型"""
    df_new = df.copy()
    for i, row in df_new.iterrows():
        age = row['Age'] + year
        # 32岁后下滑，24岁前成长
        decay = 0.05 * (age - 32) if age > 32 else (-0.05 if age < 24 else 0)
        df_new.at[i, 'S_i'] = row['S_i'] * (1 - decay)
        # 假设商业价值 F_i 随年龄略微增长 (积累名气) 但竞技下滑会抵消
        df_new.at[i, 'F_i'] = row['F_i'] * 1.01
    return df_new


# ==========================================
# 4. 模拟流程 (Simulation Process)
# ==========================================
history = {
    'Year': [], 'Profit': [], 'V_Franchise': [],
    'Delta_V': [], 'Discounted_Z': [], 'Cumulative_Z': [],
    'Salary_Paid': [], 'Wins': []
}

# --- 初始状态 (t=0, 用于计算第一年的 Delta) ---
# 计算初始估值 V_0
profit_init, r_total_init, _, _ = calculate_revenue_profit(df_roster)
v_prev, _, _ = calculate_franchise_value_refined(df_roster, r_total_init)

cumulative_z = 0
current_roster = df_roster.copy()

print(f"=== Lakers Strategy Simulation (New Valuation Model) ===\n")
print(f"Initial Franchise Value: ${v_prev:,.1f} M\n")

for t in range(T_YEARS):
    # 1. 球员老化 (Aging)
    roster_t = apply_aging(current_roster, t)

    # 2. 计算利润 (Pi_t) 和 常规赛收入 (R_total)
    profit_t, r_total_t, actual_salary, tax_paid = calculate_revenue_profit(roster_t)

    # 3. 计算新估值 (V_t) - 使用新公式
    v_t, wins_t, rounds_t = calculate_franchise_value_refined(roster_t, r_total_t)

    # 4. 计算估值增量 (Delta V)
    delta_v = v_t - v_prev

    # 5. 目标函数 Z 贡献
    z_term = W1 * profit_t + W2 * delta_v
    discounted_z = (GAMMA ** t) * z_term
    cumulative_z += discounted_z

    # 记录数据
    history['Year'].append(t + 1)
    history['Profit'].append(profit_t)
    history['V_Franchise'].append(v_t)
    history['Delta_V'].append(delta_v)
    history['Discounted_Z'].append(discounted_z)
    history['Cumulative_Z'].append(cumulative_z)
    history['Salary_Paid'].append(actual_salary)
    history['Wins'].append(wins_t)

    # 更新上一期估值
    v_prev = v_t

    # 打印日志
    print(f"Year {t + 1}: Wins={wins_t:.1f} (Rounds={rounds_t}) | Profit=${profit_t:.0f}M")
    print(f"        Valuation=${v_t:,.0f}M (Delta=${delta_v:,.0f}M) -> Z_contrib=${discounted_z:.1f}")

# ==========================================
# 5. 可视化 (Visualization)
# ==========================================
plt.rcParams['font.sans-serif'] = ['Arial', 'SimHei', 'sans-serif']  # 尝试兼容中文
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('ggplot')

# 湖人配色
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'
LINE_RED = '#FF0000'
LINE_BLACK = '#000000'

df_res = pd.DataFrame(history)

fig, ax1 = plt.subplots(figsize=(12, 7))

width = 0.35
x = df_res['Year']

# 柱状图：利润 vs 估值增量
p1 = ax1.bar(x - width / 2, df_res['Profit'] * W1, width,
             label=r'Profit Component ($w_1 \Pi_t$)',
             color=LAKERS_GOLD, alpha=0.9, edgecolor='gray')

p2 = ax1.bar(x + width / 2, df_res['Delta_V'] * W2, width,
             label=r'Valuation Component ($w_2 \Delta V_t$)',
             color=LAKERS_PURPLE, alpha=0.85, edgecolor='gray')

# 折线图：薪资超帽情况
ax1.plot(x, (df_res['Salary_Paid'] - SALARY_CAP),
         color=LINE_RED, linestyle=':', marker='x', linewidth=2,
         label='Salary Cap Overdraft')

ax1.set_xlabel('Simulation Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Weighted Contribution ($M)', fontweight='bold', fontsize=12)
ax1.set_title(
    f'Lakers Strategy Optimization: Profit vs Valuation Growth\n(Model: V = 18*(R_tot + R_playoff) + P_brand)',
    fontsize=14, fontweight='bold')
ax1.axhline(0, color='gray', linewidth=1)

legend = ax1.legend(loc='upper left', frameon=True, facecolor='white')

# 右轴：累计 Z 值
ax2 = ax1.twinx()
ax2.plot(x, df_res['Cumulative_Z'],
         color=LINE_BLACK, marker='D', markersize=6,
         linewidth=2.5, linestyle='-',
         label='Cumulative Z Value')

ax2.set_ylabel('Cumulative Objective Z', color=LINE_BLACK, fontweight='bold', fontsize=12)
ax2.legend(loc='lower right')

plt.tight_layout()
plt.show()

print(fr"\nFinal Result: 5-Year Cumulative Z = {cumulative_z:,.2f}")