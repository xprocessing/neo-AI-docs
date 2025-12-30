好的，我将为你把这些常用的设计模式用 Java 代码实现一遍。

Java 的语法和特性（如 `interface`、`abstract class`、`static` 关键字等）非常适合用来清晰地展示这些设计模式的结构。

以下是各种设计模式的 Java 实现：

---

### 一、单例模式（Singleton）

**核心思想**：保证一个类在整个应用中只有一个实例，并提供一个全局访问点。

**Java 实现（懒汉式，线程安全）**：

```java
public class Database {
    // 使用 volatile 保证 instance 在多线程间的可见性
    private static volatile Database instance;

    // 私有构造函数，防止外部实例化
    private Database() {
        // 模拟数据库连接初始化
        System.out.println("数据库连接成功。");
    }

    // 公共静态方法，提供全局访问点
    public static Database getInstance() {
        // 双重检查锁定（Double-Checked Locking），提高效率
        if (instance == null) {
            synchronized (Database.class) {
                if (instance == null) {
                    instance = new Database();
                }
            }
        }
        return instance;
    }

    // 示例方法
    public void query(String sql) {
        System.out.println("执行SQL查询: " + sql);
    }

    // 防止通过反射破坏单例（可选）
    private Database(Object lock) {}
}

// 使用示例
class SingletonDemo {
    public static void main(String[] args) {
        Database db1 = Database.getInstance();
        Database db2 = Database.getInstance();

        System.out.println(db1 == db2); // 输出: true，证明是同一个实例
        db1.query("SELECT * FROM users");
    }
}
```

---

### 二、工厂模式（Factory）

**核心思想**：定义一个创建对象的接口，但由子类决定实例化哪个类。工厂方法使一个类的实例化延迟到其子类。

**Java 实现**：

```java
// 产品接口
interface Product {
    String getName();
}

// 具体产品A
class ConcreteProductA implements Product {
    @Override
    public String getName() {
        return "产品A";
    }
}

// 具体产品B
class ConcreteProductB implements Product {
    @Override
    public String getName() {
        return "产品B";
    }
}

// 工厂接口
interface ProductFactory {
    Product createProduct();
}

// 具体工厂A，用于创建产品A
class ConcreteProductAFactory implements ProductFactory {
    @Override
    public Product createProduct() {
        return new ConcreteProductA();
    }
}

// 具体工厂B，用于创建产品B
class ConcreteProductBFactory implements ProductFactory {
    @Override
    public Product createProduct() {
        return new ConcreteProductB();
    }
}

// 使用示例
class FactoryDemo {
    public static void main(String[] args) {
        ProductFactory factoryA = new ConcreteProductAFactory();
        Product productA = factoryA.createProduct();
        System.out.println(productA.getName()); // 输出: 产品A

        ProductFactory factoryB = new ConcreteProductBFactory();
        Product productB = factoryB.createProduct();
        System.out.println(productB.getName()); // 输出: 产品B
    }
}
```
*注：上面是**工厂方法模式**。有时“工厂模式”也泛指**简单工厂模式**，即把所有创建逻辑放在一个 `static` 方法中。*

---

### 三、抽象工厂模式（Abstract Factory）

**核心思想**：提供一个创建一系列相关或相互依赖对象的接口，而无需指定它们具体的类。

**Java 实现**：

```java
// 抽象产品族 - 手机
interface Phone {
    void call();
}

// 抽象产品族 - 电脑
interface Computer {
    void code();
}

// 具体产品 - 华为手机
class HuaweiPhone implements Phone {
    @Override
    public void call() {
        System.out.println("用华为手机打电话。");
    }
}

// 具体产品 - 华为电脑
class HuaweiComputer implements Computer {
    @Override
    public void code() {
        System.out.println("用华为电脑写代码。");
    }
}

// 具体产品 - 苹果手机
class ApplePhone implements Phone {
    @Override
    public void call() {
        System.out.println("用苹果手机打电话。");
    }
}

// 具体产品 - 苹果电脑
class AppleComputer implements Computer {
    @Override
    public void code() {
        System.out.println("用苹果电脑写代码。");
    }
}

// 抽象工厂接口
interface AbstractFactory {
    Phone createPhone();
    Computer createComputer();
}

// 具体工厂 - 华为工厂
class HuaweiFactory implements AbstractFactory {
    @Override
    public Phone createPhone() {
        return new HuaweiPhone();
    }

    @Override
    public Computer createComputer() {
        return new HuaweiComputer();
    }
}

// 具体工厂 - 苹果工厂
class AppleFactory implements AbstractFactory {
    @Override
    public Phone createPhone() {
        return new ApplePhone();
    }

    @Override
    public Computer createComputer() {
        return new AppleComputer();
    }
}

// 使用示例
class AbstractFactoryDemo {
    public static void main(String[] args) {
        AbstractFactory huaweiFactory = new HuaweiFactory();
        Phone huaweiPhone = huaweiFactory.createPhone();
        Computer huaweiComputer = huaweiFactory.createComputer();
        huaweiPhone.call();
        huaweiComputer.code();

        AbstractFactory appleFactory = new AppleFactory();
        Phone applePhone = appleFactory.createPhone();
        Computer appleComputer = appleFactory.createComputer();
        applePhone.call();
        appleComputer.code();
    }
}
```

