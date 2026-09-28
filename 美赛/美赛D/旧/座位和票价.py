import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

# ==========================================
# 1. 配置参数与颜色 (湖人配色)
# ==========================================
LAKERS_PURPLE = '#552583'
LAKERS_GOLD = '#FDB927'
COURT_COLOR = '#CBB67C'
COURT_LINES = 'white'

lakers_cmap = LinearSegmentedColormap.from_list("LakersPricing", [LAKERS_PURPLE, LAKERS_GOLD], N=256)

# 放大系数
scale_factor = 1.25
real_w = 28.65
real_h = 15.24
w = real_w * scale_factor  # ~35.8
h = real_h * scale_factor  # ~19.0
lw = 2.0

# 几何参数
straight_length = w + 8  # ~44
# 调整半径，确保每一层有足够的宽度容纳文字
ring_radii = np.array([100, 84, 68, 52, 36, 22])
zone_prices = np.array([80, 180, 450, 1200, 4500])

norm = plt.Normalize(zone_prices.min(), zone_prices.max())

# ==========================================
# 2. 绘图初始化
# ==========================================
# 稍微增加高度，防止标题重叠
fig, ax = plt.subplots(figsize=(14, 11))
ax.set_aspect('equal')
ax.axis('off')

# 设置显示范围 (关键：顶部留出更多空间)
max_r = ring_radii[0]
limit_x = max_r + straight_length / 2 + 5
limit_y_bottom = max_r + 5
limit_y_top = max_r + 20  # 顶部多留20单位给标题
ax.set_xlim(-limit_x, limit_x)
ax.set_ylim(-limit_y_bottom, limit_y_top)
fig.patch.set_facecolor('white')


# ==========================================
# 3. 绘图函数 (无缝平滑版)
# ==========================================
def draw_capsule_smooth(ax, radius, length, color, zorder):
    """绘制无内部接缝的胶囊"""
    l_half = length / 2

    # 填充 (无边框)
    rect = patches.Rectangle((-l_half, -radius), length, 2 * radius,
                             facecolor=color, edgecolor='none', zorder=zorder)
    ax.add_patch(rect)

    left_wedge = patches.Wedge((-l_half, 0), radius, 90, 270,
                               facecolor=color, edgecolor='none', zorder=zorder)
    ax.add_patch(left_wedge)

    right_wedge = patches.Wedge((l_half, 0), radius, 270, 90,
                                facecolor=color, edgecolor='none', zorder=zorder)
    ax.add_patch(right_wedge)

    # 外轮廓描边
    line_width = 1.0
    line_color = 'white'

    ax.plot([-l_half, l_half], [radius, radius], color=line_color, linewidth=line_width, zorder=zorder + 0.1)
    ax.plot([-l_half, l_half], [-radius, -radius], color=line_color, linewidth=line_width, zorder=zorder + 0.1)

    left_arc = patches.Arc((-l_half, 0), 2 * radius, 2 * radius, angle=0, theta1=90, theta2=270,
                           color=line_color, linewidth=line_width, zorder=zorder + 0.1)
    ax.add_patch(left_arc)

    right_arc = patches.Arc((l_half, 0), 2 * radius, 2 * radius, angle=0, theta1=270, theta2=90,
                            color=line_color, linewidth=line_width, zorder=zorder + 0.1)
    ax.add_patch(right_arc)


# ==========================================
# 4. 绘制环形座位区
# ==========================================
for i in range(len(zone_prices)):
    r_outer = ring_radii[i]
    r_inner = ring_radii[i + 1] if i + 1 < len(ring_radii) else 0
    price = zone_prices[i]

    color_val = norm(price)
    ring_color = lakers_cmap(color_val)

    draw_capsule_smooth(ax, r_outer, straight_length, ring_color, zorder=10 + i)

    # --- 标签位置优化 ---
    # 计算几何中心半径
    mid_r = (r_outer + r_inner) / 2

    # 角度设置 (45度)
    angle_deg = 45
    angle_rad = np.deg2rad(angle_deg)

    # 计算坐标
    label_x = (straight_length / 2) + mid_r * np.cos(angle_rad)
    label_y = mid_r * np.sin(angle_rad)

    text_color = 'white' if color_val < 0.5 else 'black'

    # --- 字体大小动态调整 ---
    # 根据环的宽度调整字体大小，防止压线
    ring_width = r_outer - r_inner
    if ring_width < 15:
        font_size = 9  # 窄环用小字
    elif ring_width < 20:
        font_size = 10  # 中环用中字
    else:
        font_size = 12  # 宽环用大字

    ax.text(label_x, label_y, f"${price}", ha='center', va='center',
            color=text_color, fontweight='bold', fontsize=font_size, zorder=50)

# ==========================================
# 5. 绘制中心球场
# ==========================================
center_r = ring_radii[-1]
draw_capsule_smooth(ax, center_r, straight_length, '#f5f5f5', zorder=60)

# 绘制球场
court = patches.Rectangle((-w / 2, -h / 2), w, h, facecolor=COURT_COLOR, edgecolor='none', zorder=61)
ax.add_patch(court)

border = patches.Rectangle((-w / 2, -h / 2), w, h, fill=False, edgecolor=COURT_LINES, linewidth=lw, zorder=62)
ax.add_patch(border)
ax.plot([0, 0], [-h / 2, h / 2], color=COURT_LINES, linewidth=lw, zorder=62)
center_circle = patches.Circle((0, 0), radius=1.8 * scale_factor, fill=False, edgecolor=COURT_LINES, linewidth=lw,
                               zorder=62)
ax.add_patch(center_circle)


def draw_half_court(direction=1):
    key_w = 4.9 * scale_factor
    key_h = 5.8 * scale_factor
    key_y = -key_w / 2
    key_x = (w / 2 - key_h) if direction == 1 else -w / 2

    key_rect = patches.Rectangle((key_x, key_y), key_h, key_w, fill=False, edgecolor=COURT_LINES, linewidth=lw,
                                 zorder=62)
    ax.add_patch(key_rect)

    arc_r = 7.24 * scale_factor
    hoop_x = (w / 2 - 1.575 * scale_factor) * direction
    theta1 = 90 if direction == 1 else 270
    theta2 = 270 if direction == 1 else 90
    arc = patches.Arc((hoop_x, 0), arc_r * 2, arc_r * 2, angle=0, theta1=theta1, theta2=theta2, color=COURT_LINES,
                      linewidth=lw, zorder=62)
    ax.add_patch(arc)


draw_half_court(1)
draw_half_court(-1)

# ==========================================
# 6. 装饰 (解决重叠问题的关键)
# ==========================================
# 调整 y 位置参数，也可以使用 pad 参数
plt.title("Lakers Arena Dynamic Pricing: Stadium View", fontsize=18, fontweight='bold', color=LAKERS_PURPLE, pad=20)

# 颜色条
cax = fig.add_axes([0.25, 0.05, 0.5, 0.03])
sm = plt.cm.ScalarMappable(cmap=lakers_cmap, norm=norm)
sm.set_array([])
cbar = plt.colorbar(sm, cax=cax, orientation='horizontal')
cbar.set_label('Ticket Price ($)', fontsize=12, fontweight='bold')
cbar.outline.set_visible(False)

# plt.savefig('lakers_stadium_final.png', dpi=300, bbox_inches='tight')
plt.show()