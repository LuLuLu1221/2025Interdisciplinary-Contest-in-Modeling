import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import os
import glob
import sys
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)


# ==========================================
# 1. 全局配置 (Lakers Edition)
# ==========================================
class Config:
    # 路径配置
    PATH_CURRENT_ROSTER = r"C:\Users\28137\Desktop\球员数据"
    PATH_TRADE_TARGETS = r"C:\Users\28137\Desktop\交易决策"
    PATH_LEAGUE_BASIC = r"C:\Users\28137\Desktop\球队数据\全联盟场均.xlsx"
    PATH_LEAGUE_ADV = r"C:\Users\28137\Desktop\球队数据\全联盟球队高阶数据.xlsx"

    MY_TEAM_NAME = "Lakers"

    # 激进策略
    # OUTGOING_PLAYERS = ["Vanderbilt", "Vincent", "Knecht","Kleber","Hachimura"]
    # INCOMING_PLAYERS = ["Siakam", "Nesmith"]

    # 保守策略
    OUTGOING_PLAYERS = ["Vanderbilt", "Vincent", "Knecht"]
    INCOMING_PLAYERS = ["Dillion", "Kessler"]

    # 🎨 配色方案
    COLOR_LAKERS_PURPLE = '#552583'  # 交易前
    COLOR_LAKERS_GOLD = '#FDB927'  # 交易后
    COLOR_LEAGUE_AVG = '#AAAAAA'  # 联盟平均 (灰色)


# ==========================================
# 2. 智能读取模块
# ==========================================
def smart_read_player_file(file_path):
    df = pd.DataFrame()
    try:
        dfs = pd.read_html(file_path)
        if dfs: df = dfs[0]
    except:
        try:
            df = pd.read_excel(file_path)
        except:
            return pd.DataFrame()

    if df.empty: return df

    header_idx = -1
    for i in range(min(5, len(df))):
        row_str = df.iloc[i].astype(str).tolist()
        if 'Season' in row_str and ('PTS' in row_str or 'Tm' in row_str):
            header_idx = i
            break

    if header_idx != -1:
        df.columns = df.iloc[header_idx]
        df = df[header_idx + 1:].reset_index(drop=True)

    df.columns = [str(c).strip() for c in df.columns]
    return df


def process_player_data(root_path, tag):
    all_data = []
    if not os.path.exists(root_path): return pd.DataFrame()

    print(f"📂 [{tag}] 正在读取...", end=" ")
    folders = [f.path for f in os.scandir(root_path) if f.is_dir()]

    for folder in folders:
        name = os.path.basename(folder)

        # === 🔥 核心改动：名单过滤逻辑 ===
        # 如果是读“新援”，必须在 Config.INCOMING_PLAYERS 名单里才读
        if tag == "新援":
            # 检查名字是否在名单里 (模糊匹配，忽略大小写)
            is_wanted = False
            for target in Config.INCOMING_PLAYERS:
                if target.lower() in name.lower():
                    is_wanted = True
                    break
            if not is_wanted:
                continue  # 跳过这个人，不读
        # ================================

        files = glob.glob(os.path.join(folder, "*.xls*"))

        df_player = pd.DataFrame()
        for f in files:
            temp = smart_read_player_file(f)
            if not temp.empty:
                df_player = pd.concat([df_player, temp], ignore_index=True)

        if not df_player.empty:
            # 清洗
            if 'Season' in df_player.columns:
                df_player = df_player.dropna(subset=['Season'])
            if 'PTS' in df_player.columns:
                df_player = df_player[pd.to_numeric(df_player['PTS'], errors='coerce').notna()]
            df_player = df_player[df_player['Season'] != 'Season']

            if df_player.empty: continue

            last = df_player.iloc[-1].to_dict()
            last['Player'] = name

            cols_to_fix = ['MP', 'PTS', 'TRB', 'AST', 'STL', 'BLK', 'ORtg', 'DRtg', 'Pace', 'TS%']
            for col in cols_to_fix:
                if col in last:
                    try:
                        last[col] = float(last[col])
                    except:
                        last[col] = 0.0

            if last.get('MP', 0) == 0: last['MP'] = 15.0
            all_data.append(last)

    print(f"成功加载 {len(all_data)} 人")
    return pd.DataFrame(all_data)


