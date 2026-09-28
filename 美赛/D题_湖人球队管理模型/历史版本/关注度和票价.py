import numpy as np
import matplotlib.pyplot as plt

# ==========================================
# 1. 参数设置 (湖人配色)
# ==========================================
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'
LAKERS_BLACK = '#000000'
LAKERS_WHITE = '#FFFFFF'
BG_COLOR = '#F9F9F9'

# 关注度评分 (0 到 10 分)
# 0: 无人问津 (e.g., vs 摆烂队, 周二晚)
# 10: 世纪大战 (e.g., vs 凯尔特人总决赛, 詹姆斯破纪录之夜)
attention_score = np.linspace(0, 10, 500)

# === 定价模型 ===
base_price = 150  # 基础票价 (门槛价)

# 关注度溢价系数 (非线性增长：关注度越高，溢价越夸张)
# 使用指数函数模拟 "炒作效应 (Hype Effect)"
# 当关注度为0时，溢价为0；当关注度为10时，溢价可能达到 200% 甚至更高
premium_factor = 0.15 * (attention_score ** 1.6)

# 计算各部分价格
premium_price = base_price * premium_factor
total_price = base_price + premium_price

# ==========================================
# 2. 绘图代码 (堆叠面积图)
# ==========================================
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG_COLOR)
ax.set_facecolor(BG_COLOR)

# 绘制堆叠区域
# 底层：基础价值 (Base Value)
ax.fill_between(attention_score, 0, base_price,
                color=LAKERS_GOLD, alpha=0.8, label='Intrinsic Value (Base Price)')

# 上层：关注度溢价 (Attention Premium)
ax.fill_between(attention_score, base_price, total_price,
                color=LAKERS_PURPLE, alpha=0.9, label='Hype Premium (Star Power/Rivalry)')

# 绘制总价格曲线 (轮廓线)
ax.plot(attention_score, total_price, color=LAKERS_BLACK, linewidth=2.5, linestyle='-')

# ==========================================
# 3. 场景标注 (结合湖人队现实)
# ==========================================
# 定义关键场景点
scenarios = [
    (1.0, "vs Pistons\n(Tue Night)", 20),  # 低关注
    (4.5, "vs Clippers\n(Regular)", 60),  # 中等 (同城德比但普通场)
    (7.5, "vs Warriors\n(Curry visits)", 100),  # 高关注 (球星效应)
    (9.5, "vs Celtics\n(Rivalry/Xmas)", 140)  # 极高 (宿敌/圣诞)
]

for score, text, offset in scenarios:
    # 计算该分数下的价格
    idx = np.argmin(np.abs(attention_score - score))
    price = total_price[idx]

    # 画虚线指示
    ax.vlines(score, 0, price, colors='white', linestyles=':', linewidth=1.5, alpha=0.8)
    ax.scatter(score, price, color='white', edgecolor=LAKERS_PURPLE, s=80, zorder=10, linewidth=2)

    # 添加文本标签
    ax.annotate(f"{text}\n${price:.0f}",
                xy=(score, price), xytext=(score, price + offset),
                ha='center', va='bottom', fontsize=10, fontweight='bold', color='#333',
                arrowprops=dict(arrowstyle='-', color='#555', linewidth=1))

# ==========================================
# 4. 装饰与美化
# ==========================================
ax.set_title("Impact of Game Attention on Ticket Pricing (Hype Model)",
             fontsize=16, fontweight='bold', color=LAKERS_PURPLE, pad=25)

# 副标题解释模型
ax.text(0.5, 1.02, r"Model: $P_{total} = P_{base} + \beta \cdot (Attention)^{\gamma}$",
        transform=ax.transAxes, ha='center', fontsize=12, color='#666')

# 坐标轴标签
ax.set_xlabel("Game Attention Score (0-10)", fontsize=12, fontweight='bold')
ax.set_ylabel("Average Ticket Price ($)", fontsize=12, fontweight='bold')

# X轴刻度美化
ax.set_xticks(np.arange(0, 11, 1))
ax.set_xlim(0, 10.5)

# Y轴范围 (留出顶部空间给标签)
ax.set_ylim(0, np.max(total_price) * 1.25)

# 图例
ax.legend(loc='upper left', fontsize=11, frameon=True, facecolor='white', framealpha=0.95)

# 网格
ax.grid(axis='y', linestyle='--', alpha=0.3)

# 添加右侧注释箭头
ax.annotate('Exponential growth due to\nFOMO (Fear Of Missing Out)',
            xy=(8.5, (base_price + total_price[-100]) / 2), xytext=(11, total_price[-100]),
            xycoords='data', textcoords='data',
            arrowprops=dict(arrowstyle='->', color=LAKERS_PURPLE, lw=1.5),
            ha='left', va='center', fontsize=10, color=LAKERS_PURPLE, style='italic')

plt.tight_layout()
plt.show()


# ===========================================================
# 📊 票务动态定价模型分析报告 (Ticket Dynamic Pricing Report)
# ===========================================================
#
# 1. 图表核心逻辑：双层价值叠加
# -----------------------------------------------------------
# 该图表将票价结构拆分为两个部分（对应湖人配色）：
#
# 🟨 底部金色区域 (Intrinsic Value / Base Price):
#    - 代表球票的【基础价值】。
#    - 无论对手是谁（哪怕是活塞队），只要是湖人主场，每张票至少值 $150。
#    - 这部分是由于洛杉矶的市场地位、球馆设施等固定因素决定的，是收入的"安全垫"。
#
# 🟪 顶部紫色区域 (Hype Premium / Star Power):
#    - 代表由【关注度/球星效应】带来的溢价。
#    - 这是一个非线性增长区域（指数函数 Attention^1.6）。
#    - 含义：当关注度从 5 提升到 10 时，价格不是翻倍，而是翻了 3-4 倍。这就是"流量经济"的本质。
#
# 2. 关键场景数据点解读
# -----------------------------------------------------------
# 📍 场景 A: 关注度 1.0 (vs Pistons / 周二晚)
#    - 票价构成：$150 (基础) + ~$22 (微小溢价) ≈ $172
#    - 结论：对于缺乏看点的比赛，票价回归到仅由品牌保底。
#
# 📍 场景 B: 关注度 4.5 (vs Clippers / 常规赛)
#    - 票价构成：$150 (基础) + ~$100 (中等溢价) ≈ $250
#    - 结论：普通的强队交手，溢价能够覆盖基础票价的一大半。
#
# 📍 场景 C: 关注度 9.5 (vs Celtics / 圣诞大战 / 宿敌)
#    - 票价构成：$150 (基础) + ~$820 (巨额溢价!) ≈ $970+
#    - 结论：紫色区域占据了总价格的 80% 以上。
#    - 💡 核心洞察：在这种高关注度比赛中，球队卖的不是"篮球比赛"，卖的是"历史时刻"和"稀缺性"。
#
# 3. 经济学模型总结 (Model Insight)
# -----------------------------------------------------------
# 该模型揭示了为什么你需要勒布朗（LeBron）这样的超级巨星：
# 虽然他随着年龄增长，竞技能力 ($S_i$) 可能下降，但他带来的关注度 ($F_i$) 能够将比赛推向图表的右侧（8-10分区域）。
#
# 在右侧区域，紫色部分的【溢价利润】是呈指数级爆炸的。这就是为什么从商业角度看，维持高关注度比单纯赢球更能带来暴利。
#
# ===========================================================