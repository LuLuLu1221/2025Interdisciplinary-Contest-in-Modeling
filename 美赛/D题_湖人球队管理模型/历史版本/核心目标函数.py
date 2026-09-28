import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. Initialize Data
# ==========================================
initial_data = {
    'Player': ['Luka Doncic', 'Austin Reaves', 'Deandre Ayton', 'LeBron James', 'Jaxson Hayes',
               'Chris Manon', 'Jake LaRavia', 'Rui Hachimura', 'Jarred Vanderbilt', 'Dalton Knecht'],
    'Age': [26, 27, 27, 41, 25, 24, 24, 27, 26, 24],
    'G': [38, 23, 41, 29, 38, 4, 46, 36, 37, 37],
    'Minutes': [1380, 812, 1161, 962, 671, 14, 1261, 1084, 720, 458],
    # S_i: Athletic Ability, F_i: Commercial Appeal
    'S_i': [6.57, 5.40, 4.92, 4.89, 4.76, 4.60, 4.50, 4.18, 4.08, 3.93],
    'F_i': [8.04, 6.90, 5.55, 9.18, 5.41, 3.62, 5.03, 5.06, 4.33, 4.43]
}

df_roster = pd.DataFrame(initial_data)
df_roster['MPG'] = df_roster['Minutes'] / df_roster['G']
# x_i: Resource Allocation Variable (Minutes played normalized)
df_roster['x_i'] = df_roster['MPG'] / 48.0

# ==========================================
# 2. Global Parameters
# ==========================================
W1 = 0.60  # w1: Weight for Profit
W2 = 0.40  # w2: Weight for Valuation Change
GAMMA = 0.90  # γ: Time Discount Factor
T_YEARS = 5  # T: Simulation Years

SALARY_CAP = 180.0  # Salary Cap ($M)
TAX_RATE = 1.5  # Luxury Tax Rate
BASE_BRAND_VAL = 6000.0  # Base Franchise Value ($M)

ALPHA = 150.0  # Competitive Revenue Coefficient
BETA = 8.0  # Star Power Revenue Coefficient
THETA = 1.0  # External Environment Coefficient
E_MEDIA = 120.0  # Media Rights Baseline
LAMBDA = 0.005  # Friction Coefficient

# Set random seed for reproducibility
np.random.seed(42)


# ==========================================
# 3. Core Calculation Models
# ==========================================

def calculate_revenue_profit(current_df, year_idx):
    """
    Calculate Current Period Profit (Pi_t)
    """
    # 1. Competitive Performance (T_perf)
    raw_talent = np.sum(current_df['S_i'] * current_df['x_i'])
    friction = LAMBDA * (raw_talent ** 2)
    t_perf = raw_talent - friction

    # 2. Revenue (R)
    rev_comp = ALPHA * np.log(1 + max(0, t_perf))
    rev_star = BETA * np.sum(current_df['F_i'] * current_df['x_i'])
    rev_media = THETA * E_MEDIA
    total_revenue = rev_comp + rev_star + rev_media

    # --- Salary Fluctuation Simulation ---
    # Randomly fluctuate between 90% and 125% of the Salary Cap
    fluctuation = np.random.uniform(0.90, 1.25)
    total_salary = SALARY_CAP * fluctuation

    # Luxury Tax Calculation
    tax = 0
    if total_salary > SALARY_CAP:
        tax = (total_salary - SALARY_CAP) * TAX_RATE

    total_cost = total_salary + tax + 50.0  # 50 is Ops Cost

    # 3. Net Profit
    profit = total_revenue - total_cost

    # Win Probability (for Valuation)
    win_prob = 1 / (1 + np.exp(-0.3 * (t_perf - 20.0)))

    return profit, win_prob, total_salary, tax


def calculate_franchise_value(current_df, base_brand_val, win_prob):
    """
    Calculate Franchise Value (V_t)
    """
    # Brand/Media Value (Impacted by Win Probability)
    brand_multiplier = 1.0 + (win_prob - 0.5) * 0.5
    val_brand = base_brand_val * brand_multiplier

    # Player Asset Portfolio Value
    player_asset_val = np.sum((current_df['S_i'] + current_df['F_i']) * 10.0)

    return val_brand + player_asset_val


def apply_aging(df, year):
    """Simple Aging Model"""
    df_new = df.copy()
    for i, row in df_new.iterrows():
        age = row['Age'] + year
        # Decline after 32, slight improve before 24
        decay = 0.05 * (age - 32) if age > 32 else (-0.05 if age < 24 else 0)
        df_new.at[i, 'S_i'] = row['S_i'] * (1 - decay)
    return df_new


# ==========================================
# 4. Simulation Process
# ==========================================
history = {
    'Year': [], 'Profit': [], 'V_Franchise': [],
    'Delta_V': [], 'Discounted_Z': [], 'Cumulative_Z': [],
    'Salary_Paid': []
}

