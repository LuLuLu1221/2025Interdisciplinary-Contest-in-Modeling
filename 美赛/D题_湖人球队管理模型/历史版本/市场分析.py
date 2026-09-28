import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. 数据准备
data = {
    'City': ['New York', 'Los Angeles', 'San Francisco', 'Chicago', 'Dallas', 'Washington, D.C.',
             'Boston', 'Seattle', 'Houston', 'Atlanta', 'Toronto', 'Miami', 'Philadelphia',
             'Denver', 'Phoenix', 'Las Vegas', 'Minneapolis', 'Charlotte', 'San Antonio',
             'Portland', 'Detroit', 'Sacramento', 'Cleveland', 'Indianapolis', 'Salt Lake City',
             'Milwaukee', 'Oklahoma City', 'Memphis', 'New Orleans'],
    'Population': [20817000, 13778000, 3652000, 9830000, 7380000, 6122000, 4778000, 3909000,
                   7569000, 6889000, 6400000, 6952000, 6378000, 3278000, 5301000, 3312000,
                   3315000, 2631000, 2777000, 2476000, 3837000, 2487000, 1932000, 2109000,
                   1339000, 1603000, 1133000, 1295000, 1123000],
    'GDP_Per_Capita': [98000, 81000, 128000, 78000, 76000, 89000, 92000, 95000, 70000, 72000,
                       68500, 64000, 66000, 75000, 60000, 68000, 67000, 63000, 59000, 62000,
                       55000, 54000, 56000, 58000, 71000, 59000, 55000, 52000, 51000]
}

df = pd.DataFrame(data)

# 2. 高级数学模型：对数潜力模型 (Log-Potential Model)
# 使用对数处理人口和GDP，模拟边际效用递减
df['Log_Pop'] = np.log10(df['Population'])
df['Log_GDP'] = np.log10(df['GDP_Per_Capita'])

# 归一化处理
def normalize(col):
    return (col - col.min()) / (col.max() - col.min())

df['Score'] = (normalize(df['Log_Pop']) * 0.45 + normalize(df['Log_GDP']) * 0.55) * 100

# 市场分级逻辑
def categorize(score):
    if score > 85: return 'Tier 1: Global Elite'
    elif score > 65: return 'Tier 2: Major Market'
    elif score > 45: return 'Tier 3: Stable Mid'
    else: return 'Tier 4: Small Market'

df['Market_Tier'] = df['Score'].apply(categorize)

# 3. 打印高级商业排名
print("\n" + "="*60)
print("     2026 NBA ADVANCED MARKET VALUATION POTENTIAL (MVP)")
print("="*60)
print(df.sort_values('Score', ascending=False)[['City', 'Market_Tier', 'Score']].to_string(index=False))

# 4. 绘图：四分象限图 (Matrix Analysis)
plt.figure(figsize=(15, 11))
sns.set_style("whitegrid")

# 绘制散点，大小由对数分值决定
scatter = sns.scatterplot(
    data=df, x='Population', y='GDP_Per_Capita',
    size='Score', hue='Market_Tier',
    palette='magma', sizes=(100, 1500), alpha=0.7, edgecolor='w', linewidth=1.5
)

# 绘制均值辅助线，划分象限
plt.axvline(df['Population'].mean(), color='grey', linestyle='--', alpha=0.5)
plt.axhline(df['GDP_Per_Capita'].mean(), color='grey', linestyle='--', alpha=0.5)

# 标注所有城市，并处理纽约等极端点
for i in range(df.shape[0]):
    plt.text(
        df.iloc[i]['Population'] * 1.02,
        df.iloc[i]['GDP_Per_Capita'],
        df.iloc[i]['City'],
        fontsize=10, verticalalignment='center'
    )

plt.title('NBA Advanced Market Matrix: Value Density vs. Reach (2026)', fontsize=18, fontweight='bold')
plt.xlabel('Metro Population (Market Reach)', fontsize=13)
plt.ylabel('GDP Per Capita (Wealth Density)', fontsize=13)
plt.xscale('log') # 使用对数坐标轴，市场分布更均匀
plt.grid(True, which="both", ls="-", alpha=0.2)
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Market Classification")

plt.tight_layout()
plt.show()