以下是Python中常用设计模式的代码实现，包含每种模式的核心思想、适用场景和完整示例：

### 一、单例模式（Singleton）
**核心思想**：保证一个类只有一个实例，并提供全局访问点。

**适用场景**：数据库连接、缓存服务、日志系统等需要共享资源的场景。

```python
class Database:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not Database._initialized:
            print("数据库连接成功")
            Database._initialized = True

    def query(self, sql):
        print(f"执行SQL：{sql}")

# 使用示例
db1 = Database()
db2 = Database()
print(db1 is db2)  # True
db1.query("SELECT * FROM users")
```


### 二、工厂模式（Factory）
**核心思想**：定义一个创建对象的接口，让子类决定实例化哪个类，将对象创建与使用分离。

**适用场景**：对象创建逻辑复杂、需要根据条件动态创建不同对象的场景。

```python
from abc import ABC, abstractmethod

# 产品接口
class Product(ABC):
    @abstractmethod
    def get_name(self):
        pass

# 具体产品A
class ConcreteProductA(Product):
    def get_name(self):
        return "产品A"

# 具体产品B
class ConcreteProductB(Product):
    def get_name(self):
        return "产品B"

# 工厂类
class ProductFactory:
    @staticmethod
    def create_product(product_type):
        if product_type == "A":
            return ConcreteProductA()
        elif product_type == "B":
            return ConcreteProductB()
        else:
            raise ValueError(f"未知产品类型：{product_type}")

# 使用示例
product_a = ProductFactory.create_product("A")
product_b = ProductFactory.create_product("B")
print(product_a.get_name())  # 产品A
print(product_b.get_name())  # 产品B
```


### 三、抽象工厂模式（Abstract Factory）
**核心思想**：提供一个创建一系列相关或相互依赖对象的接口，无需指定具体类。

**适用场景**：需要创建多个系列的产品（如不同品牌的手机、电脑），且产品之间存在依赖关系。

```python
from abc import ABC, abstractmethod

# 抽象产品A：手机接口
class Phone(ABC):
    @abstractmethod
    def call(self):
        pass

# 抽象产品B：电脑接口
class Computer(ABC):
    @abstractmethod
    def code(self):
        pass

# 具体产品A1：华为手机
class HuaweiPhone(Phone):
    def call(self):
        return "用华为手机打电话"

# 具体产品B1：华为电脑
class HuaweiComputer(Computer):
    def code(self):
        return "用华为电脑写代码"

# 具体产品A2：苹果手机
class ApplePhone(Phone):
    def call(self):
        return "用苹果手机打电话"

# 具体产品B2：苹果电脑
class AppleComputer(Computer):
    def code(self):
        return "用苹果电脑写代码"

# 抽象工厂接口
class AbstractFactory(ABC):
    @abstractmethod
    def create_phone(self):
        pass

    @abstractmethod
    def create_computer(self):
        pass

# 具体工厂1：华为工厂
class HuaweiFactory(AbstractFactory):
    def create_phone(self):
        return HuaweiPhone()

    def create_computer(self):
        return HuaweiComputer()

# 具体工厂2：苹果工厂
class AppleFactory(AbstractFactory):
    def create_phone(self):
        return ApplePhone()

    def create_computer(self):
        return AppleComputer()

# 使用示例
huawei_factory = HuaweiFactory()
huawei_phone = huawei_factory.create_phone()
huawei_computer = huawei_factory.create_computer()
print(huawei_phone.call())  # 用华为手机打电话
print(huawei_computer.code())  # 用华为电脑写代码

apple_factory = AppleFactory()
apple_phone = apple_factory.create_phone()
apple_computer = apple_factory.create_computer()
print(apple_phone.call())  # 用苹果手机打电话
print(apple_computer.code())  # 用苹果电脑写代码
```


### 四、建造者模式（Builder）
**核心思想**：将复杂对象的构建过程与表示分离，使得同样的构建过程可以创建不同的表示。

**适用场景**：创建复杂对象（如汽车、文档），且对象的组成部分需要逐步构建。

