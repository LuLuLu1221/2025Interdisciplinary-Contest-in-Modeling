import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import base64
from io import BytesIO


# ==========================================
# 1. Generate Base Chart (Image Only)
# ==========================================
def create_seasonal_base_chart():
    # --- Data Generation ---
    start_date = datetime(2025, 10, 22)
    days = 175
    dates = [start_date + timedelta(days=i) for i in range(days)]

    # Base Price (Linear growth)
    base_prices = np.linspace(140, 160, days)

    # Weekend Bump
    np.random.seed(42)
    weekend_bump = np.zeros(days)
    for i, d in enumerate(dates):
        if d.weekday() in [4, 5]:  # Fri/Sat
            weekend_bump[i] = 40
        elif d.weekday() == 6:  # Sun
            weekend_bump[i] = 25

    # Event Bumps (Gaussian)
    events = {
        0: 200,  # Opening Night
        36: 120,  # Thanksgiving
        64: 350,  # Christmas (Peak)
        71: 150,  # New Year
        86: 130,  # MLK
        165: 180  # Playoffs
    }

    event_premium = np.zeros(days)
    for day_idx, amount in events.items():
        sigma = 3
        x_range = np.arange(days)
        bump = amount * np.exp(-0.5 * ((x_range - day_idx) / sigma) ** 2)
        event_premium += bump

    # Dip for All-Star
    event_premium[123:128] -= 50

    total_prices = base_prices + weekend_bump + event_premium
    total_prices = np.maximum(total_prices, base_prices)

    # --- Plotting ---
    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # Areas
    ax.fill_between(dates, 0, base_prices, color='#FDB927', alpha=0.9)  # Gold
    ax.fill_between(dates, base_prices, total_prices, color='#552583', alpha=0.8)  # Purple
    ax.plot(dates, total_prices, color='#333333', linewidth=2.5)

    # Vertical Lines for Key Dates (Visual Guide)
    for day_idx in events.keys():
        ax.vlines(x=dates[day_idx], ymin=0, ymax=total_prices[day_idx],
                  colors='white', linestyles=':', linewidth=2)
        ax.plot(dates[day_idx], total_prices[day_idx], marker='o', markersize=10,
                markerfacecolor='white', markeredgecolor='#552583', markeredgewidth=3, zorder=10)

    # Formatting
    ax.set_ylim(0, 700)  # Plenty of headroom for labels
    ax.set_xlim(dates[0], dates[-1])
    ax.set_ylabel("Average Ticket Price ($)", fontsize=12, fontweight='bold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # Clean look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()

    # Convert to Base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.read()).decode('utf-8')
    plt.close()
    return img_str


# ==========================================
# 2. Generate HTML with Draggable Elements
# ==========================================
def generate_html(base64_img):
    html_part1 = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Seasonal Pricing Chart Editor</title>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://code.jquery.com/ui/1.13.2/jquery-ui.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #f0f0f0; padding: 20px; }
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
            background: rgba(255, 255, 255, 0.9);
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid #ddd;
            text-align: center;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
            z-index: 100;
            white-space: nowrap; /* Prevent accidental wrapping */
        }
        .draggable:hover { border-color: #552583; background: white; transform: scale(1.02); transition: 0.1s; }

        /* Styles for specific types of labels */
        .title-box { font-size: 26px; font-weight: bold; color: #333; background: transparent; border: none; box-shadow: none; }
        .subtitle-box { font-size: 16px; color: #666; background: transparent; border: none; box-shadow: none; }

        .label-text { font-size: 13px; font-weight: bold; color: #333; line-height: 1.4; }
        .emoji { font-size: 16px; display: block; margin-bottom: 2px; }

        .legend-box { text-align: left; font-size: 14px; }
        .dot { height: 12px; width: 12px; display: inline-block; margin-right: 8px; border-radius: 2px; }
    </style>
</head>
<body>
    <h3 style="text-align:center; color:#555;">Drag labels to align with the peaks and dots. Screenshot when ready.</h3>

    <div id="canvas-container">

        <div class="draggable title-box" style="top: 20px; left: 400px;">
            Seasonal Time Factors Impact on Pricing
        </div>
        <div class="draggable subtitle-box" style="top: 60px; left: 480px;">
            Strategy: Dynamic Pricing Multipliers for Holidays & Weekends
        </div>

        <div class="draggable legend-box" style="top: 100px; left: 1100px;">
            <div><span class="dot" style="background:#FDB927;"></span>Base Value (Weekday)</div>
            <div style="margin-top:5px;"><span class="dot" style="background:#552583;"></span>Time Premium (Holidays)</div>
        </div>

        <div class="draggable label-text" style="top: 350px; left: 30px;">
            <span class="emoji">🏀</span>
            Opening Night<br>$350
        </div>

        <div class="draggable label-text" style="top: 300px; left: 250px;">
            <span class="emoji">🦃</span>
            Thanksgiving<br>$300
        </div>

        <div class="draggable label-text" style="top: 520px; left: 480px;">
            <span class="emoji">🎄</span>
            Christmas Day<br>vs Celtics<br>$550
        </div>

        <div class="draggable label-text" style="top: 330px; left: 580px;">
            <span class="emoji">🎉</span>
            New Year's<br>$330
        </div>

        <div class="draggable label-text" style="top: 320px; left: 700px;">
            <span class="emoji">👑</span>
            MLK Day<br>$310
        </div>

        <div class="draggable label-text" style="top: 180px; left: 950px; font-style:italic; color:#777;">
            <span class="emoji">⭐</span>
            All-Star Break<br>(No Games)
        </div>

        <div class="draggable label-text" style="top: 380px; left: 1250px;">
            <span class="emoji">🔥</span>
            Playoff Push<br>$360
        </div>

    </div>

    <script>
        $( function() {
            $( ".draggable" ).draggable({ containment: "#canvas-container" });
        } );
    </script>
</body>
</html>
    """
    return html_part1 + base64_img + html_part2


# ==========================================
# 3. Execution
# ==========================================
if __name__ == "__main__":
    print("Generating Seasonal Pricing Chart HTML...")
    img_base64 = create_seasonal_base_chart()
    html_code = generate_html(img_base64)

    filename = "seasonal_chart_editor.html"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html_code)

    print(f"Done! Open '{filename}' in your browser.")