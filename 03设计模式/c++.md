我将为你用 C++ 实现这些常用的设计模式。

C++ 提供了强大的面向对象特性，如类、继承、虚函数等，非常适合实现这些设计模式。以下是各种模式的 C++ 代码实现：

---

### 一、单例模式（Singleton）

**核心思想**：保证一个类在整个应用中只有一个实例，并提供一个全局访问点。

**C++ 实现（懒汉式，线程安全）**：

```cpp
#include <iostream>
#include <mutex>

class Database {
private:
    // 私有静态实例指针
    static Database* instance;
    // 互斥锁，保证线程安全
    static std::mutex mtx;

    // 私有构造函数，防止外部实例化
    Database() {
        std::cout << "数据库连接成功。" << std::endl;
    }

    // 私有拷贝构造函数和赋值运算符，防止拷贝
    Database(const Database&) = delete;
    Database& operator=(const Database&) = delete;

public:
    // 公共静态方法，提供全局访问点
    static Database* getInstance() {
        // 双重检查锁定（Double-Checked Locking）
        if (instance == nullptr) {
            std::lock_guard<std::mutex> lock(mtx); // 自动加锁和解锁
            if (instance == nullptr) {
                instance = new Database();
            }
        }
        return instance;
    }

    // 示例方法
    void query(const std::string& sql) {
        std::cout << "执行SQL查询: " << sql << std::endl;
    }

    // 静态销毁方法（可选）
    static void destroyInstance() {
        std::lock_guard<std::mutex> lock(mtx);
        if (instance != nullptr) {
            delete instance;
            instance = nullptr;
            std::cout << "数据库连接已关闭。" << std::endl;
        }
    }
};

// 初始化静态成员
Database* Database::instance = nullptr;
std::mutex Database::mtx;

// 使用示例
int main() {
    Database* db1 = Database::getInstance();
    Database* db2 = Database::getInstance();

    std::cout << "db1 和 db2 是否为同一个实例: " << (db1 == db2 ? "是" : "否") << std::endl;

    db1->query("SELECT * FROM users");

    // 程序结束时销毁实例
    Database::destroyInstance();

    return 0;
}
```

---

### 二、工厂模式（Factory）

**核心思想**：定义一个创建对象的接口，但由子类决定实例化哪个类。工厂方法使一个类的实例化延迟到其子类。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 产品接口
class Product {
public:
    virtual ~Product() {}
    virtual std::string getName() const = 0;
};

// 具体产品A
class ConcreteProductA : public Product {
public:
    std::string getName() const override {
        return "产品A";
    }
};

// 具体产品B
class ConcreteProductB : public Product {
public:
    std::string getName() const override {
        return "产品B";
    }
};

// 工厂接口
class ProductFactory {
public:
    virtual ~ProductFactory() {}
    virtual Product* createProduct() const = 0;
};

// 具体工厂A，用于创建产品A
class ConcreteProductAFactory : public ProductFactory {
public:
    Product* createProduct() const override {
        return new ConcreteProductA();
    }
};

// 具体工厂B，用于创建产品B
class ConcreteProductBFactory : public ProductFactory {
public:
    Product* createProduct() const override {
        return new ConcreteProductB();
    }
};

// 使用示例
int main() {
    ProductFactory* factoryA = new ConcreteProductAFactory();
    Product* productA = factoryA->createProduct();
    std::cout << productA->getName() << std::endl;

    ProductFactory* factoryB = new ConcreteProductBFactory();
    Product* productB = factoryB->createProduct();
    std::cout << productB->getName() << std::endl;

    // 释放内存
    delete productA;
    delete factoryA;
    delete productB;
    delete factoryB;

    return 0;
}
```

---

### 三、抽象工厂模式（Abstract Factory）

**核心思想**：提供一个创建一系列相关或相互依赖对象的接口，而无需指定它们具体的类。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 抽象产品族 - 手机
class Phone {
public:
    virtual ~Phone() {}
    virtual void call() const = 0;
};

// 抽象产品族 - 电脑
class Computer {
public:
    virtual ~Computer() {}
    virtual void code() const = 0;
};

// 具体产品 - 华为手机
class HuaweiPhone : public Phone {
public:
    void call() const override {
        std::cout << "用华为手机打电话。" << std::endl;
    }
};

// 具体产品 - 华为电脑
class HuaweiComputer : public Computer {
public:
    void code() const override {
        std::cout << "用华为电脑写代码。" << std::endl;
    }
};

// 具体产品 - 苹果手机
class ApplePhone : public Phone {
public:
    void call() const override {
        std::cout << "用苹果手机打电话。" << std::endl;
    }
};

// 具体产品 - 苹果电脑
class AppleComputer : public Computer {
public:
    void code() const override {
        std::cout << "用苹果电脑写代码。" << std::endl;
    }
};

// 抽象工厂接口
class AbstractFactory {
public:
    virtual ~AbstractFactory() {}
    virtual Phone* createPhone() const = 0;
    virtual Computer* createComputer() const = 0;
};

// 具体工厂 - 华为工厂
class HuaweiFactory : public AbstractFactory {
public:
    Phone* createPhone() const override {
        return new HuaweiPhone();
    }

    Computer* createComputer() const override {
        return new HuaweiComputer();
    }
};

// 具体工厂 - 苹果工厂
class AppleFactory : public AbstractFactory {
public:
    Phone* createPhone() const override {
        return new ApplePhone();
    }

    Computer* createComputer() const override {
        return new AppleComputer();
    }
};

// 使用示例
int main() {
    AbstractFactory* huaweiFactory = new HuaweiFactory();
    Phone* huaweiPhone = huaweiFactory->createPhone();
    Computer* huaweiComputer = huaweiFactory->createComputer();
    huaweiPhone->call();
    huaweiComputer->code();

    AbstractFactory* appleFactory = new AppleFactory();
    Phone* applePhone = appleFactory->createPhone();
    Computer* appleComputer = appleFactory->createComputer();
    applePhone->call();
    appleComputer->code();

    // 释放内存
    delete huaweiPhone;
    delete huaweiComputer;
    delete huaweiFactory;
    delete applePhone;
    delete appleComputer;
    delete appleFactory;

    return 0;
}
```

