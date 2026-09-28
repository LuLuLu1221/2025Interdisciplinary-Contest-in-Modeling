import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ==========================================
# 1. Model Configuration (Based on your formulas)
# ==========================================
class Config:
    # --- Competitive Model ---
    LAMBDA = 0.005
    S_OPP = 20.0

    # --- Revenue Model ---
    ALPHA = 150.0
    BETA = 8.0
    THETA_E = 120.0

    # --- Objective Function ---
    W1 = 0.6
    W2 = 0.4
    GAMMA = 0.90

    # --- Operations ---
    SALARY_CAP = 180.0
    TAX_RATE = 1.5
    LOAD_MGMT_THRESHOLD = 0.35


# ==========================================
# 2. Player Class (State Transition)
# ==========================================
class Player:
    def __init__(self, name, age, s_i, f_i, minutes, g_played):
        self.name = name
        self.age = age
        self.s_i_base = s_i
        self.s_i_current = s_i
        self.f_i = f_i
        self.minutes_per_season = minutes
        self.games = g_played
        self.risk_score = 0.1

    @property
    def x_i(self):
        if self.games == 0: return 0
        return (self.minutes_per_season / self.games) / 48.0

    def update_phase3_aging(self):
        # Phase 3: Aging Logic
        decay_rate = 0.0
        if self.age >= 32:
            decay_rate = 0.05 + (self.age - 32) * 0.02
        elif self.age < 24:
            decay_rate = -0.05

        self.s_i_current = self.s_i_current * (1 - decay_rate)
        self.age += 1
        self.risk_score = 0.1 + max(0, (self.age - 28) * 0.05)

    def apply_phase2_load_management(self):
        # Phase 2: Load Management
        if self.risk_score > Config.LOAD_MGMT_THRESHOLD:
            self.minutes_per_season *= 0.8
            return True
        return False


# ==========================================
# 3. Team Environment & MDP Engine
# ==========================================
class TeamEnv:
    def __init__(self, roster_data, initial_brand_val):
        self.roster = [Player(**p) for p in roster_data]
        self.brand_value = initial_brand_val
        self.year = 0
        self.history = {'Year': [], 'Revenue': [], 'Profit': [], 'WinRate': [], 'Z': []}
        self.cumulative_z = 0

    def calculate_metrics(self):
        raw_talent = sum(p.s_i_current * p.x_i for p in self.roster)
        friction = Config.LAMBDA * (raw_talent ** 2)
        t_perf = raw_talent - friction

        win_prob = 1 / (1 + np.exp(-0.3 * (t_perf - Config.S_OPP)))

        rev_win = Config.ALPHA * np.log(1 + max(0.1, t_perf))
        rev_comm = Config.BETA * sum(p.f_i * p.x_i for p in self.roster)
        r_total = rev_win + rev_comm + Config.THETA_E

        salaries = sum(p.s_i_current * 4.0 + p.f_i * 2.0 for p in self.roster)
        tax = max(0, (salaries - Config.SALARY_CAP) * Config.TAX_RATE)
        cost = salaries + tax + 50

        return t_perf, win_prob, r_total, cost

    def step_simulation(self):
        print(f"\n--- Season {self.year + 1} Simulation ---")

        # Phase 1
        top_commercial = sorted(self.roster, key=lambda x: x.f_i, reverse=True)[0]

        # Phase 2
        load_managed_players = []
        for p in self.roster:
            if p.apply_phase2_load_management():
                load_managed_players.append(p.name)

        t_perf, win_prob, revenue, cost = self.calculate_metrics()
        profit = revenue - cost

        market_growth = 1.05
        performance_mult = 1.0 + (win_prob - 0.5) * 0.5
        new_brand_val = self.brand_value * market_growth * performance_mult
        delta_v = new_brand_val - self.brand_value

        step_z = (Config.GAMMA ** self.year) * (Config.W1 * profit + Config.W2 * delta_v)
        self.cumulative_z += step_z

        self.history['Year'].append(self.year)
        self.history['Revenue'].append(revenue)
        self.history['Profit'].append(profit)
        self.history['WinRate'].append(win_prob)
        self.history['Z'].append(self.cumulative_z)

        print(f"   -> Win%: {win_prob * 100:.1f}% | Profit: ${profit:.1f}M | Delta V: ${delta_v:.1f}M")

        # Phase 3
        for p in self.roster:
            p.update_phase3_aging()

        self.brand_value = new_brand_val
        self.year += 1


