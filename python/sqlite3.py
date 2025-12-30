import sqlite3

# 连接数据库（不存在则创建）
conn = sqlite3.connect("data.db")
cursor = conn.cursor()

# 创建表
cursor.execute("CREATE TABLE IF NOT EXISTS users (name TEXT, age INT)")

# 插入数据
cursor.execute("INSERT INTO users VALUES (?, ?)", ("张三", 20))
conn.commit()  # 提交事务

# 查询数据
cursor.execute("SELECT * FROM users")
# 打印查询结果
print(cursor.fetchall())  # 结果：[('张三', 20)]







# 关闭连接
conn.close()