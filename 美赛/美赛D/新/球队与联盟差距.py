import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
from scipy import stats
import os


# ==========================================
# 1. Configuration (Absolute Paths)
# ==========================================
class Config:
    FILE_BASIC = r"C:\Users\28137\Desktop\球队数据\全联盟场均.xlsx"
    FILE_ADV = r"C:\Users\28137\Desktop\球队数据\全联盟球队高阶数据.xlsx"

    # 维度配置
    METRICS_CONFIG = {
        'ORtg': {'label': 'OFF RATING\n(Efficiency)', 'weight': 0.15, 'reverse': False},
        'DRtg': {'label': 'DEF RATING\n(Stops/100)', 'weight': 0.15, 'reverse': True},
        'TS%': {'label': 'TRUE SHOOTING\n(Shot Quality)', 'weight': 0.12, 'reverse': False},
        'AST': {'label': 'PLAYMAKING\n(AST)', 'weight': 0.12, 'reverse': False},
        'TRB': {'label': 'REBOUNDING\n(TRB)', 'weight': 0.12, 'reverse': False},
        'STL': {'label': 'PRESSURE\n(STL)', 'weight': 0.11, 'reverse': False},
        'BLK': {'label': 'RIM PROTECT\n(BLK)', 'weight': 0.11, 'reverse': False},
        'Pace': {'label': 'PACE\n(Tempo)', 'weight': 0.12, 'reverse': False}
    }

    PLOT_CONFIG = {
        'figsize': (16, 16),  # 进一步加大画布尺寸
        'dpi': 150,
        'team_colors': {'Lakers': ('#552583', '#FDB927')},
        'save_path': r"C:\Users\28137\Desktop\Lakers_Octagon_Analysis_Clean.png"
    }


# ==========================================
# 2. Data Loading
# ==========================================
def smart_load_data(basic_path, adv_path):
    print(f"Loading data...")
    try:
        df_basic = pd.read_excel(basic_path)
        df_adv = pd.read_excel(adv_path, header=1)
    except Exception as e:
        print(f"Error: {e}")
        return None

    for df in [df_basic, df_adv]:
        df.columns = [str(c).strip() for c in df.columns]
        if 'Team' in df.columns:
            df.drop(df[df['Team'] == 'League Average'].index, inplace=True)

    df_combined = pd.merge(df_basic, df_adv, on='Team', how='inner', suffixes=('_basic', '_adv'))

    for metric in Config.METRICS_CONFIG.keys():
        cols = [metric, f'{metric}_basic', f'{metric}_adv']
        for c in cols:
            if c in df_combined.columns:
                df_combined[c] = pd.to_numeric(df_combined[c], errors='coerce')
    return df_combined


# ==========================================
# 3. Algorithm: MAD Robust Z-Score
# ==========================================
def analyze_octagon(df, target_keyword):
    target_mask = df['Team'].str.contains(target_keyword, case=False, na=False)
    if not target_mask.any(): return None, None, None

    team_data = df[target_mask].iloc[0]
    team_name = team_data['Team']

    results = {}
    raw_values = {}

    for metric, config in Config.METRICS_CONFIG.items():
        col_candidates = [metric, f'{metric}_basic', f'{metric}_adv']
        actual_col = next((c for c in col_candidates if c in df.columns), None)
        if not actual_col: continue

        data_series = df[actual_col].dropna()
        team_val = team_data[actual_col]
        median = data_series.median()
        mad = stats.median_abs_deviation(data_series, scale='normal')

        mad_z = 0 if mad == 0 else (team_val - median) / mad
        if config['reverse']: mad_z = -mad_z

        results[config['label']] = mad_z
        raw_values[config['label']] = team_val

    return results, raw_values, team_name