---

### 四、建造者模式（Builder）

**核心思想**：将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 产品类
class Car {
private:
    std::string engine;
    std::string wheels;
    std::string body;

public:
    void setEngine(const std::string& e) { engine = e; }
    void setWheels(const std::string& w) { wheels = w; }
    void setBody(const std::string& b) { body = b; }

    void show() const {
        std::cout << "Car [发动机=" << engine << ", 轮胎=" << wheels << ", 车身=" << body << "]" << std::endl;
    }
};

// 抽象建造者
class CarBuilder {
protected:
    Car* car;

public:
    CarBuilder() { car = new Car(); }
    virtual ~CarBuilder() { delete car; }

    Car* getCar() { return car; }

    virtual void buildEngine() = 0;
    virtual void buildWheels() = 0;
    virtual void buildBody() = 0;
};

// 具体建造者 - 普通汽车
class CommonCarBuilder : public CarBuilder {
public:
    void buildEngine() override {
        car->setEngine("普通发动机");
    }

    void buildWheels() override {
        car->setWheels("普通轮胎");
    }

    void buildBody() override {
        car->setBody("普通车身");
    }
};

// 具体建造者 - 豪华汽车
class LuxuryCarBuilder : public CarBuilder {
public:
    void buildEngine() override {
        car->setEngine("豪华发动机");
    }

    void buildWheels() override {
        car->setWheels("豪华轮胎");
    }

    void buildBody() override {
        car->setBody("豪华车身");
    }
};

// 指挥者
class Director {
public:
    Car* constructCar(CarBuilder* builder) {
        builder->buildEngine();
        builder->buildWheels();
        builder->buildBody();
        return builder->getCar();
    }
};

// 使用示例
int main() {
    Director director;

    CarBuilder* commonBuilder = new CommonCarBuilder();
    Car* commonCar = director.constructCar(commonBuilder);
    commonCar->show();
    delete commonBuilder; // 同时会删除内部的 car

    CarBuilder* luxuryBuilder = new LuxuryCarBuilder();
    Car* luxuryCar = director.constructCar(luxuryBuilder);
    luxuryCar->show();
    delete luxuryBuilder; // 同时会删除内部的 car

    return 0;
}
```

---

### 五、原型模式（Prototype）

**核心思想**：用原型实例指定创建对象的种类，并且通过拷贝这个原型来创建新的对象。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 原型接口
class Prototype {
public:
    virtual ~Prototype() {}
    virtual Prototype* clone() const = 0;
    virtual void showInfo() const = 0;
};

// 具体原型
class User : public Prototype {
private:
    std::string name;
    int age;
    std::string* address; // 指针成员，用于演示深拷贝

public:
    User(const std::string& n, int a, const std::string& addr) 
        : name(n), age(a), address(new std::string(addr)) {
        std::cout << "创建用户对象（成本较高）。" << std::endl;
    }

    // 拷贝构造函数（深拷贝）
    User(const User& other) 
        : name(other.name), age(other.age), address(new std::string(*other.address)) {
        std::cout << "通过深拷贝创建用户对象。" << std::endl;
    }

    ~User() {
        delete address;
        std::cout << "用户对象被销毁。" << std::endl;
    }

    // 实现克隆方法
    Prototype* clone() const override {
        return new User(*this); // 调用拷贝构造函数
    }

    void showInfo() const override {
        std::cout << "User [name=" << name << ", age=" << age << ", address=" << *address << "]" << std::endl;
    }

    // 设置新地址，用于测试深拷贝
    void setAddress(const std::string& newAddr) {
        *address = newAddr;
    }
};

// 使用示例
int main() {
    User* user1 = new User("张三", 25, "Main Street");
    user1->showInfo();

    // 通过克隆创建新对象
    User* user2 = dynamic_cast<User*>(user1->clone());
    user2->showInfo();

    // 修改克隆对象的地址，验证深拷贝
    user2->setAddress("Second Avenue");
    std::cout << "\n修改克隆对象地址后：" << std::endl;
    user1->showInfo();
    user2->showInfo();

    // 释放内存
    delete user1;
    delete user2;

    return 0;
}
```

