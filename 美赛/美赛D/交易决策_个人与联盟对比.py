import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import os
import glob
import sys
import warnings

# 基础配置：关闭警告、显示所有列
warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)


# ==========================================
# 1. 全局配置（仅需修改目标球员，路径仅用于读取球员数据）
# ==========================================
class Config:
    # 路径配置：仅用于读取目标球员的个人数据
    PATH_TRADE_TARGETS = r"C:\Users\28137\Desktop\交易决策"

    # 🔥 仅需修改此处：单名新援姓名（模糊匹配，忽略大小写）
    TARGET_PLAYER = "Nesmith"  # 示例：Dillion / Siakam / Nesmith

    # 🎨 配色配置（刻度线专属配色，视觉柔和不抢镜）
    COLOR_LAKERS_GOLD = '#FDB927'    # 新援主色（核心视觉）
    COLOR_LAKERS_PURPLE = '#552583'  # 联盟平均色（基准对比）
    COLOR_TEXT = '#333333'           # 图表文字主色
    COLOR_GRID = '#EEEEEE'           # 极坐标径向网格线色
    COLOR_CIRCLE = '#C0C0C0'         # 同心圆刻度线色（浅灰）
    COLOR_CIRCLE_ALPHA = 0.6         # 同心圆透明度（柔和不刺眼）
    COLOR_EDGE = '#DDDDDD'           # 边框色


# ==========================================
# 2. 核心配置：指标映射+2025-26NBA球员个人场均平均数据
# ==========================================
# 雷达图保留英文缩写（专业可视化），控制台输出中文全称
METRIC_MAP = {
    'MP': '场均出场时间',
    'PTS': '场均得分',
    'FG%': '投篮命中率',
    '3P%': '三分命中率',
    'TRB': '场均篮板',
    'AST': '场均助攻',
    'STL': '场均抢断',
    'BLK': '场均盖帽'
}
METRICS_EN = list(METRIC_MAP.keys())  # 雷达图英文指标
METRICS_CN = list(METRIC_MAP.values())# 控制台中文指标

# 🚨 2025-26赛季NBA**球员个人场均平均数据**（纯球员维度，非球队）
NBA_2025_26_PLAYER_AVG = {
    'MP': 24.1,  'PTS': 13.9,  'FG%': 0.448,  '3P%': 0.354,
    'TRB': 5.5,  'AST': 2.9,   'STL': 0.7,    'BLK': 0.4
}
# 🚨 同心圆刻度线配置（仅保留线，无数值/标签）
CIRCLE_TICKS = [20, 50, 80, 100]    # 同心圆刻度线位置（50为联盟平均基准）


# ==========================================
# 3. 核心工具函数（与原版本一致，兼容球员数据读取）
# ==========================================
def smart_read_player_file(file_path):
    """智能读取球员数据（兼容html/xlsx/xls）"""
    df = pd.DataFrame()
    try:
        dfs = pd.read_html(file_path)
        if dfs: df = dfs[0]
    except:
        try:
            df = pd.read_excel(file_path)
        except:
            return pd.DataFrame()

    if df.empty: return df

    # 自动识别表头行（包含Season+PTS/Tm）
    header_idx = -1
    for i in range(min(5, len(df))):
        row_str = df.iloc[i].astype(str).tolist()
        if 'Season' in row_str and ('PTS' in row_str or 'Tm' in row_str):
            header_idx = i
            break

    if header_idx != -1:
        df.columns = df.iloc[header_idx]
        df = df[header_idx + 1:].reset_index(drop=True)

    df.columns = [str(c).strip() for c in df.columns]
    return df