# ==========================================
# 4. Data Initialization
# ==========================================
roster_data = [
    {'name': 'Luka Doncic', 'age': 26, 's_i': 8.5, 'f_i': 9.0, 'minutes': 1380, 'g_played': 38},
    {'name': 'LeBron James', 'age': 41, 's_i': 7.5, 'f_i': 10.0, 'minutes': 962, 'g_played': 29},
    {'name': 'Austin Reaves', 'age': 27, 's_i': 6.5, 'f_i': 7.8, 'minutes': 812, 'g_played': 23},
    {'name': 'Deandre Ayton', 'age': 27, 's_i': 6.8, 'f_i': 5.8, 'minutes': 1161, 'g_played': 41},
    {'name': 'Rui Hachimura', 'age': 27, 's_i': 5.9, 'f_i': 7.5, 'minutes': 1084, 'g_played': 36},
    {'name': 'D. Knecht', 'age': 24, 's_i': 4.2, 'f_i': 4.0, 'minutes': 458, 'g_played': 37},
    {'name': 'J. Vanderbilt', 'age': 26, 's_i': 6.2, 'f_i': 5.0, 'minutes': 720, 'g_played': 37},
]

# ==========================================
# 5. Run Simulation
# ==========================================
env = TeamEnv(roster_data, initial_brand_val=6500.0)
T_YEARS = 5
for _ in range(T_YEARS):
    env.step_simulation()

# ==========================================
# 6. Visualization (UPDATED: English & Gold/Purple)
# ==========================================
df_res = pd.DataFrame(env.history)

# Define Theme Colors (Lakers Style)
COLOR_PURPLE = '#552583'  # Lakers Purple
COLOR_GOLD = '#FDB927'  # Lakers Gold

plt.style.use('default')  # Reset style to ensure clean background
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# --- Graph 1: Profit vs Win Rate ---
ax1.set_title("MDP Simulation: Financial vs Competitive", fontsize=12, fontweight='bold')
ax1.set_xlabel("Year (Future)")

# Left Y-Axis: Profit (Purple)
ax1.set_ylabel("Annual Profit ($ Million)", color=COLOR_PURPLE, fontweight='bold')
ax1.plot(df_res['Year'], df_res['Profit'], marker='o', linestyle='-', linewidth=2.5, color=COLOR_PURPLE,
         label='Annual Profit ($\Pi_t$)')
ax1.tick_params(axis='y', labelcolor=COLOR_PURPLE)
ax1.grid(True, linestyle=':', alpha=0.6)

# Right Y-Axis: Win Rate (Gold)
ax1_twin = ax1.twinx()
ax1_twin.set_ylabel("Win Rate (%)", color='#B8860B',
                    fontweight='bold')  # Use a slightly darker gold for text readability
ax1_twin.plot(df_res['Year'], df_res['WinRate'] * 100, marker='s', linestyle='--', linewidth=2.5, color=COLOR_GOLD,
              label='Win Rate (%)')
ax1_twin.tick_params(axis='y', labelcolor='#B8860B')

# Combined Legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax1_twin.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc='center right', frameon=True)

# --- Graph 2: Cumulative Z ---
ax2.set_title(r"Objective Function Value: $Z = \Sigma \gamma^t (w_1 \Pi + w_2 \Delta V)$", fontsize=12,
              fontweight='bold')
ax2.set_xlabel("Year (Future)")
ax2.set_ylabel("Cumulative Strategic Value (Z)", fontweight='bold')

# Plot Line (Purple) and Fill (Gold)
ax2.plot(df_res['Year'], df_res['Z'], marker='D', linestyle='-', linewidth=2, color=COLOR_PURPLE, label='Cumulative Z')
ax2.fill_between(df_res['Year'], df_res['Z'], color=COLOR_GOLD, alpha=0.4)  # Gold fill

# Annotate values
for i, txt in enumerate(df_res['Z']):
    ax2.annotate(f"{txt:.0f}", (df_res['Year'][i], df_res['Z'][i]),
                 xytext=(0, 10), textcoords='offset points', ha='center', color='black', fontweight='bold')

ax2.grid(True, linestyle=':', alpha=0.6)
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()