---

### 六、适配器模式（Adapter）

**核心思想**：将一个类的接口转换成客户希望的另一个接口。适配器模式使得原本由于接口不兼容而不能一起工作的那些类可以一起工作。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 目标接口（客户端期望的接口）
class Target {
public:
    virtual ~Target() {}
    virtual std::string request() const = 0;
};

// 适配者（需要被适配的现有接口）
class Adaptee {
public:
    std::string specificRequest() const {
        return "旧系统的特殊请求";
    }
};

// 适配器（对象适配器，使用组合）
class Adapter : public Target {
private:
    Adaptee* adaptee;

public:
    Adapter(Adaptee* a) : adaptee(a) {}
    ~Adapter() { delete adaptee; }

    std::string request() const override {
        std::string result = adaptee->specificRequest();
        return "适配器转换: " + result + " -> 新系统的标准响应";
    }
};

// 使用示例
int main() {
    Adaptee* adaptee = new Adaptee();
    Target* adapter = new Adapter(adaptee); // adaptee 的所有权转移给 adapter

    std::cout << adapter->request() << std::endl;

    delete adapter; // 会自动删除内部的 adaptee

    return 0;
}
```

---

### 七、装饰器模式（Decorator）

**核心思想**：动态地给一个对象添加一些额外的职责。就增加功能来说，装饰器模式相比生成子类更为灵活。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 抽象组件
class Component {
public:
    virtual ~Component() {}
    virtual std::string operation() const = 0;
};

// 具体组件
class ConcreteComponent : public Component {
public:
    std::string operation() const override {
        return "核心功能";
    }
};

// 抽象装饰器
class Decorator : public Component {
protected:
    Component* component;

public:
    Decorator(Component* c) : component(c) {}
    ~Decorator() { delete component; }

    virtual std::string operation() const override = 0;
};

// 具体装饰器A
class LogDecorator : public Decorator {
public:
    LogDecorator(Component* c) : Decorator(c) {}

    std::string operation() const override {
        return "日志记录 -> " + component->operation();
    }
};

// 具体装饰器B
class CacheDecorator : public Decorator {
public:
    CacheDecorator(Component* c) : Decorator(c) {}

    std::string operation() const override {
        return "缓存处理 -> " + component->operation();
    }
};

// 使用示例
int main() {
    Component* component = new ConcreteComponent();
    std::cout << component->operation() << std::endl;

    Component* loggedComponent = new LogDecorator(new ConcreteComponent());
    std::cout << loggedComponent->operation() << std::endl;

    Component* cachedAndLoggedComponent = new CacheDecorator(new LogDecorator(new ConcreteComponent()));
    std::cout << cachedAndLoggedComponent->operation() << std::endl;

    delete component;
    delete loggedComponent;
    delete cachedAndLoggedComponent;

    return 0;
}
```

---

### 八、观察者模式（Observer）

**核心思想**：定义对象间的一种一对多的依赖关系，当一个对象的状态发生改变时，所有依赖于它的对象都得到通知并被自动更新。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

// 前向声明
class Subject;

// 观察者接口
class Observer {
public:
    virtual ~Observer() {}
    virtual void update(Subject* subject) = 0;
};

// 主题（被观察者）接口
class Subject {
private:
    std::vector<Observer*> observers;

public:
    virtual ~Subject() {
        // 注意：这里不负责删除观察者对象，由使用者管理
        observers.clear();
    }

    void attach(Observer* observer) {
        observers.push_back(observer);
    }

    void detach(Observer* observer) {
        auto it = std::find(observers.begin(), observers.end(), observer);
        if (it != observers.end()) {
            observers.erase(it);
        }
    }

    void notifyObservers() {
        for (Observer* observer : observers) {
            observer->update(this);
        }
    }

    virtual std::string getStatus() const = 0;
    virtual void setStatus(const std::string& status) = 0;
};

// 具体主题
class Order : public Subject {
private:
    std::string status;

public:
    std::string getStatus() const override {
        return status;
    }