def load_single_target_player():
    """加载单名新援数据，精准匹配TARGET_PLAYER（模糊匹配，忽略大小写）"""
    root_path = Config.PATH_TRADE_TARGETS
    if not os.path.exists(root_path):
        print(f"❌ 新援数据路径不存在：{root_path}")
        return pd.Series(dtype='object')

    print(f"📂 正在加载单名新援数据：{Config.TARGET_PLAYER}...", end=" ")
    # 遍历球员文件夹
    for folder in os.scandir(root_path):
        if not folder.is_dir():
            continue
        player_folder_name = folder.path
        player_name = os.path.basename(player_folder_name)

        # 精准模糊匹配（忽略大小写，兼容文件夹名后缀）
        if Config.TARGET_PLAYER.lower() in player_name.lower():
            # 读取该球员所有数据文件
            files = glob.glob(os.path.join(player_folder_name, "*.xls*"))
            df_player = pd.DataFrame()
            for f in files:
                temp = smart_read_player_file(f)
                if not temp.empty:
                    df_player = pd.concat([df_player, temp], ignore_index=True)

            if df_player.empty:
                print(f"❌ {Config.TARGET_PLAYER} 无有效数据文件")
                return pd.Series(dtype='object')

            # 数据清洗（保证基础数据有效性）
            if 'Season' in df_player.columns:
                df_player = df_player.dropna(subset=['Season'])
            if 'PTS' in df_player.columns:
                df_player = df_player[pd.to_numeric(df_player['PTS'], errors='coerce').notna()]
            df_player = df_player[df_player['Season'] != 'Season']
            if df_player.empty:
                print(f"❌ {Config.TARGET_PLAYER} 数据清洗后无有效内容")
                return pd.Series(dtype='object')

            # 取最新赛季数据（最后一行，反映最新状态）
            last_season = df_player.iloc[-1]
            last_season['Player'] = player_name

            # 数值列类型转换（核心基础指标，异常值置0，适配命中率转换）
            core_cols = METRICS_EN  # 仅转换雷达图用到的8大指标
            for col in core_cols:
                if col in last_season.index:
                    try:
                        val_str = str(last_season[col]).strip()
                        # 命中率特殊处理：百分比字符串转小数（如45.3%→0.453）
                        if '%' in val_str:
                            last_season[col] = float(val_str.replace('%', '')) / 100
                        else:
                            last_season[col] = float(val_str)
                    except:
                        last_season[col] = 0.0

            print(f"✅ 加载成功（球员名称：{player_name}）")
            return last_season

    # 未找到匹配球员
    print(f"❌ 未找到 {Config.TARGET_PLAYER} 对应的球员文件夹")
    return pd.Series(dtype='object')