# Initial State (t=-1)
profit_init, win_init, _, _ = calculate_revenue_profit(df_roster, -1)
v_prev = calculate_franchise_value(df_roster, BASE_BRAND_VAL, win_init)
cumulative_z = 0
current_base_brand = BASE_BRAND_VAL

print(f"=== Objective Function Z Simulation (Salary Cap: ${SALARY_CAP}M) ===\n")

for t in range(T_YEARS):
    # 1. Aging & Market Growth
    roster_t = apply_aging(df_roster, t)
    current_base_brand *= 1.05  # 5% Market Growth

    # 2. Calculate Profit (With Random Salary)
    profit_t, win_prob_t, actual_salary, tax_paid = calculate_revenue_profit(roster_t, t)

    # 3. Calculate Value V_t
    v_t = calculate_franchise_value(roster_t, current_base_brand, win_prob_t)

    # 4. Value Increment Delta_V
    delta_v = v_t - v_prev

    # 5. Discounted Z Contribution
    z_term = W1 * profit_t + W2 * delta_v
    discounted_z = (GAMMA ** t) * z_term
    cumulative_z += discounted_z

    # Record Data
    history['Year'].append(t + 1)
    history['Profit'].append(profit_t)
    history['V_Franchise'].append(v_t)
    history['Delta_V'].append(delta_v)
    history['Discounted_Z'].append(discounted_z)
    history['Cumulative_Z'].append(cumulative_z)
    history['Salary_Paid'].append(actual_salary)

    v_prev = v_t

    # Log
    cap_ratio = (actual_salary / SALARY_CAP) * 100
    print(
        f"Year {t + 1}: Cost={cap_ratio:.0f}% Cap (Tax:${tax_paid:.0f}M) | Profit=${profit_t:.0f}M | Val Change=${delta_v:.0f}M -> Cumul Z={cumulative_z:.2f}")

# ==========================================
# 5. Visualization (English Labels & Custom Colors)
# ==========================================
# Use standard fonts for English
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False
plt.style.use('ggplot')

# --- Color Definitions ---
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'
LINE_RED = '#FF0000'  # Requested: Red for Overdraft
LINE_BLACK = '#000000'  # Requested: Black for Z

df_res = pd.DataFrame(history)

fig, ax1 = plt.subplots(figsize=(12, 7))

width = 0.35
x = df_res['Year']

# === Bar Chart (Lakers Theme) ===
# Profit Contribution (Gold)
p1 = ax1.bar(x - width / 2, df_res['Profit'] * W1, width,
             label=r'Profit Contribution ($w_1 \Pi_t$)',
             color=LAKERS_GOLD, alpha=0.9,
             edgecolor='gray', linewidth=0.5)

# Valuation Contribution (Purple)
p2 = ax1.bar(x + width / 2, df_res['Delta_V'] * W2, width,
             label=r'Valuation Contribution ($w_2 \Delta V_t$)',
             color=LAKERS_PURPLE, alpha=0.85,
             edgecolor='gray', linewidth=0.5)

# === Line 1: Salary Cap Overdraft (RED) ===
ax1.plot(x, (df_res['Salary_Paid'] - SALARY_CAP),
         color=LINE_RED, linestyle=':', marker='x', linewidth=2,
         label='Salary Cap Overdraft')

# === Axis Settings ===
ax1.set_xlabel('Simulation Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Weighted Contribution / Cap Overdraft ($M)', fontweight='bold', fontsize=12)
ax1.set_title(f'Lakers Dynamic Objective Function Z Simulation\n(Random Salary Fluctuation vs Cap ${SALARY_CAP}M)',
              fontsize=14, fontweight='bold')
ax1.axhline(0, color='gray', linewidth=1)  # Zero line

# Legend for Left Axis
legend = ax1.legend(loc='upper left', frameon=True, facecolor='white', edgecolor='gray')

# === Line 2: Cumulative Z (BLACK) ===
ax2 = ax1.twinx()
ax2.plot(x, df_res['Cumulative_Z'],
         color=LINE_BLACK, marker='D', markersize=6,
         linewidth=2.5, linestyle='-',
         label='Cumulative Z Value')

# Right Axis Settings
ax2.set_ylabel('Cumulative Z Value', color=LINE_BLACK, fontweight='bold', fontsize=12)
ax2.tick_params(axis='y', labelcolor=LINE_BLACK, colors=LINE_BLACK)
# Legend for Right Axis
ax2.legend(loc='lower right')

# Grid
ax1.grid(True, axis='y', linestyle='--', alpha=0.3)

plt.tight_layout()
plt.show()

print(f"\nFinal Result: 5-Year Cumulative Z = {cumulative_z:.2f}")