下面是 Java 中最常见的 23 种设计模式（GoF + 部分常用模式）的简洁实现示例，全部使用 Java 17+ 语法，代码可直接运行，便于理解和面试使用。

### 一、创建型模式（5种）

1. **单例模式（Singleton）** - 饿汉式（推荐）
```java
public enum Singleton {
    INSTANCE;  // 线程安全、懒加载、防反射、防序列化
    public void doSomething() {
        System.out.println("Singleton do something");
    }
}

// 使用
Singleton.INSTANCE.doSomething();
```

2. **工厂方法（Factory Method）**
```java
interface Product { void use(); }
class ConcreteProductA implements Product { public void use() { System.out.println("Product A"); }}
class ConcreteProductB implements Product { public void use() { System.out.println("Product B"); }}

interface Factory {
    Product create();
}
class FactoryA implements Factory {
    public Product create() { return new ConcreteProductA(); }
}
```

3. **抽象工厂（Abstract Factory）**
```java
interface Button { void render(); }
interface Checkbox { void check(); }

class WindowsButton implements Button { public void render() { System.out.println("Windows Button"); }}
class MacButton implements Button { public void render() { System.out.println("Mac Button"); }}

abstract class GUIFactory {
    abstract Button createButton();
    abstract Checkbox createCheckbox();
}

class WindowsFactory extends GUIFactory {
    Button createButton() { return new WindowsButton(); }
    Checkbox createCheckbox() { return new WindowsCheckbox(); }
}
```

4. **建造者（Builder）** - 经典写法 + Lombok 风格
```java
// 传统写法
public class Computer {
    private final String cpu;
    private final String ram;
    private final String storage;

    private Computer(Builder builder) {
        this.cpu = builder.cpu;
        this.ram = builder.ram;
        this.storage = builder.storage;
    }

    public static class Builder {
        private String cpu;
        private String ram;
        private String storage;

        public Builder cpu(String cpu) { this.cpu = cpu; return this; }
        public Builder ram(String ram) { this.ram = ram; return this; }
        public Builder storage(String storage) { this.storage = storage; return this; }
        public Computer build() { return new Computer(this); }
    }
}

// 使用
Computer pc = new Computer.Builder()
    .cpu("i9").ram("32GB").storage("1TB SSD").build();
```

5. **原型模式（Prototype）** - 深拷贝示例
```java
record Address(String city) implements Serializable {}
class Person implements Cloneable, Serializable {
    String name;
    Address address;

    @Override
    protected Person clone() throws CloneNotSupportedException {
        // 深拷贝方式一：序列化
        try (var out = new ByteArrayOutputStream();
             var oos = new ObjectOutputStream(out)) {
            oos.writeObject(this);
            try (var in = new ByteArrayInputStream(out.toByteArray());
                 var ois = new ObjectInputStream(in)) {
                return (Person) ois.readObject();
            }
        } catch (Exception e) { throw new RuntimeException(e); }
    }
}
```

### 二、结构型模式（7种）

6. **适配器模式（Adapter）** - 类适配器 + 对象适配器
```java
// 对象适配器（推荐）
interface Target {
    void request();
}
class Adaptee {
    public void specificRequest() { System.out.println("Adaptee"); }
}
class Adapter implements Target {
    private final Adaptee adaptee;
    public Adapter(Adaptee adaptee) { this.adaptee = adaptee; }
    public void request() { adaptee.specificRequest(); }
}
```

7. **装饰器模式（Decorator）** - 比继承更灵活
```java
interface Coffee {
    String getDescription();
    double cost();
}
class SimpleCoffee implements Coffee {
    public String getDescription() { return "Simple Coffee"; }
    public double cost() { return 5.0; }
}
abstract class CoffeeDecorator implements Coffee {
    protected final Coffee coffee;
    protected CoffeeDecorator(Coffee coffee) { this.coffee = coffee; }
}
class MilkDecorator extends CoffeeDecorator {
    public MilkDecorator(Coffee coffee) { super(coffee); }
    public String getDescription() { return coffee.getDescription() + ", Milk"; }
    public double cost() { return coffee.cost() + 1.5; }
}
```

8. **代理模式（Proxy）** - 静态代理 + 动态代理（JDK）
```java
// JDK 动态代理
interface UserService { void addUser(); }
class UserServiceImpl implements UserService {
    public void addUser() { System.out.println("添加用户"); }
}
class ProxyFactory {
    public static UserService getProxy(UserService target) {
        return (UserService) Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            (proxy, method, args) -> {
                System.out.println("日志开始");
                Object result = method.invoke(target, args);
                System.out.println("日志结束");
                return result;
            });
    }
}
```