```python
from abc import ABC, abstractmethod

# 产品类：汽车
class Car:
    def __init__(self):
        self.parts = []

    def add_part(self, part):
        self.parts.append(part)

    def show_parts(self):
        print(f"汽车部件：{', '.join(self.parts)}")

# 抽象建造者接口
class CarBuilder(ABC):
    @abstractmethod
    def build_engine(self):
        pass

    @abstractmethod
    def build_wheel(self):
        pass

    @abstractmethod
    def build_body(self):
        pass

    @abstractmethod
    def get_car(self):
        pass

# 具体建造者：普通汽车
class CommonCarBuilder(CarBuilder):
    def __init__(self):
        self.car = Car()

    def build_engine(self):
        self.car.add_part("普通发动机")

    def build_wheel(self):
        self.car.add_part("普通轮胎")

    def build_body(self):
        self.car.add_part("普通车身")

    def get_car(self):
        return self.car

# 具体建造者：豪华汽车
class LuxuryCarBuilder(CarBuilder):
    def __init__(self):
        self.car = Car()

    def build_engine(self):
        self.car.add_part("豪华发动机")

    def build_wheel(self):
        self.car.add_part("豪华轮胎")

    def build_body(self):
        self.car.add_part("豪华车身")

    def get_car(self):
        return self.car

# 指挥者：负责控制建造流程
class Director:
    def build_car(self, builder):
        builder.build_engine()
        builder.build_wheel()
        builder.build_body()
        return builder.get_car()

# 使用示例
director = Director()

# 建造普通汽车
common_builder = CommonCarBuilder()
common_car = director.build_car(common_builder)
common_car.show_parts()  # 汽车部件：普通发动机, 普通轮胎, 普通车身

# 建造豪华汽车
luxury_builder = LuxuryCarBuilder()
luxury_car = director.build_car(luxury_builder)
luxury_car.show_parts()  # 汽车部件：豪华发动机, 豪华轮胎, 豪华车身
```


### 五、原型模式（Prototype）
**核心思想**：用原型实例指定创建对象的种类，通过复制这个原型来创建新对象。

**适用场景**：对象创建成本高（如数据库查询、复杂计算），且需要多次创建相似对象的场景。

```python
import copy

class Prototype:
    def clone(self):
        # 使用深拷贝创建新对象
        return copy.deepcopy(self)

class User(Prototype):
    def __init__(self, name, age, hobbies):
        self.name = name
        self.age = age
        self.hobbies = hobbies
        print("创建用户对象（成本较高）")

    def show_info(self):
        print(f"姓名：{self.name}，年龄：{self.age}，爱好：{', '.join(self.hobbies)}")

# 使用示例
# 创建原型对象
prototype_user = User("张三", 25, ["篮球", "游戏"])
prototype_user.show_info()  # 姓名：张三，年龄：25，爱好：篮球, 游戏

# 克隆原型对象
user1 = prototype_user.clone()
user1.name = "李四"
user1.show_info()  # 姓名：李四，年龄：25，爱好：篮球, 游戏

user2 = prototype_user.clone()
user2.name = "王五"
user2.hobbies.append("读书")
user2.show_info()  # 姓名：王五，年龄：25，爱好：篮球, 游戏, 读书
```


### 六、适配器模式（Adapter）
**核心思想**：将一个类的接口转换成客户端期望的另一个接口，解决接口不兼容问题。

**适用场景**：集成第三方库、旧系统改造、接口升级等需要兼容不同接口的场景。

```python
from abc import ABC, abstractmethod

# 目标接口（客户端期望的接口）
class Target(ABC):
    @abstractmethod
    def request(self):
        pass

# 适配者（需要被适配的旧接口）
class Adaptee:
    def specific_request(self):
        return "旧系统的特殊请求"

# 适配器（连接目标接口和适配者）
class Adapter(Target):
    def __init__(self, adaptee):
        self.adaptee = adaptee

    def request(self):
        result = self.adaptee.specific_request()
        return f"适配器转换：{result} → 新系统的标准响应"

# 使用示例
adaptee = Adaptee()
adapter = Adapter(adaptee)
print(adapter.request())  # 适配器转换：旧系统的特殊请求 → 新系统的标准响应
```


### 七、装饰器模式（Decorator）
**核心思想**：动态地给对象添加额外职责，不改变原类结构。

**适用场景**：需要给对象动态添加功能、功能可组合的场景（如日志、缓存、权限控制）。

