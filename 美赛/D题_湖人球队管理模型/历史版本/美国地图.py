import folium
from folium.features import DivIcon
import pandas as pd

# ==========================================
# 1. 数据准备 (使用你提供的精确数值)
# ==========================================
# 我已将你的文本数据整理为结构化数据，并补充了所有城市的经纬度
data = [
    # --- Tier 2: Major Market (紫色 - 高度最高) ---
    {'City': 'New York', 'Score': 84.037840, 'Tier': 'Tier 2', 'Lat': 40.7128, 'Lon': -74.0060},
    {'City': 'San Francisco', 'Score': 73.175156, 'Tier': 'Tier 2', 'Lat': 37.7749, 'Lon': -122.4194},
    {'City': 'Los Angeles', 'Score': 66.290128, 'Tier': 'Tier 2', 'Lat': 34.0522, 'Lon': -118.2437},

    # --- Tier 3: Stable Mid (红色 - 中等高度) ---
    {'City': 'Washington, D.C.', 'Score': 59.417505, 'Tier': 'Tier 3', 'Lat': 38.9072, 'Lon': -77.0369},
    {'City': 'Chicago', 'Score': 58.830731, 'Tier': 'Tier 3', 'Lat': 41.8781, 'Lon': -87.6298},
    {'City': 'Boston', 'Score': 57.578819, 'Tier': 'Tier 3', 'Lat': 42.3601, 'Lon': -71.0589},
    {'City': 'Seattle', 'Score': 56.402865, 'Tier': 'Tier 3', 'Lat': 47.6062, 'Lon': -122.3321},
    {'City': 'Dallas', 'Score': 52.860053, 'Tier': 'Tier 3', 'Lat': 32.7767, 'Lon': -96.7970},
    {'City': 'Atlanta', 'Score': 48.567399, 'Tier': 'Tier 3', 'Lat': 33.7490, 'Lon': -84.3880},
    {'City': 'Houston', 'Score': 48.334472, 'Tier': 'Tier 3', 'Lat': 29.7604, 'Lon': -95.3698},

    # --- Tier 4: Small Market (橙色 - 较低高度) ---
    {'City': 'Toronto', 'Score': 44.454184, 'Tier': 'Tier 4', 'Lat': 43.6510, 'Lon': -79.3470},
    {'City': 'Philadelphia', 'Score': 42.178949, 'Tier': 'Tier 4', 'Lat': 39.9526, 'Lon': -75.1652},
    {'City': 'Miami', 'Score': 41.667891, 'Tier': 'Tier 4', 'Lat': 25.7617, 'Lon': -80.1918},
    {'City': 'Denver', 'Score': 39.560782, 'Tier': 'Tier 4', 'Lat': 39.7392, 'Lon': -104.9903},
    {'City': 'Las Vegas', 'Score': 33.863595, 'Tier': 'Tier 4', 'Lat': 36.1699, 'Lon': -115.1398},
    {'City': 'Phoenix', 'Score': 33.631700, 'Tier': 'Tier 4', 'Lat': 33.4484, 'Lon': -112.0740},
    {'City': 'Minneapolis', 'Score': 32.992061, 'Tier': 'Tier 4', 'Lat': 44.9778, 'Lon': -93.2650},
    {'City': 'Charlotte', 'Score': 25.751129, 'Tier': 'Tier 4', 'Lat': 35.2271, 'Lon': -80.8431},
    {'City': 'Portland', 'Score': 23.858977, 'Tier': 'Tier 4', 'Lat': 45.5152, 'Lon': -122.6784},
    {'City': 'Detroit', 'Score': 23.449797, 'Tier': 'Tier 4', 'Lat': 42.3314, 'Lon': -83.0458},
    {'City': 'San Antonio', 'Score': 22.662794, 'Tier': 'Tier 4', 'Lat': 29.4241, 'Lon': -98.4936},
    {'City': 'Salt Lake City', 'Score': 22.486235, 'Tier': 'Tier 4', 'Lat': 40.7608, 'Lon': -111.8910},
    {'City': 'Indianapolis', 'Score': 17.400294, 'Tier': 'Tier 4', 'Lat': 39.7684, 'Lon': -86.1581},
    {'City': 'Sacramento', 'Score': 15.670145, 'Tier': 'Tier 4', 'Lat': 38.5816, 'Lon': -121.4944},
    {'City': 'Milwaukee', 'Score': 14.193881, 'Tier': 'Tier 4', 'Lat': 43.0389, 'Lon': -87.9065},
    {'City': 'Cleveland', 'Score': 13.951905, 'Tier': 'Tier 4', 'Lat': 41.4993, 'Lon': -81.6944},
    {'City': 'Oklahoma City', 'Score': 4.649668, 'Tier': 'Tier 4', 'Lat': 35.4676, 'Lon': -97.5164},
    {'City': 'Memphis', 'Score': 3.356951, 'Tier': 'Tier 4', 'Lat': 35.1495, 'Lon': -90.0490},
    {'City': 'New Orleans', 'Score': 0.000000, 'Tier': 'Tier 4', 'Lat': 29.9511, 'Lon': -90.0715},
]