# ==========================================
# 4. Visualization (Anti-Crowding Logic)
# ==========================================
def plot_octagon(results, raw_values, team_name):
    plt.rcParams['font.family'] = 'sans-serif'

    labels = list(results.keys())
    values = list(results.values())
    raws = list(raw_values.values())
    N = len(labels)

    values_plot = values + [values[0]]
    angles = [n / float(N) * 2 * pi for n in range(N)]
    angles += angles[:1]

    # 1. 加大画布
    fig = plt.figure(figsize=Config.PLOT_CONFIG['figsize'], dpi=Config.PLOT_CONFIG['dpi'], facecolor='white')
    ax = plt.subplot(111, polar=True)
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    purple, gold = Config.PLOT_CONFIG['team_colors']['Lakers']

    # 2. 绘制主图
    ax.plot(angles, values_plot, linewidth=3, linestyle='solid', color=purple, label=f'{team_name}')
    ax.fill(angles, values_plot, purple, alpha=0.2)

    # 3. 绘制阈值线
    ax.plot(angles, [0] * len(angles), linewidth=1, linestyle='--', color='gray', alpha=0.6)  # Avg
    ax.plot(angles, [-1.0] * len(angles), linewidth=1.5, linestyle=':', color='#D40000')  # Critical
    ax.fill_between(angles, -4.0, -1.0, color='#D40000', alpha=0.05)  # Red Zone

    # 4. 轴标签外推 (pad=45 增加距离)
    plt.xticks(angles[:-1], labels, size=12, fontweight='bold', color='#333333')
    ax.tick_params(axis='x', pad=45)

    # 5. 扩大 Y 轴范围 (核心：给文字留出空间)
    # 范围设为 -3 到 4，这样即使数值很大，也不会顶到最外圈
    plt.ylim(-3.0, 4.0)

    ax.set_rlabel_position(0)
    plt.yticks([-2.0, -1.0, 0, 1.0, 2.0],
               ["CRITICAL", "", "AVG", "", "ELITE"],
               color="grey", size=9, fontweight='bold')
    ax.grid(True, color='#E0E0E0', linestyle='-', linewidth=1)

    # 6. 智能数据标签 (防止遮挡算法)
    for i, (angle, z, val) in enumerate(zip(angles[:-1], values, raws)):
        # 文本内容
        val_text = f"{val:.1f}%" if '%' in labels[i] else f"{val:.1f}"
        full_text = f"{val_text}\n(Z={z:.1f})"

        # 颜色逻辑
        color = purple if z >= -0.5 else '#D40000'

        # 距离逻辑：不管数据点在哪，标签都往外推一点，确保不和线重叠
        # 如果是负值(凹陷)，稍微往里一点；如果是正值(凸起)，往外一点
        # 但为了不挤，统一稍微远离数据点
        radius_offset = 0.8 if z >= 0 else -0.8
        radius = z + radius_offset

        # 角度逻辑 (Alignment)
        deg = np.degrees(angle)
        # 根据象限决定对齐方式
        if np.isclose(deg, 0):
            ha, va = 'center', 'bottom'
        elif 0 < deg < 180:
            ha, va = 'left', 'center'
        elif np.isclose(deg, 180):
            ha, va = 'center', 'top'
        else:
            ha, va = 'right', 'center'

        # 绘制标签 (带白色背景框)
        ax.text(angle, radius, full_text,
                ha=ha, va=va,
                fontsize=11, fontweight='bold', color=color,
                bbox=dict(facecolor='white', alpha=0.95, edgecolor=color, boxstyle='round,pad=0.4'))

    # Title
    plt.title(f'{team_name} Team DNA: PD-RAD Octagon Diagnosis\n(Real Stats | MAD Robust Z-Scores)',
              size=22, color=purple, y=1.1, fontweight='bold')

    # 保存
    try:
        plt.savefig(Config.PLOT_CONFIG['save_path'], bbox_inches='tight')
        print(f"✅ Clean Chart saved to: {Config.PLOT_CONFIG['save_path']}")
    except Exception as e:
        print(f"⚠️ Save Error: {e}")
    plt.show()


# ==========================================
# Main
# ==========================================
if __name__ == "__main__":
    df = smart_load_data(Config.FILE_BASIC, Config.FILE_ADV)
    if df is not None:
        res, raw, name = analyze_octagon(df, "Lakers")
        if res: plot_octagon(res, raw, name)