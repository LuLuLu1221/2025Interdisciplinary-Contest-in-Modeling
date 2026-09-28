import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import sys
import os

# ==========================================
# 0. Global Settings
# ==========================================
# No special font settings needed for English
plt.style.use('ggplot')  # Optional: Makes the chart look a bit nicer


# ==========================================
# 1. Data Loading & Cleaning Module
# ==========================================

def smart_load_data(basic_path, adv_path):
    """
    Intelligently loads Excel files, handling header variations
    and different column names automatically.
    """
    print(">>> Attempting to load data...")

    # Internal helper: try reading a single file
    def read_single_file(path):
        if not os.path.exists(path):
            print(f"Error: File not found - {path}")
            sys.exit(1)

        # Try the first 3 rows as headers to find 'Team' or 'Tm'
        for header_row in range(3):
            try:
                df = pd.read_excel(path, header=header_row)

                # Check for Team column
                if 'Team' in df.columns:
                    return df
                elif 'Tm' in df.columns:
                    return df.rename(columns={'Tm': 'Team'})
                elif 'Squad' in df.columns:  # Basketball-Ref sometimes uses Squad
                    return df.rename(columns={'Squad': 'Team'})

            except Exception:
                continue

        print(f"Failure: Could not find 'Team' or 'Tm' column in file: {os.path.basename(path)}")
        sys.exit(1)

    # 1. Read the two files
    df_basic = read_single_file(basic_path)
    df_adv = read_single_file(adv_path)

    print(">>> Files read successfully. Cleaning data...")

    # 2. Clean Team Names (Remove '*' and whitespace)
    df_basic['Team'] = df_basic['Team'].astype(str).str.replace('*', '', regex=False).str.strip()
    df_adv['Team'] = df_adv['Team'].astype(str).str.replace('*', '', regex=False).str.strip()

    # 3. Check for Advanced Stats Column (DRtg)
    # Common names: 'DRtg', 'DefRtg', 'DRtg/100'
    drtg_col = None
    for col in df_adv.columns:
        if 'DRtg' in col or 'DefRtg' in col:
            drtg_col = col
            break

    if drtg_col:
        df_adv.rename(columns={drtg_col: 'DRtg'}, inplace=True)
    else:
        print("Warning: 'DRtg' column not found in advanced stats. Using 'OppPTS' from basic stats instead.")
        df_adv['DRtg'] = np.nan  # Placeholder

    # 4. Merge Data
    # If DRtg exists, merge it; otherwise just use basic data
    if 'DRtg' in df_adv.columns and not df_adv['DRtg'].isna().all():
        df = pd.merge(df_basic, df_adv[['Team', 'DRtg']], on='Team', how='inner')
    else:
        df = df_basic.copy()

    # 5. Standardize Column Names
    col_mapping = {
        'TRB': 'REB',
        'DRtg': 'Def_Rating'  # Rename to avoid confusion
    }
    df.rename(columns=col_mapping, inplace=True)

    # 6. Convert Data Types
    # Ensure these are numbers, coerce errors to NaN
    numeric_cols = ['PTS', 'FG%', '3P%', 'AST', 'REB', 'STL', 'BLK', 'Def_Rating', 'OppPTS']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 7. Filter Invalid Rows (e.g., "League Average")
    df = df[~df['Team'].str.contains('Average|Total', case=False, na=False)]

    print(f">>> Data preparation complete! Loaded {len(df)} teams.")
    return df


# ==========================================
# 2. Core Analysis Model (Z-Score)
# ==========================================