df = pd.DataFrame(data)


# ==========================================
# 2. 颜色与高度映射逻辑
# ==========================================
def get_style(tier, score):
    # 高度放大系数 (让柱子在地图上看起来更明显)
    # 基础高度20px + (分数 * 1.5)px
    height = 10 + (score * 2.0)

    if 'Tier 2' in tier:
        # 深紫色，代表顶级市场
        color = '#4A148C'
        shadow = '#7B1FA2'
    elif 'Tier 3' in tier:
        # 鲜红色，代表中坚力量
        color = '#D32F2F'
        shadow = '#EF5350'
    else:
        # 橙色，代表小市场
        color = '#F57C00'
        shadow = '#FF9800'

    return height, color, shadow


# ==========================================
# 3. 创建地图 (柱状图风格)
# ==========================================
# 使用浅色极简底图
m = folium.Map(location=[38.5, -96.0], zoom_start=4.5, tiles='CartoDB positron')

for i, row in df.iterrows():
    height, bg_color, shadow_color = get_style(row['Tier'], row['Score'])

    # 构造 HTML 柱状图
    # 这是一个垂直的长方形 div
    # 我们使用了 transform: translate 来修正位置，让柱子的底部对准城市坐标
    bar_html = f"""
    <div style="
        width: 100px; 
        height: {height + 30}px; 
        transform: translate(-50%, -100%); 
        pointer-events: none;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-end;
        ">

        <div style="
            font-family: Arial; 
            font-weight: bold; 
            font-size: 11px; 
            color: {bg_color};
            margin-bottom: 2px;
            text-shadow: 1px 1px 0 #fff;
            ">
            {row['Score']:.1f}
        </div>

        <div style="
            width: 14px;
            height: {height}px;
            background: linear-gradient(to bottom, {bg_color}, {shadow_color});
            border: 1px solid white;
            border-radius: 3px 3px 0 0;
            box-shadow: 2px 2px 4px rgba(0,0,0,0.4);
            ">
        </div>

        <div style="
            font-family: Arial;
            font-size: 9px;
            color: #666;
            margin-top: 2px;
            white-space: nowrap;
            text-shadow: 1px 1px 0 #fff;
            ">
            {row['City']}
        </div>
    </div>
    """

    folium.Marker(
        location=[row['Lat'], row['Lon']],
        icon=DivIcon(html=bar_html),
        tooltip=f"{row['City']}: {row['Score']:.2f} ({row['Tier']})"
    ).add_to(m)

# ==========================================
# 4. 添加图例
# ==========================================
legend_html = """
<div style="
    position: fixed; 
    bottom: 30px; left: 30px; 
    width: 200px; 
    background-color: rgba(255, 255, 255, 0.9); 
    z-index:9999; 
    font-size:12px;
    border: 1px solid #ccc;
    border-radius: 8px; 
    padding: 15px;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
    font-family: Arial, sans-serif;
    ">
    <h4 style="margin-top:0; margin-bottom:10px;">Market Value Score</h4>

    <div style="display:flex; align-items:center; margin-bottom:5px;">
        <div style="width:15px; height:40px; background:#4A148C; border:1px solid #fff; margin-right:10px;"></div>
        <div>
            <b>Tier 2: Major</b><br>
            <span style="color:#666;">Score > 60</span>
        </div>
    </div>

    <div style="display:flex; align-items:center; margin-bottom:5px;">
        <div style="width:15px; height:25px; background:#D32F2F; border:1px solid #fff; margin-right:10px;"></div>
        <div>
            <b>Tier 3: Mid</b><br>
            <span style="color:#666;">Score 45 - 60</span>
        </div>
    </div>

    <div style="display:flex; align-items:center;">
        <div style="width:15px; height:10px; background:#F57C00; border:1px solid #fff; margin-right:10px;"></div>
        <div>
            <b>Tier 4: Small</b><br>
            <span style="color:#666;">Score < 45</span>
        </div>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# ==========================================
# 5. 保存
# ==========================================
output_file = '../nba_market_bar_chart_map.html'
m.save(output_file)
print(f"地图已生成: {output_file}")
print("说明：")
print("- 柱子高度代表 Market Score (数值越大柱子越高)")
print("- 纽约、旧金山显示为最高的深紫色柱子")
print("- 新奥尔良显示为高度为0的基准点")