# ==========================================
# 3. 球队数据加载
# ==========================================
def load_team_data():
    try:
        df_b = pd.read_excel(Config.PATH_LEAGUE_BASIC)
        df_a = pd.read_excel(Config.PATH_LEAGUE_ADV, header=1)
        for d in [df_b, df_a]:
            d.columns = [str(c).strip() for c in d.columns]
            rename_map = {k: 'Team' for k in ['Tm', '球队'] if k in d.columns}
            d.rename(columns=rename_map, inplace=True)
            d['Team'] = d['Team'].astype(str).str.replace('*', '').str.strip()
        return pd.merge(df_b, df_a, on='Team', suffixes=('_b', '_a'))
    except:
        return pd.DataFrame()


# ==========================================
# 4. 交易计算引擎
# ==========================================
def run_simulation(team_df, current_df, new_df):
    print("\n🔄 开始计算...")

    metrics = ['ORtg', 'DRtg', 'TS%', 'AST', 'TRB', 'STL', 'BLK', 'Pace']

    # 1. 联盟平均
    league_avgs = {}
    print("📊 计算联盟平均水平...")
    for m in metrics:
        cols = [c for c in team_df.columns if c == m or c == f"{m}_a" or c == f"{m}_b"]
        if cols:
            league_avgs[m] = team_df[cols[0]].mean(skipna=True)
        else:
            league_avgs[m] = 0.0

    # 2. 主队
    my_team = team_df[team_df['Team'].str.contains(Config.MY_TEAM_NAME, case=False)]
    if my_team.empty:
        print(f"❌ 找不到球队: {Config.MY_TEAM_NAME}")
        return None, None, None

    base_stats = {}
    for m in metrics:
        col = next((c for c in team_df.columns if c == m or c == f"{m}_a" or c == f"{m}_b"), None)
        base_stats[m] = float(my_team[col].values[0]) if col else 0.0

    # 3. 计算变化
    delta = {k: 0.0 for k in metrics}

    def calc(df_p, sign):
        for _, p in df_p.iterrows():
            mp = p.get('MP', 15.0)
            wt = mp / 240.0

            p_ortg = p.get('ORtg', 0)
            if p_ortg == 0: p_ortg = 105 + (p.get('PTS', 10) - 10) * 1.2
            p_drtg = p.get('DRtg', 0)
            if p_drtg == 0: p_drtg = 112 - (p.get('STL', 0.7) * 2 + p.get('BLK', 0.5) * 1.5)

            delta['ORtg'] += (p_ortg - base_stats['ORtg']) * wt * sign
            delta['DRtg'] += (p_drtg - base_stats['DRtg']) * wt * sign
            delta['AST'] += (p.get('AST', 0) * 5 - base_stats['AST']) * wt * sign * 0.2
            delta['TRB'] += (p.get('TRB', 0) * 5 - base_stats['TRB']) * wt * sign * 0.2
            delta['STL'] += (p.get('STL', 0) * 5 - base_stats['STL']) * wt * sign
            delta['BLK'] += (p.get('BLK', 0) * 5 - base_stats['BLK']) * wt * sign
            delta['Pace'] += (p.get('Pace', 99) - base_stats['Pace']) * wt * sign
            delta['TS%'] += (p.get('TS%', 0.57) - base_stats['TS%']) * wt * sign

    out_names = Config.OUTGOING_PLAYERS
    out_df = pd.DataFrame()
    for n in out_names:
        found = current_df[current_df['Player'].str.contains(n, case=False)]
        if not found.empty: out_df = pd.concat([out_df, found.iloc[[0]]])

    if not out_df.empty: calc(out_df, -1)
    if not new_df.empty: calc(new_df, 1)

    final_stats = {k: base_stats[k] + delta[k] for k in metrics}
    return base_stats, final_stats, league_avgs