# ==========================================
# 4. 核心绘图：仅保留灰色虚线同心圆刻度线（无任何数值/标签）
# ==========================================
def plot_single_player_vs_league(player_series, league_avg):
    """
    绘制单名新援与2025-26NBA球员平均数据的八边形雷达图
    核心修改：移除所有刻度数值/标签，仅保留灰色虚线同心圆刻度线
    """
    player_name = player_series['Player']
    num_vars = len(METRICS_EN)

    # --------------------------
    # 数据预处理与兜底（适配基础数据，保证指标完整有效）
    # --------------------------
    player_stats = {}
    for m in METRICS_EN:
        val = player_series.get(m, 0.0)
        # 命中率兜底：低于0.2或高于1.0置为联盟平均（避免异常值）
        if m in ['FG%', '3P%']:
            if val < 0.2 or val > 1.0:
                val = league_avg[m]
        # 其他指标兜底：负值置0（出场时间、得分等不能为负）
        elif val < 0:
            val = 0.0
        player_stats[m] = val

    # --------------------------
    # 数据归一化（适配雷达图0-100刻度，所有指标越高越好）
    # --------------------------
    def normalize(stats_dict):
        """归一化：将指标转换为0-100刻度，联盟平均固定在50刻度"""
        vals = []
        for m in METRICS_EN:
            val = stats_dict[m]
            avg = league_avg[m]
            avg = 0.01 if avg == 0 else avg  # 避免除零错误
            ratio = val / avg
            # 归一化到10-100区间，防止极值溢出
            norm_val = 50 + (ratio - 1.0) * 80
            vals.append(np.clip(norm_val, 10, 100))
        return vals

    # 归一化并闭合雷达图曲线（极坐标要求：首尾相连）
    league_vals = normalize(league_avg)
    player_vals = normalize(player_stats)
    angles = np.linspace(0, 2 * pi, num_vars, endpoint=False).tolist()
    league_vals += league_vals[:1]
    player_vals += player_vals[:1]
    angles += angles[:1]

    # --------------------------
    # 画布与极坐标设置（湖人专业风格）
    # --------------------------
    plt.style.use('bmh')
    fig, ax = plt.subplots(figsize=(11, 11), subplot_kw=dict(polar=True))
    ax.set_theta_offset(pi / 2)    # 起始方向向上
    ax.set_theta_direction(-1)     # 顺时针旋转（符合中文阅读习惯）
    ax.set_ylim(0, 110)            # 径向范围匹配刻度线位置
    ax.spines['polar'].set_visible(False)  # 隐藏极坐标外轴线

    # --------------------------
    # 🚨 核心修改：仅绘制灰色虚线同心圆刻度线（无数值/无标签）
    # --------------------------
    # 隐藏所有径向刻度的数值和标签，仅保留刻度线
    ax.set_yticks(CIRCLE_TICKS)
    ax.set_yticklabels([])  # 清空刻度标签，彻底移除数值
    ax.tick_params(axis='y', length=0)  # 隐藏刻度小短线，视觉更干净
    # 循环绘制灰色虚线同心圆：仅线，无任何文字/标识
    for tick in CIRCLE_TICKS:
        ax.plot(angles, [tick]*len(angles),
                color=Config.COLOR_CIRCLE,
                linestyle='--',  # 虚线样式，与需求一致
                linewidth=1.2,   # 线宽适中，不粗不细
                alpha=Config.COLOR_CIRCLE_ALPHA,  # 透明度柔和，不抢镜
                zorder=1)  # 图层置最低，避免遮挡核心数据

    # --------------------------
    # 绘制核心数据层（联盟平均+球员数据，分层展示，视觉聚焦）
    # --------------------------
    # 1. 联盟平均层（紫色虚线+浅填充，基准背景，zorder=2）
    ax.plot(angles, league_vals, color=Config.COLOR_LAKERS_PURPLE, linewidth=2.5,
            linestyle='--', marker='o', markersize=5, label='2025-26 League Avg', zorder=2)
    ax.fill(angles, league_vals, color=Config.COLOR_LAKERS_PURPLE, alpha=0.08, zorder=1)

    # 2. 新援核心层（湖人金粗线+方形标记，视觉焦点，zorder=5）
    ax.plot(angles, player_vals, color=Config.COLOR_LAKERS_GOLD, linewidth=4.5,
            marker='s', markersize=7, label=player_name, zorder=5)
    ax.fill(angles, player_vals, color=Config.COLOR_LAKERS_GOLD, alpha=0.4, zorder=4)

    # --------------------------
    # 差值标注+坐标轴美化（图表全英文，注释清晰）
    # --------------------------
    # 差值标注（彩色加粗，绿色优于联盟/红色弱于联盟）
    for i, m in enumerate(METRICS_EN):
        diff = player_stats[m] - league_avg[m]
        color = 'darkgreen' if diff > 0 else 'darkred'
        # 数值格式化：命中率保留3位小数，其余保留1位
        if m in ['FG%', '3P%']:
            diff_text = f"{diff:+.3f}"
        else:
            diff_text = f"{diff:+.1f}"
        # 标注位置：新援数据点外侧10个单位，避免遮挡刻度线和数据层
        ax.text(angles[i], player_vals[i] + 10, diff_text, color=color,
                weight='bold', size=11, ha='center', va='center',
                bbox=dict(facecolor='white', alpha=0.75, edgecolor='none', pad=2))

    # 极坐标指标刻度（英文缩写，加粗大字体，黑色清晰）
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(METRICS_EN, size=14, weight='bold', color=Config.COLOR_TEXT)
    # 优化径向网格线：浅灰色、低透明度，不与同心圆刻度线冲突
    ax.grid(color=Config.COLOR_GRID, linestyle='--', alpha=0.5, linewidth=1)

    # --------------------------
    # 标题与图例（湖人专属风格，图表全英文）
    # --------------------------
    main_title = f"LAKERS TRADE TARGET: {player_name.upper()} VS 2025-26 NBA PLAYER AVG"
    plt.suptitle(main_title, size=18, weight='black', color=Config.COLOR_LAKERS_PURPLE, y=0.98)
    sub_title = "   "
    plt.title(sub_title, size=12, color='#666666', pad=30)

    # 图例：底部居中，带阴影，紫金配色清晰，无多余标识
    legend = ax.legend(loc='lower center', bbox_to_anchor=(0.5, -0.12),
                       ncol=2, frameon=True, shadow=True, fontsize=12)
    legend.get_frame().set_edgecolor(Config.COLOR_EDGE)
    legend.get_frame().set_facecolor('white')

    # --------------------------
    # 控制台输出：全中文，无缩写，命中率百分比显示
    # --------------------------
    print(f"\n{'=' * 80}")
    print(f"{'[湖人单球员对比分析] ' + player_name + ' VS 2025-26NBA球员平均':^80}")
    print(f"{'=' * 80}")
    print(f"{'指标名称':<12} {'联盟球员平均':<15} {'球员个人数据':<15} {'差值':<12} {'表现评价'}")
    print(f"{'-' * 80}")
    for m_en, m_cn in METRIC_MAP.items():
        avg_val = league_avg[m_en]
        ply_val = player_stats[m_en]
        diff = ply_val - avg_val
        # 数值格式化：命中率显示百分比，其余保留1位小数
        if m_en in ['FG%', '3P%']:
            avg_str = f"{avg_val:.1%}"
            ply_str = f"{ply_val:.1%}"
            diff_str = f"{diff:+.3f}"
        else:
            avg_str = f"{avg_val:.1f}"
            ply_str = f"{ply_val:.1f}"
            diff_str = f"{diff:+.1f}"
        # 表现评价：带表情符号，直观判断优劣
        performance = "✅ 优于联盟平均" if diff > 0 else "❌ 弱于联盟平均"
        print(f"{m_cn:<12} {avg_str:<15} {ply_str:<15} {diff_str:<12} {performance}")
    print(f"{'=' * 80}")

    # --------------------------
    # 保存高清图表并显示
    # --------------------------
    plt.tight_layout()
    save_filename = f"湖人_{player_name}_2025-26NBA球员平均对比雷达图.png"
    plt.savefig(save_filename, dpi=300, bbox_inches='tight')
    print(f"\n✅ 高清雷达图已保存：{os.path.abspath(save_filename)}")
    plt.show()


# ==========================================
# 5. 主程序执行入口（极简操作，一键运行）
# ==========================================
if __name__ == "__main__":
    print("🚀 湖人单新援vs2025-26NBA球员平均 雷达图分析程序（仅刻度线版）启动")
    # 步骤1：加载单名新援数据
    target_player = load_single_target_player()
    if target_player.empty:
        sys.exit("❌ 无有效新援数据，程序退出")
    # 步骤2：加载2025-26NBA球员个人平均数据
    league_average = NBA_2025_26_PLAYER_AVG
    print(f"📊 已加载2025-26赛季NBA联盟球员个人场均平均数据（纯球员维度）")
    # 步骤3：绘制仅带灰色虚线同心圆刻度线的雷达图
    plot_single_player_vs_league(target_player, league_average)
    print("\n🎉 湖人单球员vs联盟平均对比分析完成！")