---

### 四、建造者模式（Builder）

**核心思想**：将一个复杂对象的构建与它的表示分离，使得同样的构建过程可以创建不同的表示。

**Java 实现**：

```java
// 产品类
class Car {
    private String engine;
    private String wheels;
    private String body;

    public void setEngine(String engine) { this.engine = engine; }
    public void setWheels(String wheels) { this.wheels = wheels; }
    public void setBody(String body) { this.body = body; }

    @Override
    public String toString() {
        return "Car [发动机=" + engine + ", 轮胎=" + wheels + ", 车身=" + body + "]";
    }
}

// 抽象建造者
interface CarBuilder {
    void buildEngine();
    void buildWheels();
    void buildBody();
    Car getCar();
}

// 具体建造者 - 普通汽车
class CommonCarBuilder implements CarBuilder {
    private Car car;

    public CommonCarBuilder() {
        car = new Car();
    }

    @Override
    public void buildEngine() {
        car.setEngine("普通发动机");
    }

    @Override
    public void buildWheels() {
        car.setWheels("普通轮胎");
    }

    @Override
    public void buildBody() {
        car.setBody("普通车身");
    }

    @Override
    public Car getCar() {
        return car;
    }
}

// 具体建造者 - 豪华汽车
class LuxuryCarBuilder implements CarBuilder {
    private Car car;

    public LuxuryCarBuilder() {
        car = new Car();
    }

    @Override
    public void buildEngine() {
        car.setEngine("豪华发动机");
    }

    @Override
    public void buildWheels() {
        car.setWheels("豪华轮胎");
    }

    @Override
    public void buildBody() {
        car.setBody("豪华车身");
    }

    @Override
    public Car getCar() {
        return car;
    }
}

// 指挥者
class Director {
    public Car constructCar(CarBuilder builder) {
        builder.buildEngine();
        builder.buildWheels();
        builder.buildBody();
        return builder.getCar();
    }
}

// 使用示例
class BuilderDemo {
    public static void main(String[] args) {
        Director director = new Director();

        CarBuilder commonBuilder = new CommonCarBuilder();
        Car commonCar = director.constructCar(commonBuilder);
        System.out.println(commonCar);

        CarBuilder luxuryBuilder = new LuxuryCarBuilder();
        Car luxuryCar = director.constructCar(luxuryBuilder);
        System.out.println(luxuryCar);
    }
}
```

---

### 五、原型模式（Prototype）

**核心思想**：用原型实例指定创建对象的种类，并且通过拷贝这个原型来创建新的对象。

**Java 实现**：

```java
// 原型接口，实现 Cloneable 接口
interface Prototype extends Cloneable {
    Prototype clone();
}

// 具体原型
class User implements Prototype {
    private String name;
    private int age;
    private Address address; // 引用类型成员

    public User(String name, int age, Address address) {
        this.name = name;
        this.age = age;
        this.address = address;
        System.out.println("创建用户对象（成本较高）。");
    }

    // 实现克隆方法
    @Override
    public Prototype clone() {
        try {
            // Object.clone() 是浅拷贝
            User clonedUser = (User) super.clone();
            // 手动实现深拷贝
            clonedUser.address = new Address(this.address.getStreet());
            return clonedUser;
        } catch (CloneNotSupportedException e) {
            e.printStackTrace();
            return null;
        }
    }

    @Override
    public String toString() {
        return "User [name=" + name + ", age=" + age + ", address=" + address + "]";
    }

    // Getters and Setters
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    public Address getAddress() { return address; }
}

class Address {
    private String street;

    public Address(String street) {
        this.street = street;
    }

    @Override
    public String toString() {
        return "Address [street=" + street + "]";
    }

    // Getters and Setters
    public String getStreet() { return street; }
    public void setStreet(String street) { this.street = street; }
}


// 使用示例
class PrototypeDemo {
    public static void main(String[] args) {
        Address addr = new Address("Main Street");
        User user1 = new User("张三", 25, addr);
        System.out.println(user1);

        // 通过克隆创建新对象
        User user2 = (User) user1.clone();
        user2.setName("李四");
        user2.getAddress().setStreet("Second Avenue"); // 修改克隆对象的引用成员

        System.out.println(user1); // 原对象不受影响
        System.out.println(user2); // 新对象已修改
    }
}
```

