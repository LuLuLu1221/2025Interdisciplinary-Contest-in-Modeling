import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import glob
import warnings

# Ignore warnings
warnings.filterwarnings('ignore')

# ==========================================
# 1. Configuration
# ==========================================
DATA_ROOT_FOLDER = r"C:\Users\28137\Desktop\球员数据"

# Lakers Colors
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'


# ==========================================
# 2. Data Loading Logic
# ==========================================
def find_header_and_read(file_path):
    try:
        try:
            dfs = pd.read_html(file_path, header=None)
            df = dfs[0]
        except Exception:
            try:
                df = pd.read_excel(file_path, header=None)
            except Exception as e:
                return None

        if df.empty: return None

        header_row_index = -1
        for i in range(min(5, len(df))):
            row_values = df.iloc[i].astype(str).tolist()
            if 'Season' in row_values and 'Age' in row_values:
                header_row_index = i
                break

        if header_row_index == -1: return None

        df.columns = df.iloc[header_row_index]
        df = df[header_row_index + 1:].reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        return df

    except Exception as e:
        return None


def load_all_players_data(root_path):
    all_records = []
    print(f"📂 Scanning folder: {root_path}")

    if not os.path.exists(root_path):
        print("❌ Error: Path does not exist!")
        return pd.DataFrame()

    subfolders = [f.path for f in os.scandir(root_path) if f.is_dir()]

    for folder in subfolders:
        player_name = os.path.basename(folder)
        excel_files = glob.glob(os.path.join(folder, "*.xls*"))
        if not excel_files: continue

        target_file = None
        for f in excel_files:
            if "常规赛" in os.path.basename(f):
                target_file = f
                break
        if not target_file: target_file = excel_files[0]

        df = find_header_and_read(target_file)
        if df is None or df.empty: continue

        try:
            df = df[df['Season'].astype(str).str.contains('-', na=False)]
            if df.empty: continue

            last_row = df.iloc[-1].to_dict()
            record = {'Player': player_name}
            cols_to_extract = ['PTS', 'TRB', 'AST', 'MP', 'Age', 'PER', 'STL', 'BLK']

            for col in cols_to_extract:
                val = last_row.get(col, 0)
                val = pd.to_numeric(val, errors='coerce')
                if pd.isna(val): val = 0
                record[col] = val

            # Fair Risk Calculation
            age = record.get('Age', 25)
            risk = 0.10 + max(0, (age - 25) * 0.015)
            record['Risk_Factor'] = min(risk, 0.40)

            all_records.append(record)

        except Exception as e:
            continue

    return pd.DataFrame(all_records)


# ==========================================
# 3. Calculation & Visualization (Stacked Bar)
# ==========================================
def standardize(series):
    s = pd.to_numeric(series, errors='coerce').fillna(0)
    if s.std() == 0: return pd.Series([5.0] * len(s), index=s.index)
    return (5 + 2 * (s - s.mean()) / s.std()).clip(0, 10)


def calculate_athletic_value(df):
    if df.empty: return df

    # Standardize Stats
    df['S_PTS'] = standardize(df['PTS'])
    df['S_AST'] = standardize(df['AST'])
    df['S_TRB'] = standardize(df['TRB'])
    df['S_PER'] = standardize(df['PER'])

    # 1. Calculate Raw Scores
    # Offense weight in formula: 0.6
    # Defense weight in formula: 0.4

    # Offense Component (Raw)
    raw_off_score = (0.45 * df['S_PTS'] + 0.35 * df['S_AST'] + 0.2 * df['S_PER'])

    # Defense Component (Raw)
    raw_def_score = (0.70 * df['S_TRB'] + 0.3 * 5.0)

    # 2. Apply Weighting & Risk to get Final Components
    # This ensures: Final_Off + Final_Def = Total_Athletic_Value

    risk_multiplier = (1 - df['Risk_Factor'])

    df['Final_Off_Value'] = raw_off_score * 0.6 * risk_multiplier
    df['Final_Def_Value'] = raw_def_score * 0.4 * risk_multiplier

    df['Total_Athletic_Value'] = df['Final_Off_Value'] + df['Final_Def_Value']

    return df


if __name__ == "__main__":
    df_raw = load_all_players_data(DATA_ROOT_FOLDER)

    if not df_raw.empty:
        print("\n⚡ Calculating Split Athletic Value...")
        final_df = calculate_athletic_value(df_raw)

        # Sort for Charting
        final_df = final_df.sort_values(by='Total_Athletic_Value', ascending=True)  # Ascending for barh

        # === OUTPUT TEXT TABLE (English) ===
        print_df = final_df.sort_values(by='Total_Athletic_Value', ascending=False)
        print_df.insert(0, 'Rank', range(1, len(print_df) + 1))

        print("\n" + "=" * 70)
        print("🏆 PLAYER ATHLETIC VALUE (OFFENSE vs DEFENSE) 🏆")
        print("=" * 70)
        cols = ['Rank', 'Player', 'Total_Athletic_Value', 'Final_Off_Value', 'Final_Def_Value', 'Age']
        pd.set_option('display.float_format', lambda x: '%.2f' % x)
        print(print_df[cols].to_string(index=False))
        print("=" * 70 + "\n")

        # === STACKED BAR CHART ===
        try:
            plt.figure(figsize=(14, max(8, len(final_df) * 0.5)))

            # Set English Fonts
            plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

            # Plot Offense (Base Layer) - Purple
            p1 = plt.barh(final_df['Player'], final_df['Final_Off_Value'],
                          color=LAKERS_PURPLE, edgecolor='white', label='Offensive Value')

            # Plot Defense (Stacked Layer) - Gold
            p2 = plt.barh(final_df['Player'], final_df['Final_Def_Value'],
                          left=final_df['Final_Off_Value'],  # Stack on top of offense
                          color=LAKERS_GOLD, edgecolor='white', label='Defensive Value')

            # Add Total Value Label at the end of the bar
            for i, (total, off, def_val) in enumerate(zip(final_df['Total_Athletic_Value'],
                                                          final_df['Final_Off_Value'],
                                                          final_df['Final_Def_Value'])):
                # Label for Total
                plt.text(total + 0.05, i, f"{total:.2f}",
                         va='center', fontweight='bold', fontsize=10, color='#333333')

                # Optional: Label inside the bar if it's wide enough (Offense)
                if off > 1.0:
                    plt.text(off / 2, i, f"{off:.1f}",
                             va='center', ha='center', color='white', fontsize=8, alpha=0.8)

            # Decoration
            plt.title("NBA Player Athletic Value Breakdown (Lakers Theme)", fontsize=16, fontweight='bold', pad=20)
            plt.xlabel("Weighted Value Score", fontsize=12, fontweight='bold')
            plt.ylabel("Player Name", fontsize=12, fontweight='bold')

            # Legend
            plt.legend(loc='lower right', frameon=True, fontsize=11)

            # Grid and Background
            plt.grid(axis='x', linestyle='--', alpha=0.4, color='gray')
            plt.tight_layout()

            save_name = 'Lakers_Off_Def_Chart.png'
            plt.savefig(save_name, dpi=300)
            print(f"📊 Chart generated: {save_name}")
            plt.show()

        except Exception as e:
            print(f"Plotting error: {e}")
    else:
        print("❌ No data found.")