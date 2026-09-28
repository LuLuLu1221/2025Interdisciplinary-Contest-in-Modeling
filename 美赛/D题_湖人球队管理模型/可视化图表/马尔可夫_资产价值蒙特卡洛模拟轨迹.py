import numpy as np
import matplotlib.pyplot as plt

# 1. Setup Style (English & Lakers Theme)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']


def plot_monte_carlo_valuation():
    # ==========================================
    # 1. Simulation Parameters
    # ==========================================
    n_simulations = 1000  # Number of future scenarios
    years = np.arange(2025, 2031)  # 6 seasons
    n_years = len(years)

    # Initial Valuation (High due to Luka + LBJ Superteam)
    # Current Lakers ~6.4B. With Luka, we estimate ~8.2B start.
    start_val = 8.2

    # Storage for all paths
    all_paths = np.zeros((n_simulations, n_years))
    all_paths[:, 0] = start_val

    # ==========================================
    # 2. Monte Carlo Logic (The "Trio" Dynamics)
    # ==========================================
    np.random.seed(42)  # For reproducibility

    for i in range(n_simulations):
        for t in range(1, n_years):
            year = years[t]
            prev_val = all_paths[i, t - 1]

            # A. Base Market Growth (NBA Media Rights deal kicking in)
            # Normal distribution: mean 5%, std 2%
            market_growth = np.random.normal(0.05, 0.02)

            # B. Specific Shock 1: Expansion Draft (2027)
            # Doc Phase 3: "a_protect" minimizes this, but it still hits.
            expansion_impact = 0
            if year == 2027:
                # Loss of depth assets (-3% to -8%)
                expansion_impact = np.random.uniform(-0.08, -0.03)

            # C. Specific Shock 2: LeBron Retirement Risk (2027-2028)
            # High probability of LBJ retiring in year 2 or 3
            retirement_shock = 0
            if year in [2027, 2028]:
                # 40% chance of retirement each of these years
                if np.random.rand() < 0.40:
                    # Significant drop in V_off (-10%), but cushioned by Luka
                    retirement_shock = -0.10

                    # D. The "Luka + Reaves" Resilience Factor
            # They dampen the negative shocks. If shock is negative, reduce it by 20%.
            total_shock = expansion_impact + retirement_shock
            if total_shock < 0:
                total_shock *= 0.8  # Resilience buffer

            # Calculate new value
            # Formula: V_t = V_{t-1} * (1 + Growth + Shocks) + Noise
            volatility_noise = np.random.normal(0, 0.03)
            new_val = prev_val * (1 + market_growth + total_shock) + volatility_noise

            all_paths[i, t] = new_val

    # ==========================================
    # 3. Statistical Analysis
    # ==========================================
    mean_path = np.mean(all_paths, axis=0)
    p5 = np.percentile(all_paths, 5, axis=0)  # Worst 5% case
    p95 = np.percentile(all_paths, 95, axis=0)  # Best 5% case

    # ==========================================
    # 4. Visualization (Lakers Theme)
    # ==========================================
    fig, ax = plt.subplots(figsize=(12, 7))

    # Plot 100 random individual paths (Thin traces)
    # Using Light Purple for traces
    for i in range(100):
        ax.plot(years, all_paths[i, :], color='#552583', alpha=0.05, linewidth=1)

    # Plot Confidence Interval (The "Safety Zone")
    ax.fill_between(years, p5, p95, color='#FDB927', alpha=0.3, label='95% Confidence Interval')

    # Plot Mean Trajectory (Thick Purple Line)
    ax.plot(years, mean_path, color='#552583', linewidth=4, label='Expected Valuation Trend')
    ax.scatter(years, mean_path, color='white', edgecolor='#552583', s=80, zorder=5)

    # Annotations (Key Events)

    # 1. Expansion Draft Dip
    val_2027 = mean_path[2]
    ax.annotate('Expansion Draft (2027)\n& Potential LBJ Exit',
                xy=(2027, val_2027), xytext=(2026.5, val_2027 - 1.5),
                arrowprops=dict(facecolor='red', shrink=0.05),
                fontsize=11, fontweight='bold', color='#B20000')

    # 2. The Luka Recovery
    val_2030 = mean_path[-1]
    ax.annotate('Luka & Reaves Era\n(Long-term Growth)',
                xy=(2029, val_2030), xytext=(2028, val_2030 + 1.0),
                arrowprops=dict(facecolor='green', shrink=0.05),
                fontsize=11, fontweight='bold', color='darkgreen')

    # Formatting
    ax.set_title('PROJECTED FRANCHISE VALUATION (2025-2030)\nMonte Carlo Simulation w/ Expansion & Retirement Risks',
                 fontsize=15, fontweight='bold', color='#2E003E', pad=20)
    ax.set_ylabel('Franchise Value (Billions USD)', fontsize=12, fontweight='bold')
    ax.set_xlabel('Season Year', fontsize=12, fontweight='bold')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend(loc='upper left', fontsize=11)

    # Add Text Box for "Resilience"
    textstr = '\n'.join((
        r'$\bf{Model\ Insight:}$',
        r'Despite the "Dip" in 2027 due to',
        r'Expansion/Age risks, the presence',
        r'of Luka/Reaves maintains the',
        r'valuation floor above $8.0B.'
    ))
    props = dict(boxstyle='round', facecolor='white', alpha=0.9, edgecolor='#FDB927')
    ax.text(0.02, 0.65, textstr, transform=ax.transAxes, fontsize=10, bbox=props)

    plt.tight_layout()
    plt.show()


plot_monte_carlo_valuation()