```python
from abc import ABC, abstractmethod

# 抽象组件
class Component(ABC):
    @abstractmethod
    def operation(self):
        pass

# 具体组件
class ConcreteComponent(Component):
    def operation(self):
        return "核心功能"

# 抽象装饰器
class Decorator(Component):
    def __init__(self, component):
        self.component = component

    @abstractmethod
    def operation(self):
        pass

# 具体装饰器A：日志功能
class LogDecorator(Decorator):
    def operation(self):
        return f"日志记录 → {self.component.operation()}"

# 具体装饰器B：缓存功能
class CacheDecorator(Decorator):
    def operation(self):
        return f"缓存处理 → {self.component.operation()}"

# 使用示例
# 基础功能
component = ConcreteComponent()
print(component.operation())  # 核心功能

# 添加日志功能
log_decorator = LogDecorator(component)
print(log_decorator.operation())  # 日志记录 → 核心功能

# 同时添加日志和缓存功能
cache_decorator = CacheDecorator(log_decorator)
print(cache_decorator.operation())  # 缓存处理 → 日志记录 → 核心功能
```


### 八、观察者模式（Observer）
**核心思想**：定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会收到通知并自动更新。

**适用场景**：事件监听、消息通知、状态同步等场景（如订单状态变更通知、公众号推送）。

```python
from abc import ABC, abstractmethod

# 抽象主题（被观察者）
class Subject(ABC):
    def __init__(self):
        self.observers = []

    def attach(self, observer):
        self.observers.append(observer)

    def detach(self, observer):
        self.observers.remove(observer)

    def notify(self):
        for observer in self.observers:
            observer.update(self)

# 抽象观察者
class Observer(ABC):
    @abstractmethod
    def update(self, subject):
        pass

# 具体主题：订单
class Order(Subject):
    def __init__(self):
        super().__init__()
        self.status = None

    def set_status(self, status):
        self.status = status
        self.notify()  # 状态改变时通知观察者

    def get_status(self):
        return self.status

# 具体观察者A：用户通知
class UserNotifier(Observer):
    def update(self, subject):
        print(f"用户收到通知：订单状态已变更为「{subject.get_status()}」")

# 具体观察者B：库存更新
class InventoryUpdater(Observer):
    def update(self, subject):
        print(f"库存系统更新：订单状态为「{subject.get_status()}」，开始处理库存")

# 使用示例
order = Order()
user_notifier = UserNotifier()
inventory_updater = InventoryUpdater()

# 添加观察者
order.attach(user_notifier)
order.attach(inventory_updater)

# 改变订单状态（触发通知）
order.set_status("已支付")
# 输出：
# 用户收到通知：订单状态已变更为「已支付」
# 库存系统更新：订单状态为「已支付」，开始处理库存

order.set_status("已发货")
# 输出：
# 用户收到通知：订单状态已变更为「已发货」
# 库存系统更新：订单状态为「已发货」，开始处理库存
```


### 九、策略模式（Strategy）
**核心思想**：定义一系列算法，将每个算法封装起来，并让它们可以相互替换。

**适用场景**：需要根据不同条件选择不同算法（如支付方式、排序算法、折扣计算）。

```python
from abc import ABC, abstractmethod

# 策略接口
class Strategy(ABC):
    @abstractmethod
    def calculate(self, price):
        pass

# 具体策略A：满减策略
class FullReduceStrategy(Strategy):
    def calculate(self, price):
        return price - 20 if price >= 100 else price

# 具体策略B：折扣策略
class DiscountStrategy(Strategy):
    def calculate(self, price):
        return price * 0.9  # 9折

# 具体策略C：无优惠策略
class NoDiscountStrategy(Strategy):
    def calculate(self, price):
        return price

# 上下文类（使用策略的场景）
class PriceCalculator:
    def __init__(self, strategy):
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def calculate_final_price(self, price):
        return self.strategy.calculate(price)

# 使用示例
calculator = PriceCalculator(NoDiscountStrategy())

# 无优惠
print(calculator.calculate_final_price(80))  # 80

# 切换到满减策略
calculator.set_strategy(FullReduceStrategy())
print(calculator.calculate_final_price(100))  # 80

# 切换到折扣策略
calculator.set_strategy(DiscountStrategy())
print(calculator.calculate_final_price(100))  # 90
```


