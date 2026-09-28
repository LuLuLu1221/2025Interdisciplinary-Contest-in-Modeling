import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter

# ==========================================
# 1. 参数设置 (湖人配色 & 经济学参数)
# ==========================================
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'
LAKERS_BLACK = '#000000'
BG_COLOR = '#F5F5F5'  # 浅灰背景，模仿论文常用风格

# 模拟模型一输出的胜率范围 (0% 到 100%)
win_probs = np.linspace(0, 1, 500)

# 基础票价 (假设均价)
base_price = 200

# === 核心定价逻辑：高斯函数 ===
# alpha: 最大溢价比例 (0.25 表示最高涨价 25%)
alpha = 0.25
# sigma: 敏感度宽度 (值越大曲线越平缓，值越小峰值越尖锐)
sigma = 0.22

# 计算动态定价乘数
price_multiplier = 1 + alpha * np.exp(-((win_probs - 0.5)**2) / (2 * sigma**2))

# 计算最终价格
final_prices = base_price * price_multiplier

# ==========================================
# 2. 绘图代码
# ==========================================
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# 绘制主曲线 (价格随胜率的变化)
ax.plot(win_probs, final_prices, color=LAKERS_PURPLE, linewidth=3.5, zorder=10,
        label='Dynamic Price Curve')

# 填充颜色 (金黄色填充，代表价值)
ax.fill_between(win_probs, base_price, final_prices, color=LAKERS_GOLD, alpha=0.4, zorder=5)
ax.fill_between(win_probs, 0, base_price, color='#E0E0E0', alpha=0.3, zorder=1) # 基础价格区域

# ==========================================
# 3. 关键点标注 (Annotate Key Scenarios)
# ==========================================
# 场景 A: 势均力敌 (50% 胜率) -> 最高价
idx_peak = np.argmin(np.abs(win_probs - 0.5))
peak_price = final_prices[idx_peak]
ax.scatter([0.5], [peak_price], color='#D40000', s=100, zorder=15, edgecolors='white', linewidth=2)
ax.annotate(f'Peak Suspense (50% Win Rate)\nMax Price: ${peak_price:.0f} (+{alpha:.0%})',
            xy=(0.5, peak_price), xytext=(0.5, peak_price + 15),
            ha='center', va='bottom', fontsize=11, fontweight='bold', color='#D40000',
            arrowprops=dict(arrowstyle='->', color='#D40000', lw=1.5))

# 场景 B: 必胜局/虐菜局 (90% 胜率) -> 价格回落
idx_high = np.argmin(np.abs(win_probs - 0.9))
high_price = final_prices[idx_high]
ax.scatter([0.9], [high_price], color=LAKERS_PURPLE, s=80, zorder=15)
ax.annotate(f'Blowout Game (90%)\nPrice drops: ${high_price:.0f}',
            xy=(0.9, high_price), xytext=(0.95, high_price + 20),
            ha='right', va='bottom', fontsize=10, color=LAKERS_BLACK,
            arrowprops=dict(arrowstyle='->', color=LAKERS_PURPLE))

# 场景 C: 必败局/打宇宙队 (10% 胜率) -> 价格回落
# 注意：现实中打强队虽然胜率低，但可能有球星效应，这里仅展示纯胜率模型
idx_low = np.argmin(np.abs(win_probs - 0.1))
low_price = final_prices[idx_low]
ax.scatter([0.1], [low_price], color=LAKERS_PURPLE, s=80, zorder=15)
ax.annotate(f'Underdog Game (10%)\nPrice drops: ${low_price:.0f}',
            xy=(0.1, low_price), xytext=(0.05, low_price + 20),
            ha='left', va='bottom', fontsize=10, color=LAKERS_BLACK,
            arrowprops=dict(arrowstyle='->', color=LAKERS_PURPLE))

# ==========================================
# 4. 图表美化
# ==========================================
# 标题
ax.set_title("Pricing Strategy Based on Outcome Uncertainty (Win Rate)",
             fontsize=16, fontweight='bold', color=LAKERS_PURPLE, pad=20)
ax.text(0.5, 1.02, "Model Logic: Fans pay more for competitive balance (50/50 games)",
        transform=ax.transAxes, ha='center', fontsize=11, color='#666')

# 坐标轴设置
ax.set_xlabel("Predicted Lakers Win Probability (from Model 1)", fontsize=12, fontweight='bold')
ax.set_ylabel("Recommended Average Ticket Price ($)", fontsize=12, fontweight='bold')

# X轴显示百分比
ax.xaxis.set_major_formatter(PercentFormatter(1.0))
ax.set_xlim(0, 1)
ax.set_ylim(base_price * 0.9, base_price * (1 + alpha + 0.1))

# 网格
ax.grid(True, linestyle='--', alpha=0.5, color='gray')

# 添加基准线
ax.axhline(base_price, color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
ax.text(0.02, base_price + 2, "Base Price (No Premium)", fontsize=10, color='gray', style='italic')

plt.tight_layout()
# plt.savefig('win_rate_pricing_curve.png', dpi=300)
plt.show()