# ==========================================
# 5. 绘图 (Lakers Professional Style)
# ==========================================
def plot_radar(before, after, league):
    # 设置绘图风格
    plt.style.use('bmh')  # 使用基础网格背景
    labels = list(before.keys())
    num_vars = len(labels)

    # 数据转换与归一化逻辑
    def normalize(stats):
        vals = []
        for k, v in stats.items():
            avg = league.get(k, 1.0)
            if avg == 0: avg = 1.0
            ratio = v / avg
            # DRtg(防守效率)越低越好，进行反向处理
            if k == 'DRtg': ratio = 2 - ratio
            s = 50 + (ratio - 1.0) * 150
            vals.append(np.clip(s, 10, 100))
        return vals

    v_league = [50] * num_vars
    v_before = normalize(before)
    v_after = normalize(after)

    # 闭合曲线
    angles = np.linspace(0, 2 * pi, num_vars, endpoint=False).tolist()
    v_league += v_league[:1]
    v_before += v_before[:1]
    v_after += v_after[:1]
    angles += angles[:1]

    # 创建画布
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

    # 调整雷达图起始方向
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # 1. 绘制联盟平均线 (中性背景)
    ax.plot(angles, v_league, color='#888888', linewidth=1, linestyle='--', label='League Average')
    ax.fill(angles, v_league, color='#888888', alpha=0.05)

    # 2. 绘制交易前状态 (Lakers Purple)
    ax.plot(angles, v_before, color=Config.COLOR_LAKERS_PURPLE, linewidth=2, linestyle='-',
            marker='o', markersize=4, alpha=0.6, label='Current Roster')
    ax.fill(angles, v_before, color=Config.COLOR_LAKERS_PURPLE, alpha=0.1)

    # 3. 绘制交易后状态 (Lakers Gold - 核心视觉)
    ax.plot(angles, v_after, color=Config.COLOR_LAKERS_GOLD, linewidth=4,
            marker='s', markersize=6, label='Projected Post-Trade', zorder=5)
    ax.fill(angles, v_after, color=Config.COLOR_LAKERS_GOLD, alpha=0.4, zorder=4)

    # 4. 美化坐标轴
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=12, weight='bold', color='#333333')

    # 设置圈层标记
    ax.set_ylim(0, 110)
    ax.set_yticks([20, 50, 80, 100])
    ax.set_yticklabels(['Poor', 'Avg', 'Elite', 'Peak'], color='gray', size=8)
    ax.grid(color='#DDDDDD', linestyle='--', alpha=0.7)

    # 5. 添加数据提升标注 (Data Delta)
    for i, label in enumerate(labels):
        diff = after[label] - before[label]
        color = 'green' if diff > 0 else 'red'
        if label == 'DRtg': color = 'green' if diff < 0 else 'red'  # 防守端反向判断

        # 计算文字标注位置
        angle_rad = angles[i]
        ax.text(angle_rad, v_after[i] + 8, f"{diff:+.1f}",
                color=color, weight='bold', size=10, ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.6, edgecolor='none', pad=1))

    # 6. 标题与图例
    trade_summary = f"Adding: {', '.join(Config.INCOMING_PLAYERS)}"
    plt.suptitle(f"LAKERS TRADE SIMULATION REPORT", size=20, weight='black', color=Config.COLOR_LAKERS_PURPLE, y=0.98)
    plt.title(trade_summary, size=12, color='#666666', pad=30)

    # 底部图例美化
    legend = ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.15),
                       ncol=3, frameon=True, shadow=True, fontsize=10)
    legend.get_frame().set_edgecolor('#DDDDDD')

    # 7. 控制台输出
    print(f"\n{'=' * 50}")
    print(f"{'METRIC':<10} {'BEFORE':<10} {'AFTER':<10} {'CHANGE'}")
    print(f"{'-' * 50}")
    for k in labels:
        print(f"{k:<10} {before[k]:<10.1f} {after[k]:<10.1f} {after[k] - before[k]:>+8.2f}")
    print(f"{'=' * 50}")

    plt.tight_layout()
    plt.savefig('Lakers_Professional_Analysis.png', dpi=300, bbox_inches='tight')
    print("\n✅ 已生成高清专业图表: Lakers_Professional_Analysis.png")
    plt.show()


if __name__ == "__main__":
    t = load_team_data()
    c = process_player_data(Config.PATH_CURRENT_ROSTER, "现役")
    # 这一步现在会根据 INCOMING_PLAYERS 过滤
    n = process_player_data(Config.PATH_TRADE_TARGETS, "新援")

    if not t.empty and not c.empty:
        b, a, l = run_simulation(t, c, n)
        if b and a and l: plot_radar(b, a, l)