---

### 六、适配器模式（Adapter）

**核心思想**：将一个类的接口转换成客户希望的另一个接口。适配器模式使得原本由于接口不兼容而不能一起工作的那些类可以一起工作。

**Java 实现**：

```java
// 目标接口（客户端期望的接口）
interface Target {
    String request();
}

// 适配者（需要被适配的现有接口）
class Adaptee {
    public String specificRequest() {
        return "旧系统的特殊请求";
    }
}

// 适配器（类适配器，使用继承）
class ClassAdapter extends Adaptee implements Target {
    @Override
    public String request() {
        String result = specificRequest();
        return "适配器转换: " + result + " -> 新系统的标准响应";
    }
}

// 适配器（对象适配器，使用组合，更灵活）
class ObjectAdapter implements Target {
    private Adaptee adaptee;

    public ObjectAdapter(Adaptee adaptee) {
        this.adaptee = adaptee;
    }

    @Override
    public String request() {
        String result = adaptee.specificRequest();
        return "适配器转换: " + result + " -> 新系统的标准响应";
    }
}

// 使用示例
class AdapterDemo {
    public static void main(String[] args) {
        // 使用类适配器
        Target classAdapter = new ClassAdapter();
        System.out.println(classAdapter.request());

        // 使用对象适配器
        Target objectAdapter = new ObjectAdapter(new Adaptee());
        System.out.println(objectAdapter.request());
    }
}
```

---

### 七、装饰器模式（Decorator）

**核心思想**：动态地给一个对象添加一些额外的职责。就增加功能来说，装饰器模式相比生成子类更为灵活。

**Java 实现**：

```java
// 抽象组件
interface Component {
    String operation();
}

// 具体组件
class ConcreteComponent implements Component {
    @Override
    public String operation() {
        return "核心功能";
    }
}

// 抽象装饰器
abstract class Decorator implements Component {
    protected Component component;

    public Decorator(Component component) {
        this.component = component;
    }

    @Override
    public abstract String operation();
}

// 具体装饰器A
class LogDecorator extends Decorator {
    public LogDecorator(Component component) {
        super(component);
    }

    @Override
    public String operation() {
        return "日志记录 -> " + component.operation();
    }
}

// 具体装饰器B
class CacheDecorator extends Decorator {
    public CacheDecorator(Component component) {
        super(component);
    }

    @Override
    public String operation() {
        return "缓存处理 -> " + component.operation();
    }
}

// 使用示例
class DecoratorDemo {
    public static void main(String[] args) {
        Component component = new ConcreteComponent();
        System.out.println(component.operation());

        Component loggedComponent = new LogDecorator(component);
        System.out.println(loggedComponent.operation());

        Component cachedAndLoggedComponent = new CacheDecorator(loggedComponent);
        System.out.println(cachedAndLoggedComponent.operation());
    }
}
```

---

### 八、观察者模式（Observer）

**核心思想**：定义对象间的一种一对多的依赖关系，当一个对象的状态发生改变时，所有依赖于它的对象都得到通知并被自动更新。

**Java 实现**：