### 十、代理模式（Proxy）
**核心思想**：为其他对象提供一种代理以控制对这个对象的访问。

**适用场景**：延迟加载、权限控制、日志记录、缓存等需要控制对象访问的场景。

```python
from abc import ABC, abstractmethod

# 抽象主题
class Image(ABC):
    @abstractmethod
    def display(self):
        pass

# 真实主题（实际执行功能的对象）
class RealImage(Image):
    def __init__(self, filename):
        self.filename = filename
        self.load_from_disk()  # 模拟从磁盘加载图片（成本高）

    def load_from_disk(self):
        print(f"加载图片：{self.filename}（耗时操作）")

    def display(self):
        print(f"显示图片：{self.filename}")

# 代理主题（控制对真实主题的访问）
class ProxyImage(Image):
    def __init__(self, filename):
        self.filename = filename
        self.real_image = None

    def display(self):
        # 延迟加载：只有当需要显示时才创建真实对象
        if self.real_image is None:
            self.real_image = RealImage(self.filename)
        self.real_image.display()

# 使用示例
# 使用代理加载图片（延迟加载）
proxy_image = ProxyImage("test.jpg")
print("准备显示图片...")
proxy_image.display()  # 此时才加载图片并显示
# 输出：
# 准备显示图片...
# 加载图片：test.jpg（耗时操作）
# 显示图片：test.jpg

# 再次显示（直接使用已创建的真实对象）
proxy_image.display()
# 输出：
# 显示图片：test.jpg
```

### 总结与选择建议

| 模式         | 核心意图                     | 适用场景                                     | 优点                               | 注意事项                           |
| :----------- | :--------------------------- | :------------------------------------------- | :--------------------------------- | :--------------------------------- |
| **单例模式** | 确保类只有一个实例           | 全局共享资源，如数据库连接、配置对象         | 控制资源占用，全局访问             | 破坏单一职责，可能引入全局状态     |
| **工厂模式** | 封装对象创建逻辑             | 根据条件创建不同类型的对象                   | 解耦创建与使用，便于扩展           | 增加了类的数量                     |
| **抽象工厂** | 封装一系列相关对象的创建     | 需要创建多个相互依赖的产品族                 | 保证产品族的一致性                 | 扩展新产品困难，需要修改工厂接口   |
| **建造者模式** | 分步构建复杂对象             | 对象组成复杂，构建步骤固定但配置可变         | 控制对象构建过程，灵活性高         | 结构复杂，增加了代码量             |
| **原型模式** | 通过复制原型创建新对象       | 对象创建成本高，需频繁创建相似对象           | 提高创建效率，简化创建过程         | 深拷贝实现复杂，需注意循环引用     |
| **适配器模式** | 转换接口，解决不兼容问题     | 集成第三方库、旧系统改造                     | 复用现有代码，提高兼容性           | 增加了一层抽象，可能影响性能       |
| **装饰器模式** | 动态添加对象职责             | 需灵活扩展功能，且不希望修改原类             | 遵循开闭原则，扩展灵活             | 多层装饰可能导致代码复杂度增加     |
| **观察者模式** | 实现对象间的事件通知机制     | 事件监听、状态同步、消息通知                 | 解耦观察者与被观察者，支持广播通知 | 通知顺序不确定，可能导致循环依赖   |
| **策略模式** | 封装算法族，支持动态切换     | 多种算法可选，需根据条件动态选择             | 算法可替换，便于扩展和测试         | 增加了策略类的数量，客户端需了解策略 |
| **代理模式** | 控制对对象的访问             | 延迟加载、权限控制、日志记录                 | 保护目标对象，实现额外功能         | 增加了一层代理，可能影响性能       |

**选择建议**：

- **优先考虑设计原则**：是否符合开闭原则、单一职责原则。
- **根据业务场景选择**：
  - 创建对象时考虑工厂、抽象工厂、建造者、原型。
  - 扩展功能时考虑装饰器、适配器。
  - 处理依赖关系时考虑观察者、策略。
  - 控制访问时考虑代理、单例。
- **避免过度设计**：简单的场景无需使用复杂模式，如仅创建少量固定对象时，直接 `new` 可能更简单。