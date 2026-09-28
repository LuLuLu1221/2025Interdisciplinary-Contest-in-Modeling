import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import os
import glob
import warnings
import time

# 忽略警告
warnings.filterwarnings('ignore')

# ==========================================
# 1. 配置区域 (模型参数调整)
# ==========================================

DATA_ROOT_FOLDER = r"C:\Users\28137\Desktop\球员数据"  # 文件夹名保持不变（若为英文可改为'Player_Data'）

# --- 风险模型参数 ---
BETA_0 = -6.0
BETA_AGE = 0.12
BETA_HIST = 3.0

# --- 字段映射（修改为纯英文，直接匹配数据中的英文表头）---
COLUMN_MAPPING = {
    'Player_Name': 'Player',
    'Season': 'Season',
    'Age': 'Age',
    'G': 'G',
    'MP': 'MP',  # 原“出场时间”改为英文MP
    'PTS': 'PTS',
    'ThreeP_pct': '3P%',  # 匹配数据中的三分命中率列名（如3P%）
    'OWS': 'OWS',
    'OBPM': 'OBPM',
    'PER': 'PER',
    'TS_pct': 'TS%',  # 匹配真实命中率列名
    'TOV_pct': 'TOV%',  # 匹配失误率列名
    'USG_pct': 'USG%',  # 匹配球权使用率列名
    'AST_pct': 'AST%',  # 匹配助攻率列名
    'ORB_pct': 'ORB%',  # 匹配进攻篮板率列名
    'DWS': 'DWS',
    'DBPM': 'DBPM',
    'DRB_pct': 'DRB%',  # 匹配防守篮板率列名
    'STL_pct': 'STL%',  # 匹配抢断率列名
    'BLK_pct': 'BLK%',  # 匹配盖帽率列名
    'Off_PM': 'Off_PM',
    'Def_PM': 'Def_PM',
    'Trans_Score': 'Trans_Score',
    'Diff_pct': 'Diff%',
    'Rot_Score': 'Rot_Score',
    'Clutch_Points': 'Clutch'
}


# ==========================================
# 2. 核心逻辑：区分“菜”与“伤”
# ==========================================
def calculate_history_stats(df_player):
    try:
        # 直接处理英文列名（无需中文转换）
        df_player['Age'] = pd.to_numeric(df_player['Age'], errors='coerce')
        df_player['G'] = pd.to_numeric(df_player['G'], errors='coerce').fillna(0)
        df_player['MP'] = pd.to_numeric(df_player['MP'], errors='coerce').fillna(20)  # 直接用MP列

        valid_seasons = df_player[df_player['Season'].astype(str).str.contains('-', na=False)].copy()

        if valid_seasons.empty:
            return 1.0, 0.0, df_player.iloc[-1].to_dict()

        valid_seasons = valid_seasons.sort_values(by='Season')
        valid_seasons = valid_seasons.drop_duplicates(subset=['Season'], keep='last')

        current_stats = valid_seasons.iloc[-1].to_dict()
        current_age = current_stats.get('Age', 25)
        if pd.isna(current_age): current_age = 25

        weights = [0.5, 0.3, 0.2]
        attendance_scores = []
        recent_years = valid_seasons.tail(3).iloc[::-1]

        for i, (_, row) in enumerate(recent_years.iterrows()):
            games = row['G']
            minutes = row['MP']

            if minutes < 15:
                rate = 1.0
            else:
                rate = min(games / 78.0, 1.0)

            attendance_scores.append(rate * weights[i])

        current_weight_sum = sum(weights[:len(attendance_scores)])
        missing_weight = 1.0 - current_weight_sum
        phi = sum(attendance_scores) + (missing_weight * 0.98)

        history_factor = 1.0 - phi
        z = BETA_0 + (BETA_AGE * current_age) + (BETA_HIST * history_factor)
        p_risk = 1 / (1 + np.exp(-z))

        return phi, p_risk, current_stats

    except Exception as e:
        return 1.0, 0.0, df_player.iloc[-1].to_dict()