    void setStatus(const std::string& s) override {
        status = s;
        notifyObservers(); // 状态改变时通知所有观察者
    }
};

// 具体观察者A
class UserNotifier : public Observer {
public:
    void update(Subject* subject) override {
        Order* order = dynamic_cast<Order*>(subject);
        if (order) {
            std::cout << "用户收到通知: 订单状态已更新为 \"" << order->getStatus() << "\"" << std::endl;
        }
    }
};

// 具体观察者B
class InventoryUpdater : public Observer {
public:
    void update(Subject* subject) override {
        Order* order = dynamic_cast<Order*>(subject);
        if (order) {
            std::cout << "库存系统更新: 处理订单状态 \"" << order->getStatus() << "\" 的库存变化" << std::endl;
        }
    }
};

// 使用示例
int main() {
    Order* order = new Order();
    Observer* userNotifier = new UserNotifier();
    Observer* inventoryUpdater = new InventoryUpdater();

    order->attach(userNotifier);
    order->attach(inventoryUpdater);

    order->setStatus("已支付");
    std::cout << "---" << std::endl;
    order->setStatus("已发货");

    // 释放内存
    order->detach(userNotifier);
    order->detach(inventoryUpdater);
    delete userNotifier;
    delete inventoryUpdater;
    delete order;

    return 0;
}
```

---

### 九、策略模式（Strategy）

**核心思想**：定义一系列的算法，并将每一个算法封装起来，使它们可以相互替换。策略模式让算法独立于使用它的客户而变化。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 策略接口
class Strategy {
public:
    virtual ~Strategy() {}
    virtual double calculatePrice(double originalPrice) const = 0;
};

// 具体策略A：满减
class FullReduceStrategy : public Strategy {
public:
    double calculatePrice(double originalPrice) const override {
        if (originalPrice >= 100) {
            return originalPrice - 20;
        }
        return originalPrice;
    }
};

// 具体策略B：折扣
class DiscountStrategy : public Strategy {
public:
    double calculatePrice(double originalPrice) const override {
        return originalPrice * 0.9; // 9折
    }
};

// 具体策略C：无优惠
class NoDiscountStrategy : public Strategy {
public:
    double calculatePrice(double originalPrice) const override {
        return originalPrice;
    }
};

// 上下文类
class PriceCalculator {
private:
    Strategy* strategy;

public:
    PriceCalculator(Strategy* s) : strategy(s) {}
    ~PriceCalculator() { delete strategy; }

    // 提供方法切换策略
    void setStrategy(Strategy* s) {
        delete strategy;
        strategy = s;
    }

    double getFinalPrice(double originalPrice) const {
        return strategy->calculatePrice(originalPrice);
    }
};

// 使用示例
int main() {
    PriceCalculator calculator(new NoDiscountStrategy());

    std::cout << "原价 80元，无优惠: " << calculator.getFinalPrice(80) << std::endl;

    calculator.setStrategy(new FullReduceStrategy());
    std::cout << "原价 100元，满减: " << calculator.getFinalPrice(100) << std::endl;

    calculator.setStrategy(new DiscountStrategy());
    std::cout << "原价 100元，折扣: " << calculator.getFinalPrice(100) << std::endl;

    return 0;
}
```

---

### 十、代理模式（Proxy）

**核心思想**：为其他对象提供一种代理以控制对这个对象的访问。

**C++ 实现**：

```cpp
#include <iostream>
#include <string>

// 抽象主题
class Image {
public:
    virtual ~Image() {}
    virtual void display() const = 0;
};

// 真实主题
class RealImage : public Image {
private:
    std::string filename;

    // 模拟加载图片的耗时操作
    void loadFromDisk() const {
        std::cout << "加载图片: " << filename << " (耗时操作)" << std::endl;
    }

public:
    RealImage(const std::string& fname) : filename(fname) {
        loadFromDisk();
    }

    void display() const override {
        std::cout << "显示图片: " << filename << std::endl;
    }
};

// 代理主题
class ProxyImage : public Image {
private:
    RealImage* realImage;
    std::string filename;

public:
    ProxyImage(const std::string& fname) : realImage(nullptr), filename(fname) {}
    ~ProxyImage() {
        delete realImage;
    }

    void display() const override {
        // 懒加载：只有在需要显示时才创建真实对象
        if (realImage == nullptr) {
            realImage = new RealImage(filename);
        }
        realImage->display();
    }
};

// 使用示例
int main() {
    Image* image = new ProxyImage("test.jpg");

    std::cout << "准备显示图片..." << std::endl;
    // 第一次调用display()，会加载图片
    image->display();

    std::cout << "\n再次准备显示图片..." << std::endl;
    // 第二次调用display()，直接使用已加载的真实对象
    image->display();

    delete image;

    return 0;
}
```

希望这些 C++ 实现能帮助你更好地理解和应用这些设计模式！