def analyze_team(df, target_team_keyword):
    """
    Input: DataFrame and Team Keyword (e.g., 'Lakers')
    Output: Results Dictionary and Full Team Name
    """
    # 1. Find the full team name
    matched_teams = df[df['Team'].str.contains(target_team_keyword, case=False)]
    if matched_teams.empty:
        print(f"Error: No team found matching '{target_team_keyword}'. Please check spelling.")
        return None, None

    full_team_name = matched_teams.iloc[0]['Team']
    print(f"Analyzing Team: {full_team_name}")

    # 2. Define Metrics
    # Use Def_Rating if available, otherwise OppPTS
    def_metric = 'Def_Rating' if 'Def_Rating' in df.columns and df['Def_Rating'].notna().any() else 'OppPTS'

    # Metrics Mapping: {Excel_Column: Display_Name}
    metrics_map = {
        'PTS': 'Scoring (Offense)',
        'FG%': 'Efficiency (Off)',
        '3P%': '3-Point (Space)',
        'AST': 'Assists (Playmaking)',
        def_metric: 'Defense (Overall)',  # Note: Needs inversion (Lower is better)
        'REB': 'Rebounding (Size)',
        'BLK': 'Rim Protection',
        'STL': 'Steals (Perimeter)'
    }

    results = {}

    # 3. Calculate Z-Score
    for col, label in metrics_map.items():
        if col not in df.columns:
            continue

        mean_val = df[col].mean()
        std_val = df[col].std()
        team_val = df.loc[df['Team'] == full_team_name, col].values[0]

        z_score = (team_val - mean_val) / std_val

        # Special Handling: For Defense/Turnovers, Lower is Better.
        # We invert Z-Score so that on the chart, "Outward" is always "Good".
        if col in ['Def_Rating', 'OppPTS', 'TOV']:
            z_score = z_score * -1

        results[label] = z_score

    # 4. Generate GM Action Plan
    print("\n-------- GM DIAGNOSTIC REPORT --------")
    recommendations = []

    if results.get('Scoring (Offense)', 0) < 0:
        recommendations.append("Low Scoring Output: Need a primary scorer.")

    if results.get('3-Point (Space)', 0) < -0.5:
        recommendations.append("[CRITICAL GAP] Poor Spacing: Need high-volume 3-point shooters.")

    if results.get('Defense (Overall)', 0) < -0.2:
        recommendations.append("Defensive Liability: Need to improve overall defensive scheme.")

    if results.get('Rim Protection', 0) < -0.5:
        recommendations.append("[CRITICAL GAP] Interior Defense: Immediate need for a Shot-Blocking Center.")

    if not recommendations:
        print("Status: Team is well-balanced. Suggest looking for depth or star upgrades.")
    else:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")

    return results, full_team_name


# ==========================================
# 3. Visualization Module (Radar Chart)
# ==========================================

def plot_radar(results, team_name):
    if not results: return

    # Prepare Data
    labels = list(results.keys())
    values = list(results.values())

    # Normalize Data: Map Z-Score (-3 to +3) to (0 to 100)
    # Z=0 (League Average) -> 50 points
    scores = [min(max(50 + (v * 16.66), 0), 100) for v in values]

    # Close the loop for the radar chart
    scores += scores[:1]
    angles = np.linspace(0, 2 * pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    # Plotting
    fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True))

    # Draw Lines
    ax.plot(angles, scores, color='#552583', linewidth=2, label=team_name)  # Lakers Purple
    ax.fill(angles, scores, color='#FDB927', alpha=0.4)  # Lakers Gold

    # Draw Average Line (at 50)
    ax.plot(angles, [50] * len(angles), color='grey', linestyle='--', linewidth=1, label='League Avg')

    # Setup Labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, size=11, color='black')

    # Setup Grid/Scale
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(['Poor', 'Avg', 'Good', 'Elite'], color="grey", size=9)
    ax.set_ylim(0, 100)

    plt.title(f"{team_name} 2026 Season Performance Radar", size=16, y=1.08, weight='bold')
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))

    plt.show()


# ==========================================
# 4. Main Execution
# ==========================================

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # NOTE: Keep the path as is if your files are still named in Chinese.
    # If you rename the files to English, update the paths below.
    file_basic = r"C:\Users\28137\Desktop\球队数据\全联盟场均.xlsx"
    file_adv = r"C:\Users\28137\Desktop\球队数据\全联盟球队高阶数据.xlsx"

    target_team = "Lakers"  # The team you want to analyze

    # --- EXECUTION ---
    # 1. Load
    df = smart_load_data(file_basic, file_adv)

    # 2. Analyze
    stats, full_name = analyze_team(df, target_team)

    # 3. Plot
    if stats:
        plot_radar(stats, full_name)