import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns  # <--- 关键是这一行，必须是 seaborn as sns
import os
import glob
import warnings

# 忽略警告
warnings.filterwarnings('ignore')

# 忽略警告
warnings.filterwarnings('ignore')

# ==========================================
# 1. 配置区域 (模型参数调整)
# ==========================================

DATA_ROOT_FOLDER = '球员数据'  # 注意：如果你的文件夹名还是中文，请保持这个不变

# --- 风险模型参数 ---
BETA_0 = -6.0
BETA_AGE = 0.12
BETA_HIST = 3.0

# --- 字段映射 ---
COLUMN_MAPPING = {
    'Player_Name': 'Player',
    'Season': 'Season',
    'Age': 'Age',
    'G': 'G',
    'MP': '出场时间',
    'PTS': '得分',
    'ThreeP_pct': '三分球命中率',
    'OWS': '进攻胜利贡献值',
    'OBPM': '进攻正负值',
    'PER': '球员效率值',
    'TS_pct': '真实命中率',
    'TOV_pct': '失误率',
    'USG_pct': '球权使用率',
    'AST_pct': '助攻率',
    'ORB_pct': '进攻篮板率',
    'DWS': '防守胜利贡献值',
    'DBPM': '防守正负值',
    'DRB_pct': '防守篮板率',
    'STL_pct': '抢断率',
    'BLK_pct': '盖帽率',
    'Off_PM': '进攻正负值',
    'Def_PM': '防守正负值',
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
        df_player['Age'] = pd.to_numeric(df_player['Age'], errors='coerce')
        df_player['G'] = pd.to_numeric(df_player['G'], errors='coerce').fillna(0)

        if 'MP' in df_player.columns:
            df_player['MP'] = pd.to_numeric(df_player['MP'], errors='coerce').fillna(20)
        else:
            df_player['MP'] = 20

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
# 3. 数据读取
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
        excel_files = glob.glob(os.path.join(folder, "*.xls*"))
        if not excel_files: continue

        df_history = pd.DataFrame()
        for file in excel_files:
            try:
                try:
                    temp = pd.read_excel(file)
                except:
                    dfs = pd.read_html(file)
                    temp = dfs[0] if dfs else pd.DataFrame()

                if temp.empty: continue

                for i in range(min(5, len(temp))):
                    row_vals = temp.iloc[i].astype(str).tolist()
                    if 'Season' in row_vals or 'Age' in row_vals:
                        temp.columns = row_vals
                        temp = temp[i + 1:]
                        break

                if 'Season' in temp.columns: df_history = temp
            except:
                continue

        if df_history.empty: continue
        phi, risk, stats = calculate_history_stats(df_history)
        record = {'Player': player_name}
        record.update(stats)
        record['Phi'] = phi
        record['P_risk'] = risk
        all_records.append(record)
    return pd.DataFrame(all_records)


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

    for key, col_name in COLUMN_MAPPING.items():
        if key in ['Player_Name', 'Season', 'Age', 'G', 'MP']: continue
        if col_name in df_raw.columns:
            df[key] = df_raw[col_name]
        else:
            df[key] = 0

    df['Phi'] = df_raw.get('Phi', 1.0)
    df['P_risk'] = df_raw.get('P_risk', 0.0)

    # --- Standardize ---
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

    # --- Weights ---
    v_core = 0.70 * df['S_OWS'] + 0.30 * df['S_OBPM']
    v_vol = 0.35 * df['S_USG'] + 0.45 * df['S_PTS'] + 0.20 * df['S_AST']
    v_eff = 0.3 * df['S_PER'] + 0.25 * df['S_TS'] + 0.25 * df['S_3P'] + 0.2 * df['S_TOV']

    df['V_off'] = 0.35 * v_core + 0.35 * v_vol + 0.25 * v_eff + 0.05 * standardize_score(df.get('Trans_Score', 0))

    v_core_def = 0.65 * df['S_DWS'] + 0.35 * df['S_DBPM']
    v_prod = 0.4 * df['S_DRB'] + 0.3 * df['S_STL'] + 0.3 * df['S_BLK']
    v_indiv = 0.6 * df['S_Diff'] + 0.4 * df['S_DefPM']
    df['V_def'] = 0.40 * v_core_def + 0.30 * v_prod + 0.25 * v_indiv + 0.05 * standardize_score(df.get('Rot_Score', 0))

    # --- Final Formula ---
    base_val = 0.65 * df['V_off'] + 0.35 * df['V_def']
    risk_penalty_factor = 0.25
    phi_factor = 0.8 + 0.2 * df['Phi'].fillna(1.0)

    df['Von'] = base_val * phi_factor * (1 - risk_penalty_factor * df['P_risk'].fillna(0))

    return df


# ==========================================
# 6. 主程序 (Main Execution - High-End Visualization)
# ==========================================
if __name__ == "__main__":
    # 1. 加载与计算
    df_raw = load_all_players_data(DATA_ROOT_FOLDER)

    if not df_raw.empty:
        print("⚡ Calculating optimized model...")
        final_df = calculate_von(df_raw)

        # 排序并筛选有效数据
        final_df = final_df.sort_values(by='Von', ascending=False)
        plot_df = final_df.copy().replace([np.inf, -np.inf], np.nan).dropna(subset=['V_off', 'V_def', 'Von'])

        # 控制显示前10名
        cols = ['Player', 'Von', 'V_off', 'V_def', 'S_PTS', 'P_risk']
        print("\n=== Final Ranking (Top 10) ===")
        pd.set_option('display.float_format', lambda x: '%.3f' % x)
        print(final_df[cols].head(10).to_string(index=False))

        # 保存结果
        try:
            final_df.to_excel('Player_Ranking_Optimized.xlsx', index=False)
        except:
            pass

        # ==========================================
        # 2. 高级绘图逻辑 (Professional Visualization)
        # ==========================================
        try:
            # --- 设置画布风格 ---
            # 使用 Seaborn 的 whitegrid 风格，看起来更干净
            sns.set_style("whitegrid")
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Calibri']

            # 创建画布
            fig, ax = plt.subplots(figsize=(16, 10), dpi=300)

            # --- 定义核心数据 ---
            x = plot_df['V_off']
            y = plot_df['V_def']
            c = plot_df['Von']
            s = (plot_df['Von'] - plot_df['Von'].min() + 0.5) ** 2.5 * 8  # 气泡大小指数放大，拉开视觉差距

            # --- 绘制散点 ---
            # 使用 RdYlBu_r 色阶：红色=强，蓝色=弱
            scatter = ax.scatter(x, y, c=c, s=s, cmap='RdYlBu_r',
                                 alpha=0.85, edgecolors='white', linewidth=1.5, zorder=3)

            # --- 添加平均线 (十字准星) ---
            mean_off = x.mean()
            mean_def = y.mean()
            ax.axvline(mean_off, color='#555555', linestyle='--', alpha=0.6, zorder=1)
            ax.axhline(mean_def, color='#555555', linestyle='--', alpha=0.6, zorder=1)

            # --- 添加象限文字背景 ---
            # 这里的坐标是基于标准分大致范围估算的，放在角落
            x_min, x_max = x.min(), x.max()
            y_min, y_max = y.min(), y.max()

            ax.text(x_max, y_max, 'SUPERSTARS\n(Two-Way Elite)', fontsize=16, color='#d62728',
                    alpha=0.15, ha='right', va='top', weight='bold')
            ax.text(x_max, y_min, 'OFFENSIVE\nSPECIALISTS', fontsize=14, color='#ff7f0e',
                    alpha=0.15, ha='right', va='bottom', weight='bold')
            ax.text(x_min, y_max, 'DEFENSIVE\nANCHORS', fontsize=14, color='#1f77b4',
                    alpha=0.15, ha='left', va='top', weight='bold')
            ax.text(x_min, y_min, 'ROTATION\nDEVELOPMENT', fontsize=14, color='gray',
                    alpha=0.15, ha='left', va='bottom', weight='bold')

            # --- 智能标签 (Smart Labeling) ---
            # 策略：只标记 Top 15 的球员，以及在该区域非常突出的极值球员

            # 1. 标记总分前 15 名
            top_players = plot_df.head(15)

            # 2. 标记进攻极值 (进攻分前3但总分不在前15)
            off_outliers = plot_df.sort_values('V_off', ascending=False).head(3)

            # 3. 标记防守极值
            def_outliers = plot_df.sort_values('V_def', ascending=False).head(3)

            # 合并去重
            labels_to_plot = pd.concat([top_players, off_outliers, def_outliers]).drop_duplicates(subset=['Player'])

            from matplotlib.patheffects import withStroke

            texts = []
            for i, row in labels_to_plot.iterrows():
                # 名字加粗，带白色描边防止看不清
                txt = ax.text(row['V_off'], row['V_def'], row['Player'],
                              fontsize=10, weight='bold', color='#333333')
                txt.set_path_effects([withStroke(linewidth=3, foreground='white')])
                texts.append(txt)

            # --- 简单的防重叠逻辑 (手动偏移) ---
            # 如果不想安装 adjustText 库，可以使用这个简单的偏移
            # 这里我们只让它自然显示，Matplotlib 会自动处理一部分

            # --- 装饰图表 ---
            cbar = plt.colorbar(scatter, label='Comprehensive Player Value ($V_{on}$)')
            cbar.set_label('Player Value ($V_{on}$)', size=12, weight='bold')

            ax.set_xlabel('Offensive Impact ($V_{off}$)', fontsize=13, weight='bold')
            ax.set_ylabel('Defensive Impact ($V_{def}$)', fontsize=13, weight='bold')
            ax.set_title('NBA Player Value Matrix: Who are the Real Stars?', fontsize=18, weight='bold', pad=20)

            # 添加网格
            ax.grid(True, linestyle=':', alpha=0.6)

            # 保存并展示
            plt.tight_layout()
            plt.savefig('NBA_Player_Matrix_HD.png', dpi=300)
            print("📊 Chart generated: NBA_Player_Matrix_HD.png (High Definition)")
            plt.show()

        except Exception as e:
            print(f"Plotting Error: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("No data found.")