# ==========================================
# 3. 数据读取（终极兼容：HTML伪装xls + 真实xls/xlsx + 纯英文表头）
# ==========================================
def load_all_players_data(root_path):
    all_records = []
    print(f"📂 Scanning: {root_path} ...")
    if not os.path.exists(root_path):
        print(f"❌ Error: Folder '{root_path}' not found")
        return pd.DataFrame()

    subfolders = [f.path for f in os.scandir(root_path) if f.is_dir()]
    for folder in subfolders:
        player_name = os.path.basename(folder)
        excel_files = glob.glob(os.path.join(folder, "*.xls*"))  # 匹配xls/xlsx/伪装xls的html
        if not excel_files:
            print(f"⚠️ No data files found for player: {player_name}")
            continue

        df_history = pd.DataFrame()
        for file in excel_files:
            temp = pd.DataFrame()
            try:
                # 第一步：优先尝试HTML解析（适配99%的伪装xls格式）
                dfs = pd.read_html(file)
                temp = dfs[0] if dfs and not dfs[0].empty else pd.DataFrame()
                print(f"✅ Read as HTML: {os.path.basename(file)}")
            except Exception as e1:
                # HTML解析失败，第二步：尝试Excel引擎解析（适配真实xls/xlsx）
                try:
                    if file.endswith('.xls'):
                        temp = pd.read_excel(file, engine='xlrd')
                    else:
                        temp = pd.read_excel(file, engine='openpyxl')
                    print(f"✅ Read as Excel: {os.path.basename(file)}")
                except Exception as e2:
                    print(f"⚠️ Skip file {os.path.basename(file)}: HTML/Excel parse all failed - {str(e2)[:50]}")
                    continue

            if temp.empty:
                continue

            # 自动识别英文表头，清洗无效行（纯英文表头适配）
            if 'Season' in temp.columns:
                df_history = pd.concat([df_history, temp], ignore_index=True)
            else:
                # 兼容表头在第一行的情况，重新识别
                for i in range(min(3, len(temp))):
                    row_vals = temp.iloc[i].astype(str).tolist()
                    if 'Season' in row_vals or 'Age' in row_vals:
                        temp.columns = row_vals
                        temp = temp[i + 1:].reset_index(drop=True)
                        df_history = pd.concat([df_history, temp], ignore_index=True)
                        break

        if df_history.empty:
            print(f"⚠️ No valid data for player: {player_name}")
            continue

        # 调用核心逻辑计算球员数据
        phi, risk, stats = calculate_history_stats(df_history)
        record = {'Player': player_name}
        record.update(stats)
        record['Phi'] = phi
        record['P_risk'] = risk
        all_records.append(record)
        print(f"📌 Processed player: {player_name} (valid seasons: {len(df_history)})")

    # 统计最终有效数据
    final_df = pd.DataFrame(all_records)
    print(fr"\n📊 Scan completed: Total valid players - {len(final_df)}")
    return final_df


# ==========================================
# 4. 数据标准化
# ==========================================
def standardize_score(series, is_negative_metric=False):
    s = pd.to_numeric(series, errors='coerce')
    if s.isnull().all(): return pd.Series([5.0] * len(s), index=s.index)

    s = s.fillna(s.mean())

    sigma = s.std()
    if pd.isna(sigma) or sigma == 0: return pd.Series([5.0] * len(s), index=s.index)

    z = (s - s.mean()) / sigma
    scores = 5 + 2.0 * z
    scores = scores.clip(0, 10)
    if is_negative_metric: scores = 10 - scores
    return scores


