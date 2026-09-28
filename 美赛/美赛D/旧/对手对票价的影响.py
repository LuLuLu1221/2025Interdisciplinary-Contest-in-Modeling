import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO


# --- 1. 生成底图 (保持不变) ---
def create_base_chart():
    # 数据准备
    x = np.linspace(0, 10, 500)
    P_base = 150
    beta = 5.5
    gamma = 2.2
    y_total = P_base + beta * (x ** gamma)
    y_base = np.full_like(x, P_base)

    # 画布设置 (高清)
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # 绘制面积区域
    ax.fill_between(x, 0, y_base, color='#FDB927', alpha=0.9)  # 黄色
    ax.fill_between(x, y_base, y_total, color='#552583', alpha=0.8)  # 紫色
    ax.plot(x, y_total, color='#333333', linewidth=3)  # 黑色曲线

    # 绘制垂直辅助线 (只画线，不写字)
    points_x = [1.0, 4.5, 7.5, 9.5]
    for px in points_x:
        py = P_base + beta * (px ** gamma)
        ax.vlines(x=px, ymin=0, ymax=py, colors='white', linestyles=':', linewidth=2)
        # 画圆点
        ax.plot(px, py, marker='o', markersize=12, markerfacecolor='white',
                markeredgecolor='#552583', markeredgewidth=3, zorder=10)

    # 坐标轴设置
    ax.set_ylim(0, 1600)
    ax.set_xlim(0, 10.5)
    ax.set_xlabel("Game Attention Score (0-10)", fontsize=12, fontweight='bold')
    ax.set_ylabel("Ticket Price ($)", fontsize=12, fontweight='bold')

    # 去除边框
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    # 将图片转换为 Base64 字符串
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img_str


# --- 2. 生成 HTML 文件 (修复了花括号冲突) ---
def generate_html(base64_img):
    # 注意：这里的 CSS 和 JS 部分，花括号都被双写了 {{ }}
    # 或者我们不使用 f-string 来包裹整个大段，而是只用 f-string 插入图片变量

    html_part1 = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Drag and Drop Chart Editor</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"></script>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f0f0f0; padding: 20px; }
        #canvas-container {
            position: relative;
            width: 1400px;
            height: 800px;
            background-image: url('data:image/png;base64,"""

    html_part2 = """');
            background-size: contain;
            background-repeat: no-repeat;
            border: 2px solid #ccc;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            background-color: white;
            margin: 0 auto;
        }
        .draggable {
            position: absolute;
            cursor: move;
            background: rgba(255, 255, 255, 0.85);
            padding: 5px 10px;
            border-radius: 8px;
            border: 1px solid #ddd;
            text-align: center;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
            z-index: 100;
        }
        .draggable:hover { border-color: #552583; background: white; }

        .title-box { font-size: 24px; font-weight: bold; color: #333; background: transparent; border: none; box-shadow: none; }
        .formula-box { font-size: 18px; color: #555; background: transparent; border: none; box-shadow: none; font-style: italic; }
        .label-text { font-size: 14px; font-weight: bold; color: #333; }
        .fomo-box { color: #552583; font-style: italic; font-size: 16px; border: 2px solid #552583; }

        .legend-box { text-align: left; font-size: 14px; }
        .dot { height: 12px; width: 12px; display: inline-block; margin-right: 5px; }
    </style>
</head>
<body>
    <h2 style="text-align:center">拖动下面的文字到合适的位置，然后截图</h2>

    <div id="canvas-container">

        <div class="draggable title-box" style="top: 20px; left: 400px;">
            Dynamic Ticket Pricing Model
        </div>

        <div class="draggable formula-box" style="top: 70px; left: 550px;">
            P_total = P_base + β * (Attention)^γ
        </div>

        <div class="draggable legend-box" style="top: 100px; left: 50px;">
            <div><span class="dot" style="background:#FDB927;"></span>Intrinsic Value (Base)</div>
            <div style="margin-top:5px;"><span class="dot" style="background:#552583;"></span>Hype Premium (Star Power)</div>
        </div>

        <div class="draggable label-text" style="top: 250px; left: 100px;">
            vs Pistons<br>
            (Tue Night)<br>
            $155
        </div>

        <div class="draggable label-text" style="top: 400px; left: 550px;">
            vs Clippers<br>
            (Regular)<br>
            $300
        </div>

        <div class="draggable label-text" style="top: 600px; left: 950px;">
            vs Warriors<br>
            (Curry Visits)<br>
            $612
        </div>

        <div class="draggable label-text" style="top: 680px; left: 1150px;">
            vs Celtics<br>
            (Rivalry/Xmas)<br>
            $928
        </div>

        <div class="draggable fomo-box" style="top: 500px; left: 800px;">
            Exponential growth driven by<br>
            FOMO (Fear Of Missing Out) ↘
        </div>

    </div>

    <script>
        $( function() {
            // 启用拖拽功能
            $( ".draggable" ).draggable({ containment: "#canvas-container" });
        } );
    </script>
</body>
</html>
    """

    # 拼接字符串，避免 f-string 冲突
    return html_part1 + base64_img + html_part2


# --- 3. 执行并保存 ---
if __name__ == "__main__":
    print("正在生成图表和 HTML...")
    img_base64 = create_base_chart()
    html_code = generate_html(img_base64)

    filename = "drag_and_drop_chart.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"成功！请在浏览器中打开文件: {filename}")
    print("步骤：1. 双击打开网页 2. 拖动文字排版 3. 截图")