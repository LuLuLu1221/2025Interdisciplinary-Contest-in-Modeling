import numpy as np
import matplotlib.pyplot as plt

# 1. Setup Plot Style (Standard Font for English)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']


def plot_core_trio_analysis():
    # ==========================================
    # 1. Parameter Injection: The "Big Three" Core
    # ==========================================
    # Roster: Luka Doncic (Prime) + LeBron James (Vet) + Austin Reaves (Young)

    # Commercial Appeal (V_off):
    # Luka (Global Star) + LBJ (Icon) + Reaves (Fan Fav) = Very High
    v_off_total = 75.0

    # Performance Resilience (Alpha):
    # Unlike a single-core team, Luka + Reaves can carry the load when LBJ sits.
    # This lowers the penalty for resting LeBron.
    resilience_factor = 1.4

    # Risk Threshold (The Constraint):
    # Still dictated by the oldest core member (LeBron, 41).
    # Risk starts rising significantly after moderate intensity.
    max_age = 41
    risk_threshold = 30  # Intensity % where risk begins to spike

    # ==========================================
    # 2. Simulation Logic (MDP Phase 2)
    # ==========================================
    # X-axis: Roster Usage Intensity (0% - 100%)
    intensity = np.linspace(0, 100, 300)

    # Reward Function Component 1: Short-term Profit (Pi)
    # Formula: w1 * V_off * log(1 + Intensity) * Resilience
    w1 = 0.45
    profit_curve = w1 * (v_off_total * 1.8) * np.log(1 + intensity / 15) * resilience_factor

    # Reward Function Component 2: Asset Preservation (Delta V)
    # Formula: - w2 * exp(Intensity - Threshold)
    # Logic: Risk is low initially, but explodes if we overwork the 41-year-old.
    w2 = 0.55
    risk_curve = np.zeros_like(intensity)
    mask = intensity > risk_threshold

    # Exponential risk penalty
    risk_curve[mask] = np.exp((intensity[mask] - risk_threshold) / 14) * 3.5
    weighted_risk = - (w2 * risk_curve)

    # Global Objective Function Z
    # Base valuation constant added for visual clarity
    base_valuation = 120
    z_score = base_valuation + profit_curve + weighted_risk

    # ==========================================
    # 3. Find Optimal Policy
    # ==========================================
    optimal_idx = np.argmax(z_score)
    opt_x = intensity[optimal_idx]
    opt_z = z_score[optimal_idx]

    # ==========================================
    # 4. Visualization (English Only)
    # ==========================================
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot Curves
    ax.plot(intensity, profit_curve + base_valuation,
            color='gray', linestyle='--', alpha=0.5, linewidth=1.5,
            label='Revenue Growth (Ticket/Media)')

    ax.plot(intensity, base_valuation + weighted_risk,
            color='red', linestyle=':', alpha=0.6, linewidth=1.5,
            label='Asset Deprecation (Injury Risk)')

    ax.plot(intensity, z_score,
            color='#552583', linewidth=3.5,  # Lakers Purple
            label='Global Objective Z (Total Value)')

    # Highlight Optimal Point
    ax.scatter(opt_x, opt_z, color='#FDB927', s=150, zorder=5, edgecolors='black')  # Lakers Gold
    ax.vlines(opt_x, 100, opt_z, linestyles='dashed', colors='#FDB927', alpha=0.8)

    # Annotations (English)
    ax.annotate(f'Optimal Load: {opt_x:.1f}%\n(Balanced Strategy)',
                xy=(opt_x, opt_z), xytext=(opt_x + 5, opt_z + 15),
                arrowprops=dict(facecolor='black', arrowstyle='->', connectionstyle="arc3,rad=.2"),
                fontsize=11, fontweight='bold', color='black')

    ax.text(80, 140, 'Overload Zone:\nRisk > Reward', color='red', fontsize=10, ha='center')
    ax.text(10, 150, 'Under-utilization:\nMissed Revenue', color='gray', fontsize=10, ha='center')

    # Key Insight Box
    textstr = '\n'.join((
        r'$\bf{Core\ Trio\ Dynamics:}$',
        r'Luka + Reaves provide high resilience,',
        r'allowing the team to maintain high Z',
        r'even with moderate LBJ usage.'
    ))
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.3)
    ax.text(0.02, 0.95, textstr, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=props)

    # Labels and Title
    ax.set_title('MDP Phase 2 Optimization: Luka + LBJ + Reaves Core', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Roster Utilization / Intensity (%)', fontsize=12)
    ax.set_ylabel('Franchise Value Contribution (Normalized)', fontsize=12)
    ax.legend(loc='lower left', frameon=True)

    ax.grid(True, linestyle='--', alpha=0.3)

    plt.tight_layout()
    plt.show()


# Run the plot
plot_core_trio_analysis()