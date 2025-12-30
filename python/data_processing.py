import pandas as pd

# 数据
data = [
    {"name": "张三", "age": 20},
    {"name": "李四", "age": 22}
]


# 转为DataFrame并保存
df = pd.DataFrame(data)
df.to_csv("data.csv", index=False)  # 保存为CSV
df.to_excel("data.xlsx", index=False)  # 需额外安装openpyxl：pip install openpyxl 