# ==========================================
# 5. 模型计算
# ==========================================
def calculate_von(df_raw):
    df = pd.DataFrame()
    df['Player'] = df_raw['Player']

    # 直接匹配英文列名（无需中文映射）
    for key, col_name in COLUMN_MAPPING.items():
        if key in ['Player_Name', 'Season', 'Age', 'G', 'MP']: continue
        df[key] = df_raw.get(col_name, 0)  # 用COLUMN_MAPPING中的英文列名匹配

    df['Phi'] = df_raw.get('Phi', 1.0)
    df['P_risk'] = df_raw.get('P_risk', 0.0)

    # --- 标准化（直接用英文列名）---
    df['S_OWS'] = standardize_score(df.get('OWS', 0))
    df['S_OBPM'] = standardize_score(df.get('OBPM', 0))
    df['S_TS'] = standardize_score(df.get('TS_pct', 0))
    df['S_PER'] = standardize_score(df.get('PER', 0))
    df['S_TOV'] = standardize_score(df.get('TOV_pct', 0), True)
    df['S_USG'] = standardize_score(df.get('USG_pct', 0))
    df['S_3P'] = standardize_score(df.get('ThreeP_pct', 0))
    df['S_AST'] = standardize_score(df.get('AST_pct', 0))
    df['S_PTS'] = standardize_score(df.get('PTS', 0))

    df['S_DWS'] = standardize_score(df.get('DWS', 0))
    df['S_DBPM'] = standardize_score(df.get('DBPM', 0))
    df['S_STL'] = standardize_score(df.get('STL_pct', 0))
    df['S_BLK'] = standardize_score(df.get('BLK_pct', 0))
    df['S_DRB'] = standardize_score(df.get('DRB_pct', 0))
    df['S_Diff'] = standardize_score(df.get('Diff_pct', 0), True)
    df['S_DefPM'] = standardize_score(df.get('Def_PM', 0))

    # --- 权重计算 ---
    v_core = 0.70 * df['S_OWS'] + 0.30 * df['S_OBPM']
    v_vol = 0.35 * df['S_USG'] + 0.45 * df['S_PTS'] + 0.20 * df['S_AST']
    v_eff = 0.3 * df['S_PER'] + 0.25 * df['S_TS'] + 0.25 * df['S_3P'] + 0.2 * df['S_TOV']

    df['V_off'] = 0.35 * v_core + 0.35 * v_vol + 0.25 * v_eff + 0.05 * standardize_score(df.get('Trans_Score', 0))

    v_core_def = 0.65 * df['S_DWS'] + 0.35 * df['S_DBPM']
    v_prod = 0.4 * df['S_DRB'] + 0.3 * df['S_STL'] + 0.3 * df['S_BLK']
    v_indiv = 0.6 * df['S_Diff'] + 0.4 * df['S_DefPM']
    df['V_def'] = 0.40 * v_core_def + 0.30 * v_prod + 0.25 * v_indiv + 0.05 * standardize_score(df.get('Rot_Score', 0))

    # --- 最终价值计算 ---
    base_val = 0.65 * df['V_off'] + 0.35 * df['V_def']
    risk_penalty_factor = 0.25
    phi_factor = 0.8 + 0.2 * df['Phi'].fillna(1.0)

    df['Von'] = base_val * phi_factor * (1 - risk_penalty_factor * df['P_risk'].fillna(0))

    return df


# ==========================================
# 6. 主程序（修改为输出全部排名）
# ==========================================
if __name__ == "__main__":
    df_raw = load_all_players_data(DATA_ROOT_FOLDER)

    if not df_raw.empty:
        print("⚡ Calculating optimized model...")
        final_df = calculate_von(df_raw)
        final_df = final_df.sort_values(by='Von', ascending=False)  # 按价值降序排序

        # 核心修改：移除.head(10)，输出所有球员
        cols = ['Player', 'Von', 'V_off', 'V_def', 'S_PTS', 'P_risk']
        print("\n=== Complete Player Ranking (All Players) ===")
        pd.set_option('display.float_format', lambda x: '%.3f' % x)
        print(final_df[cols].to_string(index=False))  # 输出全部数据，无索引

        # 保存结果（包含全部球员）
        try:
            final_df.to_excel('Player_Ranking_Complete.xlsx', index=False)
            print("\n📄 Complete results saved to Player_Ranking_Complete.xlsx")
        except Exception as e:
            print(f"⚠️ Save error: {e}")

        # 绘图（保持不变）
        try:
            plot_df = final_df.copy().replace([np.inf, -np.inf], np.nan).dropna(subset=['V_off', 'V_def', 'Von'])

            plt.figure(figsize=(14, 9))
            plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'sans-serif']
            plt.rcParams['axes.unicode_minus'] = False

            cmap = plt.get_cmap('viridis')
            norm = plt.Normalize(vmin=plot_df['Von'].min(), vmax=plot_df['Von'].max())
            sizes = (plot_df['Von'] - plot_df['Von'].min() + 1) * 100

            scatter = plt.scatter(plot_df['V_off'], plot_df['V_def'],
                                  c=plot_df['Von'], cmap=cmap, norm=norm,
                                  s=sizes, alpha=0.9, edgecolors='gray', linewidth=0.5)

            plt.colorbar(scatter, label='Player Value ($V_{on}$)')
            plt.xlabel('Offensive Value ($V_{off}$)', fontsize=12)
            plt.ylabel('Defensive Value ($V_{def}$)', fontsize=12)
            plt.title('NBA Player Valuation Matrix (Risk Adjusted & Optimized)', fontsize=14)
            plt.grid(True, linestyle='--', alpha=0.3)

            # 标注所有球员名
            for idx, row in plot_df.iterrows():
                plt.text(row['V_off'], row['V_def'], row['Player'],
                         ha='center', va='center', fontsize=9,
                         color='black', fontweight='bold')

            plt.savefig('Player_Chart_All.png', dpi=300, bbox_inches='tight')
            print("📊 Chart (all players) generated: Player_Chart_All.png")
            plt.show()

        except Exception as e:
            print(f"Plotting Error: {e}")
    else:
        print("No data found.")