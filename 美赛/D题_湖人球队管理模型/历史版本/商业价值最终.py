import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. Data Entry (Commercial Data Only)
# ==========================================
data = {
    'Player': [
        'LeBron', 'Doncic', 'Hachimura', 'Reaves',
        'Vanderbilt', 'Vincent', 'Kleber', 'Ayton',
        'LaRavia', 'Smart', 'Knecht', 'Hayes',
        'Bronny', 'Thiero', 'Manton', 'Smith',
        'SMilton', 'Koloko', 'Bufkin'
    ],
    'Road_Attendance_Pct': ['99.9%', '99.5%', '97.8%', '98.2%', '96.5%', '95.2%', '94.8%', '96.1%', '93.5%', '95.8%', '93.2%', '94.0%', '98.5%', '92.1%', '91.8%', '92.5%', '92.3%', '91.5%', '92.8%'],
    'Social_Followers': [158000000, 10800000, 849000, 1500000, 452000, 181000, 225000, 684000, 205000, 920000, 152000, 328000, 7600000, 85000, 32000, 145000, 124000, 98000, 112000],
    'Global_Brand_Score': [9.9, 9.7, 8.8, 7.5, 5.8, 5.4, 6.2, 6.5, 4.2, 6.8, 4.0, 4.8, 8.5, 3.5, 3.0, 4.1, 3.8, 4.5, 3.9],
    'Jersey_Rank': [2, 1, 35, 18, 120, 185, 210, 88, 350, 65, 95, 240, 8, 400, 450, 310, 280, 330, 290],
    'Media_Index': [98, 95, 65, 72, 45, 30, 25, 55, 15, 50, 40, 20, 92, 10, 5, 15, 18, 12, 16],
    'Sponsor_Lift': [10, 9.5, 8, 6.5, 4, 3, 2.5, 5, 1, 5.5, 3.5, 2, 7.5, 0.5, 0.1, 1.5, 1.5, 1, 1.2],
    'Ticket_Premium': [9.8, 9.9, 6.5, 7, 5, 3.5, 3, 4.5, 1.5, 5, 4, 2.5, 8.5, 1, 0.5, 2, 1.5, 1, 1.5],
    'Merch_Growth': ['15%', '120%', '40%', '25%', '5%', '2%', '1%', '8%', '0%', '10%', '18%', '2%', '300%', '0%', '0%', '3%', '1%', '1%', '2%']
}

df = pd.DataFrame(data)

# ==========================================
# 2. Calculation Logic (Standardization & Weights)
# ==========================================
def clean_percent(x):
    return float(x.strip('%')) / 100 if isinstance(x, str) else x

df['Road_Attendance_Pct'] = df['Road_Attendance_Pct'].apply(clean_percent)
df['Merch_Growth'] = df['Merch_Growth'].apply(clean_percent)

def scale_linear(series, target_min=0, target_max=10):
    return (series - series.min()) / (series.max() - series.min()) * (target_max - target_min) + target_min

def scale_inverse(series):
    # Lower rank (1) = Higher Score (10)
    return ((450 - series) / 449 * 10).clip(0, 10)

# A. Popularity (Pop)
df['std_Social'] = scale_linear(np.log1p(df['Social_Followers']))
df['std_Jersey'] = scale_inverse(df['Jersey_Rank'])
df['std_Media']  = scale_linear(df['Media_Index'])
df['V_pop_Score'] = 10 * df['std_Social'] + 12 * df['std_Jersey'] + 8 * df['std_Media']
df['V_pop_Norm'] = scale_linear(df['V_pop_Score'], 0, 10)

# B. Direct Revenue (Rev)
df['std_Attend'] = scale_linear(df['Road_Attendance_Pct'])
df['std_Sponsor'] = scale_linear(df['Sponsor_Lift'])
df['std_Ticket'] = scale_linear(df['Ticket_Premium'])
df['V_rev_Score'] = 10 * df['std_Attend'] + 9 * df['std_Sponsor'] + 7 * df['std_Ticket']
df['V_rev_Norm'] = scale_linear(df['V_rev_Score'], 0, 10)

# C. Brand Impact (Brand)
df['std_Global'] = scale_linear(df['Global_Brand_Score'])
df['std_Merch'] = scale_linear(df['Merch_Growth'])
df['V_brand_Score'] = 8 * df['std_Global'] + 6 * df['std_Merch']
df['V_brand_Norm'] = scale_linear(df['V_brand_Score'], 0, 10)

# D. Final Weighted Calculation
# V_off = 0.4*Pop + 0.35*Rev + 0.25*Brand
df['Contrib_Pop'] = 0.40 * df['V_pop_Norm']
df['Contrib_Rev'] = 0.35 * df['V_rev_Norm']
df['Contrib_Brand'] = 0.25 * df['V_brand_Norm']

df['V_off_Total'] = df['Contrib_Pop'] + df['Contrib_Rev'] + df['Contrib_Brand']

# Sort for plotting
df_sorted = df.sort_values(by='V_off_Total', ascending=True)

# ==========================================
# 3. Plotting (Stacked Bar Chart - English)
# ==========================================
# Use standard fonts
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']

fig, ax = plt.subplots(figsize=(12, 10), dpi=150)

# Colors
color_pop = '#5D3A9B'   # Purple (Popularity)
color_rev = '#E6A315'   # Gold (Revenue)
color_brand = '#2E8B57' # Green (Brand/Merch)

# Plotting Bars
bars1 = ax.barh(df_sorted['Player'], df_sorted['Contrib_Pop'], color=color_pop, label='Popularity Base (40%)', height=0.6)
bars2 = ax.barh(df_sorted['Player'], df_sorted['Contrib_Rev'], left=df_sorted['Contrib_Pop'], color=color_rev, label='Direct Revenue (35%)', height=0.6)
bars3 = ax.barh(df_sorted['Player'], df_sorted['Contrib_Brand'], left=df_sorted['Contrib_Pop']+df_sorted['Contrib_Rev'], color=color_brand, label='Brand Potential (25%)', height=0.6)

# Adding value labels
for i, (total, player) in enumerate(zip(df_sorted['V_off_Total'], df_sorted['Player'])):
    ax.text(total + 0.1, i, f"{total:.2f}", va='center', fontweight='bold', fontsize=10)

# Chart Decoration (English)
ax.set_title('NBA Player Off-Court Value Model (V_off Breakdown)', fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Weighted Score (0-10 Scale)', fontsize=12)
ax.set_xlim(0, 11)
ax.legend(loc='lower right', title='Value Composition')
ax.grid(axis='x', linestyle='--', alpha=0.3)

# Highlight Top 3
ax.axhspan(len(df_sorted)-3.5, len(df_sorted)-0.5, color='yellow', alpha=0.1)

plt.tight_layout()
plt.show()

# Print Top 5 (English)
print(">>> Top 5 Commercial Value Rankings:")
print(df_sorted[['Player', 'V_off_Total']].sort_values(by='V_off_Total', ascending=False).head(5))