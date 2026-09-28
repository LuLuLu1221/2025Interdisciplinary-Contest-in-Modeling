import pandas as pd
import numpy as np

# ==========================================
# 1. 输入数据：真实出场时间 (来自你的新图片)
# ==========================================
# 我们直接录入图片中的 Total Minutes 和 Games
minutes_data = [
    {'Player': 'Luka Dončić', 'G': 38, 'Minutes': 1380},
    {'Player': 'Jake LaRavia', 'G': 46, 'Minutes': 1261},
    {'Player': 'Deandre Ayton', 'G': 41, 'Minutes': 1161},
    {'Player': 'Rui Hachimura', 'G': 36, 'Minutes': 1084},
    {'Player': 'Marcus Smart', 'G': 37, 'Minutes': 1056},
    {'Player': 'LeBron James', 'G': 29, 'Minutes': 962},
    {'Player': 'Austin Reaves', 'G': 23, 'Minutes': 812},
    {'Player': 'Jarred Vanderbilt', 'G': 37, 'Minutes': 720},
    {'Player': 'Jaxson Hayes', 'G': 38, 'Minutes': 671},
    {'Player': 'Gabe Vincent', 'G': 26, 'Minutes': 507},
    {'Player': 'Dalton Knecht', 'G': 37, 'Minutes': 458},
    {'Player': 'Nick Smith Jr.', 'G': 23, 'Minutes': 300},
    {'Player': 'Maxi Kleber', 'G': 21, 'Minutes': 239},
    {'Player': 'Bronny James', 'G': 25, 'Minutes': 173},
    {'Player': 'Drew Timme', 'G': 13, 'Minutes': 104},
    {'Player': 'Adou Thiero', 'G': 15, 'Minutes': 87},
    {'Player': 'Kobe Bufkin', 'G': 4, 'Minutes': 45},
    {'Player': 'Chris Mañon', 'G': 4, 'Minutes': 14},
    {'Player': 'Christian Koloko', 'G': 2, 'Minutes': 6}
]
df_minutes = pd.DataFrame(minutes_data)

# 计算场均时间 (MPG)
df_minutes['MPG'] = df_minutes['Minutes'] / df_minutes['G']

# ==========================================
# 2. 输入数据：竞技价值 Von (来自之前的排名)
# ==========================================
von_data = {
    'Player_Key': ['Donkic', 'Reaves', 'Ayton', 'James', 'Hayes', 'Manon', 'LaRavia',
                   'Hachimura', 'Vanderbilt', 'Knecht', 'Timme', 'Thiero', 'Smart',
                   'JrSmith', 'Bronny', 'Vincent', 'Kleber'],
    'Von': [6.573, 5.405, 4.928, 4.898, 4.768, 4.601, 4.509,
            4.185, 4.083, 3.939, 3.907, 3.809, 3.686,
            3.650, 3.625, 3.305, 3.103]
}
df_von = pd.DataFrame(von_data)

# ==========================================
# 3. 数据匹配与合并
# ==========================================

# 建立名字映射字典：{真实名字: Von表中的名字}
name_map = {
    'Luka Dončić': 'Donkic',
    'LeBron James': 'James',
    'Austin Reaves': 'Reaves',
    'Deandre Ayton': 'Ayton',
    'Jake LaRavia': 'LaRavia',
    'Rui Hachimura': 'Hachimura',
    'Marcus Smart': 'Smart',
    'Jarred Vanderbilt': 'Vanderbilt',
    'Jaxson Hayes': 'Hayes',
    'Gabe Vincent': 'Vincent',
    'Dalton Knecht': 'Knecht',
    'Nick Smith Jr.': 'JrSmith',
    'Maxi Kleber': 'Kleber',
    'Bronny James': 'Bronny',
    'Drew Timme': 'Timme',
    'Adou Thiero': 'Thiero',
    'Chris Mañon': 'Manon',
    # 那些没有Von数据的，稍后会填充默认值
    'Kobe Bufkin': 'Bufkin',
    'Christian Koloko': 'Koloko'
}

df_minutes['Player_Key'] = df_minutes['Player'].map(name_map)
df_final = pd.merge(df_minutes, df_von, on='Player_Key', how='left')

# 填充缺失的 Von 值 (对于边缘球员，给一个略低于平均的分数，例如 3.0)
df_final['Von'] = df_final['Von'].fillna(3.0)


# ==========================================
# 4. 计算竞技表现函数 T_perf
# ==========================================

def calculate_t_perf_real(df, lambda_friction=0.012):
    """
    参数:
    lambda_friction: 协同摩擦系数。
    因为这里使用的是真实时间，总权重和会比较大，
    所以 λ 需要比之前设得小一点，防止把战力扣成负数。
    """

    # 1. 计算轮换权重 xi
    # 逻辑：一名球员打满48分钟，权重为1.0。
    # 全队加起来的权重通常在 5.0 左右 (5个位置 * 48分钟)
    df['xi'] = df['MPG'] / 48.0

    # 2. 计算加权单项 (Si * xi)
    df['Weighted_Von'] = df['Von'] * df['xi']

    # 3. 基础累加 (Raw Sum)
    raw_sum = df['Weighted_Von'].sum()

    # 4. 摩擦损耗 (Friction)
    # 公式: λ * (Sum)^2
    friction_loss = lambda_friction * (raw_sum ** 2)

    # 5. 最终战力
    t_perf = raw_sum - friction_loss

    return t_perf, raw_sum, friction_loss, df


# 执行计算
# 我将摩擦系数设为 0.012，这是一个针对 NBA 真实轮换数据比较合理的经验值
final_t_perf, final_raw, final_friction, df_result = calculate_t_perf_real(df_final, lambda_friction=0.012)

# ==========================================
# 5. 打印报告
# ==========================================
print("=" * 60)
print("🏀 球队真实竞技战力报告 (Based on Real Minutes)")
print("=" * 60)
print(f"1. 基础战力总和 (Σ Si*xi): {final_raw:.4f}")
print(f"2. 协同摩擦损耗 (Friction): -{final_friction:.4f} (λ=0.012)")
print("-" * 30)
print(f"🏆 最终竞技表现 (T_perf):   {final_t_perf:.4f}")
print("=" * 60)

print("\n[详细轮换贡献表]")
# 格式化输出
display_cols = ['Player', 'G', 'MPG', 'Von', 'xi', 'Weighted_Von']
df_result = df_result.sort_values(by='Weighted_Von', ascending=False)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
print(df_result[display_cols].to_string(index=False))