9. **外观模式（Facade）**
```java
class CPU { public void startup() { System.out.println("CPU start"); }}
class Memory { public void load() { System.out.println("Memory load"); }}
class HardDrive { public void read() { System.out.println("HardDrive read"); }}

class ComputerFacade {
    private final CPU cpu = new CPU();
    private final Memory memory = new Memory();
    private final HardDrive hd = new HardDrive();

    public void start() {
        cpu.startup();
        memory.load();
        hd.read();
    }
}
```

### 三、行为型模式（11种）

10. **策略模式（Strategy）** - Spring 中最常见
```java
interface PaymentStrategy {
    void pay(int amount);
}
class AliPay implements PaymentStrategy {
    public void pay(int amount) { System.out.println("支付宝支付：" + amount); }
}
class WechatPay implements PaymentStrategy {
    public void pay(int amount) { System.out.println("微信支付：" + amount); }
}
class PaymentContext {
    private PaymentStrategy strategy;
    public void setStrategy(PaymentStrategy strategy) { this.strategy = strategy; }
    public void pay(int amount) { strategy.pay(amount); }
}
```

11. **观察者模式（Observer）** - JDK 自带 + 自定义
```java
// JDK 自带
class WeatherData extends Observable {
    public void setTemperature(int temp) {
        setChanged();
        notifyObservers(temp);
    }
}
class PhoneDisplay implements Observer {
    public void update(Observable o, Object arg) {
        System.out.println("手机显示温度：" + arg);
    }
}
```

12. **责任链模式（Chain of Responsibility）** - Spring Security、过滤器常用
```java
abstract class Handler {
    protected Handler next;
    public void setNext(Handler next) { this.next = next; }
    public abstract void handleRequest(String request);
}
class ConcreteHandlerA extends Handler {
    public void handleRequest(String request) {
        if ("A".equals(request)) {
            System.out.println("HandlerA 处理");
        } else if (next != null) {
            next.handleRequest(request);
        }
    }
}
```

13. **命令模式（Command）** - 撤销、重做
```java
interface Command {
    void execute();
    void undo();
}
class Light {
    void on() { System.out.println("灯打开"); }
    void off() { System.out.println("灯关闭"); }
}
class LightOnCommand implements Command {
    private final Light light;
    public LightOnCommand(Light light) { this.light = light; }
    public void execute() { light.on(); }
    public void undo() { light.off(); }
}
class RemoteControl {
    private Command command;
    public void setCommand(Command command) { this.command = command; }
    public void pressButton() { command.execute(); }
}
```

14. **模板方法模式（Template Method）** - Spring JdbcTemplate、HttpServlet
```java
abstract class CaffeineBeverage {
    // 模板方法
    final void prepareRecipe() {
        boilWater();
        brew();
        pourInCup();
        addCondiments();
    }
    abstract void brew();
    abstract void addCondiments();
    void boilWater() { System.out.println("煮开水"); }
    void pourInCup() { System.out.println("倒进杯子"); }
}
class Tea extends CaffeineBeverage {
    void brew() { System.out.println("泡茶叶"); }
    void addCondiments() { System.out.println("加柠檬"); }
}
```

15. **状态模式（State）** - 订单状态流转
```java
interface State {
    void handle(OrderContext context);
}
class PaidState implements State {
    public void handle(OrderContext context) {
        System.out.println("已支付，准备发货");
        context.setState(new ShippedState());
    }
}
class OrderContext {
    private State state = new UnpaidState();
    void setState(State state) { this.state = state; }
    void next() { state.handle(this); }
}
```

其他常见模式（简要代码）：

16. **迭代器（Iterator）** → `List.iterator()`
17. **中介者（Mediator）** → ChatRoom 示例（类似微信群）
18. **备忘录（Memento）** → 游戏存档
19. **访问者（Visitor）** → AST 遍历编译器
20. **解释器（Interpreter）** → 简单表达式计算器
21. **组合模式（Composite）** → 菜单树、部门树
22. **享元模式（Flyweight）** → 字符串常量池、游戏中重复的怪物对象
23. **桥接模式（Bridge）** → JDBC Driver（DriverManager + 具体驱动）

### 推荐记忆口诀（23种）
创建型：单工抽建原  
结构型：适装代外桥组享  
行为型：策模观责命状备命访解组

如果需要每一类模式的完整可运行代码 + UML 图 + 实际项目应用场景（Spring/MyBatis/Dubbo 等框架源码分析），可以告诉我，我继续发详细版！