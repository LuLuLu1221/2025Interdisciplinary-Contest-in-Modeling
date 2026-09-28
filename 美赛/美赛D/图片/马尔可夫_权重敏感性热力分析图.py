import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 1. Setup Style (English Professional & Lakers Font Style)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']


def plot_lakers_heatmap():
    # ==========================================
    # 1. Lakers Custom Color Scheme
    # ==========================================
    # Creating a gradient from Deep Purple (Bad) -> Lakers Purple -> White (Neutral) -> Lakers Gold (Good)
    colors = ["#2E003E", "#552583", "#FDFDFD", "#FDB927", "#FFEB3B"]
    lakers_cmap = LinearSegmentedColormap.from_list("LakersTheme", colors, N=100)

    # ==========================================
    # 2. Data Injection (Based on YOUR Real Trio)
    # ==========================================
    # X-axis: Weight on Short-term Profit (w1)
    w1_values = np.linspace(0.0, 1.0, 150)
    # Y-axis: Roster Intensity / Load (0% to 100%)
    intensity_values = np.linspace(0, 100, 150)
    W1, Intensity = np.meshgrid(w1_values, intensity_values)

    # --- Real Data Parameters ---
    # 1. Commercial Power (Luka+LBJ+Reaves): Very High
    v_off_score = 75.0
    # 2. Resilience (Reaves Factor):
    # Helps team perform even when not playing at 100% intensity
    resilience = 1.3
    # 3. Age Cliff (LeBron Factor):
    # Risk explodes after 30% intensity because he is 41
    risk_threshold = 30

    # ==========================================
    # 3. Mathematical Model Calculations
    # ==========================================
    # Profit Component (Gold Zone driver)
    Profit = (v_off_score * 1.6) * np.log(1 + Intensity / 12) * resilience

    # Risk Component (Purple Zone driver)
    Risk_Penalty = np.zeros_like(Intensity)
    mask = Intensity > risk_threshold
    # Exponential penalty for overworking a 41-year-old
    Risk_Penalty[mask] = np.exp((Intensity[mask] - risk_threshold) / 13) * 4.5

    # Global Z Calculation
    Z_matrix = (W1 * Profit) - ((1 - W1) * Risk_Penalty)

    # ==========================================
    # 4. Optimal Path Calculation (White Line)
    # ==========================================
    optimal_path = []
    for w in w1_values:
        # Recalculate column to match matrix dimensions exactly
        profit_col = (v_off_score * 1.6) * np.log(1 + intensity_values / 12) * resilience
        risk_col = np.zeros_like(intensity_values)
        mask_col = intensity_values > risk_threshold
        risk_col[mask_col] = np.exp((intensity_values[mask_col] - risk_threshold) / 13) * 4.5

        z_col = (w * profit_col) - ((1 - w) * risk_col)
        best_idx = np.argmax(z_col)
        optimal_path.append(intensity_values[best_idx])

    # ==========================================
    # 5. Visualization (Lakers Style)
    # ==========================================
    fig, ax = plt.subplots(figsize=(11, 8))

    # Draw Heatmap
    cp = ax.contourf(W1, Intensity, Z_matrix, levels=50, cmap=lakers_cmap)

    # Colorbar
    cbar = fig.colorbar(cp)
    cbar.set_label('Global Objective Value Z (Purple=Risk, Gold=Reward)', fontsize=12, fontweight='bold')

    # Draw Optimal Path (White stands out on Purple/Gold)
    ax.plot(w1_values, optimal_path, color='white', linewidth=4, linestyle='-',
            label='Optimal Strategy Trajectory', alpha=0.9)
    ax.plot(w1_values, optimal_path, color='black', linewidth=1, linestyle='-', alpha=0.5)  # outline

    # Annotations (English)
    # Zone 1: Purple Zone (Risk/Bad)
    ax.text(0.15, 80, 'DANGER ZONE\n(Overworking LBJ at 41)',
            color='white', fontsize=11, fontweight='bold', ha='center',
            bbox=dict(facecolor='#552583', alpha=0.7, edgecolor='white'))

    # Zone 2: Gold Zone (Reward/Good)
    ax.text(0.85, 45, 'OPTIMAL ZONE\n(Balanced Trio Usage)',
            color='black', fontsize=11, fontweight='bold', ha='center',
            bbox=dict(facecolor='#FDB927', alpha=0.7, edgecolor='black'))

    # Critical Insight Arrow
    ax.annotate('Reaves & Luka allow\nhigher intensity here', xy=(0.6, 38), xytext=(0.4, 20),
                arrowprops=dict(facecolor='white', shrink=0.05),
                color='white', fontsize=10, fontweight='bold')

    # Labels and Titles
    ax.set_title('Lakers Core Trio: Strategy Sensitivity Heatmap\n(Luka + LeBron + Reaves)',
                 fontsize=16, fontweight='bold', color='#2E003E', pad=20)
    ax.set_xlabel('Management Priority ($w_1$): Cash Flow Preference', fontsize=12, fontweight='bold')
    ax.set_ylabel('Roster Intensity / Usage Rate (%)', fontsize=12, fontweight='bold')

    # Legend
    ax.legend(loc='lower right', framealpha=0.9, facecolor='white', edgecolor='#552583')

    plt.tight_layout()
    plt.show()


plot_lakers_heatmap()