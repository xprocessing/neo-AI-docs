# ==============================================
# Python 核心语法速查 (A4纸打印版)
# 涵盖变量、数据类型、控制流、函数、容器、异常等核心知识点
# ==============================================

# 1. 基础变量与数据类型
# 数值类型：整数、浮点数、布尔值
integer_num = 10                # 整数
float_num = 3.14159             # 浮点数
boolean_val = True              # 布尔值 (True/False)
string_val = "Hello Python"     # 字符串
empty_val = None                # 空值

# 字符串操作
str_concat = string_val + "!"   # 字符串拼接
str_format = f"数值：{integer_num}, 浮点：{float_num:.2f}"  # f-string格式化
str_slice = string_val[0:5]     # 字符串切片 (左闭右开)

# 2. 常用数据容器
# 列表 (有序、可变、可重复)
my_list = [1, 2, 3, "Python", True]
my_list.append(4)               # 添加元素
my_list[0] = 0                  # 修改元素

# 元组 (有序、不可变、可重复)
my_tuple = (10, 20, 30)
# my_tuple[0] = 0  # 报错：元组不可修改

# 字典 (键值对、无序、键唯一)
my_dict = {"name": "张三", "age": 20, "city": "北京"}
my_dict["age"] = 21             # 修改值
my_dict["gender"] = "男"        # 添加键值对

# 集合 (无序、无重复、可哈希)
my_set = {1, 2, 2, 3}          # 自动去重，结果为 {1,2,3}
my_set.add(4)                   # 添加元素

# 3. 控制流语句
# 条件判断
score = 85
if score >= 90:
    grade = "优秀"
elif score >= 80:
    grade = "良好"
else:
    grade = "及格"

# 循环语句
# for循环 (遍历)
sum_num = 0
for i in range(1, 11):          # range(1,11) 生成 1-10 的整数
    sum_num += i                # 累加求和

# while循环 (条件循环)
count = 0
while count < 5:
    count += 1
    if count == 3:
        continue                # 跳过本次循环
    if count == 5:
        break                   # 终止循环

# 4. 函数定义与使用
def calculate(a, b, op="+"):
    """
    简单计算器函数 (带默认参数)
    :param a: 第一个数
    :param b: 第二个数
    :param op: 操作符，默认加法
    :return: 计算结果
    """
    if op == "+":
        return a + b
    elif op == "-":
        return a - b
    else:
        return "不支持的操作"

# 调用函数
add_result = calculate(10, 5)    # 使用默认参数 (加法)
sub_result = calculate(10, 5, "-")  # 指定参数 (减法)

# 匿名函数 (lambda)
square = lambda x: x * x        # 计算平方
square_result = square(6)       # 结果：36

# 5. 异常处理
try:
    result = 10 / 0             # 会触发除零异常
except ZeroDivisionError as e:
    result = f"错误：{e}"       # 捕获指定异常
except Exception as e:
    result = f"其他错误：{e}"   # 捕获所有异常
finally:
    print("无论是否异常，都会执行")  # 最终执行块

# 6. 类与对象 (面向对象基础)
class Person:
    # 构造方法
    def __init__(self, name, age):
        self.name = name        # 实例属性
        self.age = age

    # 实例方法
    def introduce(self):
        return f"我叫{self.name}，今年{self.age}岁"

# 创建对象
person = Person("李四", 25)
intro = person.introduce()      # 调用实例方法

# 7. 文件操作 (简易版)
with open("test.txt", "w", encoding="utf-8") as f:  # with自动关闭文件
    f.write("Hello Python!")    # 写入文件

with open("test.txt", "r", encoding="utf-8") as f:
    content = f.read()          # 读取文件内容

# ==============================================
# 打印关键结果 (验证语法执行)
# ==============================================
print("1. 字符串格式化结果：", str_format)
print("2. 1-10累加和：", sum_num)
print("3. 函数加法结果：", add_result)
print("4. 平方计算结果：", square_result)
print("5. 异常处理结果：", result)
print("6. 类实例介绍：", intro)