```java
import java.util.ArrayList;
import java.util.List;

// 主题（被观察者）接口
interface Subject {
    void attach(Observer observer);
    void detach(Observer observer);
    void notifyObservers();
}

// 观察者接口
interface Observer {
    void update(Subject subject);
}

// 具体主题
class Order implements Subject {
    private String status;
    private List<Observer> observers = new ArrayList<>();

    public void setStatus(String status) {
        this.status = status;
        notifyObservers(); // 状态改变时通知所有观察者
    }

    public String getStatus() {
        return status;
    }

    @Override
    public void attach(Observer observer) {
        observers.add(observer);
    }

    @Override
    public void detach(Observer observer) {
        observers.remove(observer);
    }

    @Override
    public void notifyObservers() {
        for (Observer observer : observers) {
            observer.update(this);
        }
    }
}

// 具体观察者A
class UserNotifier implements Observer {
    @Override
    public void update(Subject subject) {
        if (subject instanceof Order) {
            System.out.println("用户收到通知: 订单状态已更新为 \"" + ((Order) subject).getStatus() + "\"");
        }
    }
}

// 具体观察者B
class InventoryUpdater implements Observer {
    @Override
    public void update(Subject subject) {
        if (subject instanceof Order) {
            System.out.println("库存系统更新: 处理订单状态 \"" + ((Order) subject).getStatus() + "\" 的库存变化");
        }
    }
}

// 使用示例
class ObserverDemo {
    public static void main(String[] args) {
        Order order = new Order();
        Observer userNotifier = new UserNotifier();
        Observer inventoryUpdater = new InventoryUpdater();

        order.attach(userNotifier);
        order.attach(inventoryUpdater);

        order.setStatus("已支付");
        // 输出:
        // 用户收到通知: 订单状态已更新为 "已支付"
        // 库存系统更新: 处理订单状态 "已支付" 的库存变化

        System.out.println("---");
        order.setStatus("已发货");
        // 输出:
        // 用户收到通知: 订单状态已更新为 "已发货"
        // 库存系统更新: 处理订单状态 "已发货" 的库存变化
    }
}
```

---

### 九、策略模式（Strategy）

**核心思想**：定义一系列的算法，并将每一个算法封装起来，使它们可以相互替换。策略模式让算法独立于使用它的客户而变化。

**Java 实现**：

```java
// 策略接口
interface Strategy {
    double calculatePrice(double originalPrice);
}

// 具体策略A：满减
class FullReduceStrategy implements Strategy {
    @Override
    public double calculatePrice(double originalPrice) {
        if (originalPrice >= 100) {
            return originalPrice - 20;
        }
        return originalPrice;
    }
}

// 具体策略B：折扣
class DiscountStrategy implements Strategy {
    @Override
    public double calculatePrice(double originalPrice) {
        return originalPrice * 0.9; // 9折
    }
}

// 具体策略C：无优惠
class NoDiscountStrategy implements Strategy {
    @Override
    public double calculatePrice(double originalPrice) {
        return originalPrice;
    }
}

// 上下文类
class PriceCalculator {
    private Strategy strategy;

    // 构造函数注入策略
    public PriceCalculator(Strategy strategy) {
        this.strategy = strategy;
    }

    // 提供方法切换策略
    public void setStrategy(Strategy strategy) {
        this.strategy = strategy;
    }

    public double getFinalPrice(double originalPrice) {
        return strategy.calculatePrice(originalPrice);
    }
}

// 使用示例
class StrategyDemo {
    public static void main(String[] args) {
        PriceCalculator calculator = new PriceCalculator(new NoDiscountStrategy());

        System.out.println("原价 80元，无优惠: " + calculator.getFinalPrice(80));

        calculator.setStrategy(new FullReduceStrategy());
        System.out.println("原价 100元，满减: " + calculator.getFinalPrice(100));

        calculator.setStrategy(new DiscountStrategy());
        System.out.println("原价 100元，折扣: " + calculator.getFinalPrice(100));
    }
}
```

---

### 十、代理模式（Proxy）

**核心思想**：为其他对象提供一种代理以控制对这个对象的访问。

**Java 实现**：

```java
// 抽象主题
interface Image {
    void display();
}

// 真实主题
class RealImage implements Image {
    private String filename;

    public RealImage(String filename) {
        this.filename = filename;
        loadFromDisk(); // 模拟加载图片的耗时操作
    }

    private void loadFromDisk() {
        System.out.println("加载图片: " + filename + " (耗时操作)");
    }

    @Override
    public void display() {
        System.out.println("显示图片: " + filename);
    }
}

// 代理主题
class ProxyImage implements Image {
    private RealImage realImage;
    private String filename;

    public ProxyImage(String filename) {
        this.filename = filename;
    }

    @Override
    public void display() {
        // 懒加载：只有在需要显示时才创建真实对象
        if (realImage == null) {
            realImage = new RealImage(filename);
        }
        realImage.display();
    }
}

// 使用示例
class ProxyDemo {
    public static void main(String[] args) {
        Image image = new ProxyImage("test.jpg");

        System.out.println("准备显示图片...");
        // 第一次调用display()，会加载图片
        image.display();

        System.out.println("\n再次准备显示图片...");
        // 第二次调用display()，直接使用已加载的真实对象
        image.display();
    }
}
```

希望这些 Java 实现能帮助你更好地理解和应用这些设计模式！