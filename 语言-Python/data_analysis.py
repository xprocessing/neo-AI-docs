import pandas as pd

# 数据示例
data = [
    {"name": "张三", "age": 20},
    {"name": "李四", "age": 22}
]

# 转换为 DataFrame
df = pd.DataFrame(data)

# 保存为 CSV（index=False 去除索引列）
df.to_csv("data.csv", index=False, encoding="utf-8-sig")