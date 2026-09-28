import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# ==========================================
# 1. Data Preparation (From your previous output)
# ==========================================
data = [
    {'Player': 'Doncic', 'Von': 6.573},
    {'Player': 'Reaves', 'Von': 5.405},
    {'Player': 'Ayton', 'Von': 4.928},
    {'Player': 'James', 'Von': 4.898},
    {'Player': 'Hayes', 'Von': 4.768},
    {'Player': 'Manon', 'Von': 4.601},
    {'Player': 'LaRavia', 'Von': 4.509},
    {'Player': 'Hachimura', 'Von': 4.185},
    {'Player': 'Vanderbilt', 'Von': 4.083},
    {'Player': 'Knecht', 'Von': 3.939},
    {'Player': 'Timme', 'Von': 3.907},
    {'Player': 'Thiero', 'Von': 3.809},
    {'Player': 'Smart', 'Von': 3.686},
    {'Player': 'JrSmith', 'Von': 3.650},
    {'Player': 'Bronny', 'Von': 3.625},
    {'Player': 'Vincent', 'Von': 3.305},
    {'Player': 'Kleber', 'Von': 3.103}
]
df = pd.DataFrame(data)


# ==========================================
# 2. Calculate Team Strength (T_perf)
# ==========================================
def calculate_team_strength(df):
    """
    Calculate team strength based on Player Von and simulated rotation weights.
    Logic: Coaches give more minutes to players with higher Von.
    """
    # Sort by strength
    df = df.sort_values(by='Von', ascending=False).reset_index(drop=True)

    # Simulate NBA Rotation Weights (Minutes / 48) * 5
    # Assumes a 9-10 man rotation
    weights = np.array(
        [0.18, 0.17, 0.14, 0.13, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.01, 0.01, 0.0, 0.0, 0.0, 0.0, 0.0])

    # Ensure weights match length
    if len(weights) < len(df):
        weights = np.pad(weights, (0, len(df) - len(weights)), 'constant')
    else:
        weights = weights[:len(df)]

    # Normalize weights to sum to 1
    weights = weights / weights.sum()

    # T_perf = Weighted Sum of Von
    t_perf = np.sum(df['Von'] * weights)

    return t_perf


team_perf = calculate_team_strength(df)
league_avg_perf = 5.0  # Assumed League Average Normalized to 5.0

print(f"🏀 Team Performance (T_perf): {team_perf:.3f}")
print(f"⚖️ League Avg Performance (S_avg): {league_avg_perf:.3f}")


# ==========================================
# 3. Logistic Win Rate Model
# ==========================================
def calculate_win_prob(t_perf, s_opp, k=1.8):
    """
    Logistic Function
    k: Sensitivity factor.
       Higher k means winning probability changes more drastically with skill difference.
    """
    z = k * (t_perf - s_opp)
    return 1 / (1 + np.exp(-z))


# Generate Opponent Strength Range (from 3.5 Weak to 6.5 Strong)
opponents_strength = np.linspace(3.5, 6.5, 300)
win_rates = calculate_win_prob(team_perf, opponents_strength)

# ==========================================
# 4. Plotting
# ==========================================
plt.figure(figsize=(12, 7))
plt.style.use('bmh')  # Clean style
# Removed Chinese font settings since we are using English only

# Plot S-Curve
plt.plot(opponents_strength, win_rates, color='#552583', linewidth=3, label='Lakers Win Probability')  # Lakers Purple

# Fill Area
plt.fill_between(opponents_strength, win_rates, 0, color='#FDB927', alpha=0.3)  # Lakers Gold

# --- Key Reference Lines ---
# 1. vs League Average (S_opp = 5.0)
win_rate_vs_avg = calculate_win_prob(team_perf, league_avg_perf)
plt.scatter([league_avg_perf], [win_rate_vs_avg], color='red', s=100, zorder=5)
plt.vlines(league_avg_perf, 0, win_rate_vs_avg, linestyles='--', colors='gray')
plt.hlines(win_rate_vs_avg, 3.5, league_avg_perf, linestyles='--', colors='gray')
plt.text(league_avg_perf + 0.05, win_rate_vs_avg - 0.05,
         f'vs League Avg\nWin Rate: {win_rate_vs_avg:.1%}', fontsize=12, fontweight='bold', color='red')

# 2. vs Weak Team (S_opp = 4.0)
win_rate_vs_weak = calculate_win_prob(team_perf, 4.0)
plt.scatter([4.0], [win_rate_vs_weak], color='green', s=80, zorder=5)
plt.text(4.0, win_rate_vs_weak + 0.03, f'vs Weak Team\n{win_rate_vs_weak:.1%}', ha='center', fontsize=10)

# 3. vs Strong Team (S_opp = 6.0)
win_rate_vs_strong = calculate_win_prob(team_perf, 6.0)
plt.scatter([6.0], [win_rate_vs_strong], color='black', s=80, zorder=5)
plt.text(6.0, win_rate_vs_strong + 0.03, f'vs Strong Team\n{win_rate_vs_strong:.1%}', ha='center', fontsize=10)

# Chart Formatting
plt.title(f'NBA Win Rate Prediction Model (Logistic Function)\nTeam Performance Score: {team_perf:.2f}', fontsize=16)
plt.xlabel('Opponent Strength Score ($S_{opp}$)', fontsize=12)
plt.ylabel('Predicted Win Rate ($P$)', fontsize=12)
plt.ylim(0, 1.05)
plt.xlim(3.5, 6.5)

# Y-Axis Percentage Format
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

# Add Formula Annotation
formula_text = r"$P = \frac{1}{1 + e^{-k(T_{perf} - S_{opp})}}$"
plt.text(3.6, 0.1, formula_text, fontsize=16, bbox=dict(facecolor='white', alpha=0.8, edgecolor='gray'))

plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(loc='upper right')

plt.tight_layout()
plt.show()

# Print Simple Report
print("-" * 30)
print(f"📊 Team Evaluation: {team_perf:.2f} (League Avg: 5.00)")
print(f"📈 Win Rate vs Avg Opponent: {win_rate_vs_avg:.2%}")
if team_perf > 5.2:
    print("🏆 Verdict: Championship Contender")
elif team_perf > 4.8:
    print("😐 Verdict: Play-in / Playoff Team")
else:
    print("📉 Verdict: Lottery / Rebuilding Team")