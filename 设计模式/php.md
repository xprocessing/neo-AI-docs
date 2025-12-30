以下是PHP中常用设计模式的代码实现，包含每种模式的核心思想、适用场景和完整示例：

### 一、单例模式（Singleton）
**核心思想**：保证一个类只有一个实例，并提供全局访问点。

**适用场景**：数据库连接、缓存服务、日志系统等需要共享资源的场景。

```php
class Database {
    // 私有静态实例（确保唯一）
    private static ?Database $instance = null;
    
    // 私有构造函数（禁止外部实例化）
    private function __construct() {
        // 模拟数据库连接
        echo "数据库连接成功\n";
    }
    
    // 私有克隆方法（禁止克隆）
    private function __clone() {}
    
    // 私有序列化方法（禁止序列化）
    private function __wakeup() {}
    
    // 公共静态方法（获取唯一实例）
    public static function getInstance(): Database {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    // 示例方法
    public function query(string $sql): void {
        echo "执行SQL：{$sql}\n";
    }
}

// 使用示例
$db1 = Database::getInstance();
$db2 = Database::getInstance();
var_dump($db1 === $db2); // bool(true)（证明是同一个实例）
$db1->query("SELECT * FROM users");
```


### 二、工厂模式（Factory）
**核心思想**：定义一个创建对象的接口，让子类决定实例化哪个类，将对象创建与使用分离。

**适用场景**：对象创建逻辑复杂、需要根据条件动态创建不同对象的场景。

```php
// 产品接口（定义统一方法）
interface Product {
    public function getName(): string;
}

// 具体产品A
class ConcreteProductA implements Product {
    public function getName(): string {
        return "产品A";
    }
}

// 具体产品B
class ConcreteProductB implements Product {
    public function getName(): string {
        return "产品B";
    }
}

// 工厂类（负责创建产品）
class ProductFactory {
    public static function createProduct(string $type): Product {
        return match ($type) {
            'A' => new ConcreteProductA(),
            'B' => new ConcreteProductB(),
            default => throw new InvalidArgumentException("未知产品类型：{$type}"),
        };
    }
}

// 使用示例
$productA = ProductFactory::createProduct('A');
$productB = ProductFactory::createProduct('B');
echo $productA->getName(); // 输出：产品A
echo $productB->getName(); // 输出：产品B
```


### 三、抽象工厂模式（Abstract Factory）
**核心思想**：提供一个创建一系列相关或相互依赖对象的接口，无需指定具体类。

**适用场景**：需要创建多个系列的产品（如不同品牌的手机、电脑），且产品之间存在依赖关系。

```php
// 抽象产品A（手机接口）
interface Phone {
    public function call(): string;
}

// 抽象产品B（电脑接口）
interface Computer {
    public function code(): string;
}

// 具体产品A1（华为手机）
class HuaweiPhone implements Phone {
    public function call(): string {
        return "用华为手机打电话\n";
    }
}

// 具体产品B1（华为电脑）
class HuaweiComputer implements Computer {
    public function code(): string {
        return "用华为电脑写代码\n";
    }
}

// 具体产品A2（苹果手机）
class ApplePhone implements Phone {
    public function call(): string {
        return "用苹果手机打电话\n";
    }
}

// 具体产品B2（苹果电脑）
class AppleComputer implements Computer {
    public function code(): string {
        return "用苹果电脑写代码\n";
    }
}

// 抽象工厂接口（定义创建产品的方法）
interface AbstractFactory {
    public function createPhone(): Phone;
    public function createComputer(): Computer;
}

// 具体工厂1（华为工厂）
class HuaweiFactory implements AbstractFactory {
    public function createPhone(): Phone {
        return new HuaweiPhone();
    }
    
    public function createComputer(): Computer {
        return new HuaweiComputer();
    }
}

// 具体工厂2（苹果工厂）
class AppleFactory implements AbstractFactory {
    public function createPhone(): Phone {
        return new ApplePhone();
    }
    
    public function createComputer(): Computer {
        return new AppleComputer();
    }
}

// 使用示例
$huaweiFactory = new HuaweiFactory();
$huaweiPhone = $huaweiFactory->createPhone();
$huaweiComputer = $huaweiFactory->createComputer();
echo $huaweiPhone->call(); // 输出：用华为手机打电话
echo $huaweiComputer->code(); // 输出：用华为电脑写代码

$appleFactory = new AppleFactory();
$applePhone = $appleFactory->createPhone();
$appleComputer = $appleFactory->createComputer();
echo $applePhone->call(); // 输出：用苹果手机打电话
echo $appleComputer->code(); // 输出：用苹果电脑写代码
```


### 四、建造者模式（Builder）
**核心思想**：将复杂对象的构建过程与表示分离，使得同样的构建过程可以创建不同的表示。

**适用场景**：创建复杂对象（如汽车、文档），且对象的组成部分需要逐步构建。

```php
// 产品类（汽车）
class Car {
    private array $parts = [];
    
    public function addPart(string $part): void {
        $this->parts[] = $part;
    }
    
    public function showParts(): void {
        echo "汽车部件：" . implode(', ', $this->parts) . "\n";
    }
}

// 抽象建造者接口
interface CarBuilder {
    public function buildEngine(): void;
    public function buildWheel(): void;
    public function buildBody(): void;
    public function getCar(): Car;
}

// 具体建造者（普通汽车）
class CommonCarBuilder implements CarBuilder {
    private Car $car;
    
    public function __construct() {
        $this->car = new Car();
    }
    
    public function buildEngine(): void {
        $this->car->addPart("普通发动机");
    }
    
    public function buildWheel(): void {
        $this->car->addPart("普通轮胎");
    }
    
    public function buildBody(): void {
        $this->car->addPart("普通车身");
    }
    
    public function getCar(): Car {
        return $this->car;
    }
}

// 具体建造者（豪华汽车）
class LuxuryCarBuilder implements CarBuilder {
    private Car $car;
    
    public function __construct() {
        $this->car = new Car();
    }
    
    public function buildEngine(): void {
        $this->car->addPart("豪华发动机");
    }
    
    public function buildWheel(): void {
        $this->car->addPart("豪华轮胎");
    }
    
    public function buildBody(): void {
        $this->car->addPart("豪华车身");
    }
    
    public function getCar(): Car {
        return $this->car;
    }
}

// 指挥者（负责控制建造流程）
class Director {
    public function buildCar(CarBuilder $builder): Car {
        $builder->buildEngine();
        $builder->buildWheel();
        $builder->buildBody();
        return $builder->getCar();
    }
}

// 使用示例
$director = new Director();

// 建造普通汽车
$commonBuilder = new CommonCarBuilder();
$commonCar = $director->buildCar($commonBuilder);
$commonCar->showParts(); // 输出：汽车部件：普通发动机, 普通轮胎, 普通车身

// 建造豪华汽车
$luxuryBuilder = new LuxuryCarBuilder();
$luxuryCar = $director->buildCar($luxuryBuilder);
$luxuryCar->showParts(); // 输出：汽车部件：豪华发动机, 豪华轮胎, 豪华车身
```


### 五、原型模式（Prototype）
**核心思想**：用原型实例指定创建对象的种类，通过复制这个原型来创建新对象。

**适用场景**：对象创建成本高（如数据库查询、复杂计算），且需要多次创建相似对象的场景。

```php
// 原型接口（必须实现克隆方法）
interface Prototype {
    public function clone(): self;
}

// 具体原型（用户对象）
class User implements Prototype {
    private string $name;
    private int $age;
    private array $hobbies;
    
    public function __construct(string $name, int $age, array $hobbies) {
        $this->name = $name;
        $this->age = $age;
        $this->hobbies = $hobbies;
        echo "创建用户对象（成本较高）\n";
    }
    
    // 实现克隆方法（深克隆）
    public function clone(): self {
        // 深克隆：复制所有属性（包括引用类型）
        return new self(
            $this->name,
            $this->age,
            $this->hobbies // 数组在PHP中克隆是深拷贝，若有对象需手动处理
        );
    }
    
    // 示例方法
    public function showInfo(): void {
        echo "姓名：{$this->name}，年龄：{$this->age}，爱好：" . implode(', ', $this->hobbies) . "\n";
    }
    
    // 修改属性的方法
    public function setName(string $name): void {
        $this->name = $name;
    }
}

// 使用示例
// 1. 创建原型对象（成本高）
$prototypeUser = new User("张三", 25, ["篮球", "游戏"]);
$prototypeUser->showInfo(); // 输出：姓名：张三，年龄：25，爱好：篮球, 游戏

// 2. 克隆原型对象（成本低）
$user1 = $prototypeUser->clone();
$user1->setName("李四");
$user1->showInfo(); // 输出：姓名：李四，年龄：25，爱好：篮球, 游戏

$user2 = $prototypeUser->clone();
$user2->setName("王五");
$user2->showInfo(); // 输出：姓名：王五，年龄：25，爱好：篮球, 游戏
```


### 六、适配器模式（Adapter）
**核心思想**：将一个类的接口转换成客户端期望的另一个接口，解决接口不兼容问题。

**适用场景**：集成第三方库、旧系统改造、接口升级等需要兼容不同接口的场景。

```php
// 目标接口（客户端期望的接口）
interface Target {
    public function request(): string;
}

// 适配者（需要被适配的旧接口）
class Adaptee {
    public function specificRequest(): string {
        return "旧系统的特殊请求";
    }
}

// 适配器（连接目标接口和适配者）
class Adapter implements Target {
    private Adaptee $adaptee;
    
    public function __construct(Adaptee $adaptee) {
        $this->adaptee = $adaptee;
    }
    
    public function request(): string {
        // 适配旧接口到新接口
        $result = $this->adaptee->specificRequest();
        return "适配器转换：{$result} → 新系统的标准响应";
    }
}

// 使用示例
// 客户端只知道目标接口Target
$target = new Adapter(new Adaptee());
echo $target->request(); // 输出：适配器转换：旧系统的特殊请求 → 新系统的标准响应
```


### 七、装饰器模式（Decorator）
**核心思想**：动态地给对象添加额外职责，不改变原类结构。

**适用场景**：需要给对象动态添加功能、功能可组合的场景（如日志、缓存、权限控制）。

```php
// 抽象组件（定义核心功能）
interface Component {
    public function operation(): string;
}

// 具体组件（实现核心功能）
class ConcreteComponent implements Component {
    public function operation(): string {
        return "核心功能";
    }
}

// 抽象装饰器（继承组件接口，持有组件实例）
abstract class Decorator implements Component {
    protected Component $component;
    
    public function __construct(Component $component) {
        $this->component = $component;
    }
    
    abstract public function operation(): string;
}

// 具体装饰器A（添加日志功能）
class LogDecorator extends Decorator {
    public function operation(): string {
        return "日志记录 → " . $this->component->operation();
    }
}

// 具体装饰器B（添加缓存功能）
class CacheDecorator extends Decorator {
    public function operation(): string {
        return "缓存处理 → " . $this->component->operation();
    }
}

// 使用示例
// 1. 基础功能
$component = new ConcreteComponent();
echo $component->operation() . "\n"; // 输出：核心功能

// 2. 添加日志功能
$logDecorator = new LogDecorator($component);
echo $logDecorator->operation() . "\n"; // 输出：日志记录 → 核心功能

// 3. 同时添加日志和缓存功能（装饰器组合）
$cacheDecorator = new CacheDecorator($logDecorator);
echo $cacheDecorator->operation() . "\n"; // 输出：缓存处理 → 日志记录 → 核心功能
```


### 八、观察者模式（Observer）
**核心思想**：定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会收到通知并自动更新。

**适用场景**：事件监听、消息通知、状态同步等场景（如订单状态变更通知、公众号推送）。

```php
// 抽象主题（被观察者）
interface Subject {
    public function attach(Observer $observer): void; // 添加观察者
    public function detach(Observer $observer): void; // 移除观察者
    public function notify(): void; // 通知所有观察者
}

// 抽象观察者
interface Observer {
    public function update(Subject $subject): void; // 接收通知并更新
}

// 具体主题（订单）
class Order implements Subject {
    private string $status;
    private array $observers = [];
    
    public function setStatus(string $status): void {
        $this->status = $status;
        $this->notify(); // 状态改变时通知观察者
    }
    
    public function getStatus(): string {
        return $this->status;
    }
    
    public function attach(Observer $observer): void {
        $this->observers[] = $observer;
    }
    
    public function detach(Observer $observer): void {
        $index = array_search($observer, $this->observers);
        if ($index !== false) {
            unset($this->observers[$index]);
        }
    }
    
    public function notify(): void {
        foreach ($this->observers as $observer) {
            $observer->update($this);
        }
    }
}

// 具体观察者（用户通知）
class UserNotifier implements Observer {
    public function update(Subject $subject): void {
        if ($subject instanceof Order) {
            echo "用户收到通知：订单状态已变更为「{$subject->getStatus()}」\n";
        }
    }
}

// 具体观察者（库存更新）
class InventoryUpdater implements Observer {
    public function update(Subject $subject): void {
        if ($subject instanceof Order) {
            echo "库存系统更新：订单状态为「{$subject->getStatus()}」，开始处理库存\n";
        }
    }
}

// 使用示例
$order = new Order();
$userNotifier = new UserNotifier();
$inventoryUpdater = new InventoryUpdater();

// 添加观察者
$order->attach($userNotifier);
$order->attach($inventoryUpdater);

// 改变订单状态（触发通知）
$order->setStatus("已支付");
// 输出：
// 用户收到通知：订单状态已变更为「已支付」
// 库存系统更新：订单状态为「已支付」，开始处理库存

$order->setStatus("已发货");
// 输出：
// 用户收到通知：订单状态已变更为「已发货」
// 库存系统更新：订单状态为「已发货」，开始处理库存
```


### 九、策略模式（Strategy）
**核心思想**：定义一系列算法，将每个算法封装起来，并让它们可以相互替换。

**适用场景**：需要根据不同条件选择不同算法（如支付方式、排序算法、折扣计算）。

```php
// 策略接口（定义算法统一方法）
interface Strategy {
    public function calculate(float $price): float;
}

// 具体策略A（满减策略）
class FullReduceStrategy implements Strategy {
    public function calculate(float $price): float {
        if ($price >= 100) {
            return $price - 20;
        }
        return $price;
    }
}

// 具体策略B（折扣策略）
class DiscountStrategy implements Strategy {
    public function calculate(float $price): float {
        return $price * 0.9; // 9折
    }
}

// 具体策略C（无优惠策略）
class NoDiscountStrategy implements Strategy {
    public function calculate(float $price): float {
        return $price;
    }
}

// 上下文类（使用策略的场景）
class PriceCalculator {
    private Strategy $strategy;
    
    public function __construct(Strategy $strategy) {
        $this->strategy = $strategy;
    }
    
    // 切换策略
    public function setStrategy(Strategy $strategy): void {
        $this->strategy = $strategy;
    }
    
    // 计算最终价格
    public function calculateFinalPrice(float $price): float {
        return $this->strategy->calculate($price);
    }
}

// 使用示例
$calculator = new PriceCalculator(new NoDiscountStrategy());

// 无优惠
echo $calculator->calculateFinalPrice(80) . "\n"; // 输出：80

// 切换到满减策略
$calculator->setStrategy(new FullReduceStrategy());
echo $calculator->calculateFinalPrice(100) . "\n"; // 输出：80

// 切换到折扣策略
$calculator->setStrategy(new DiscountStrategy());
echo $calculator->calculateFinalPrice(100) . "\n"; // 输出：90
```


### 十、代理模式（Proxy）
**核心思想**：为其他对象提供一种代理以控制对这个对象的访问。

**适用场景**：延迟加载、权限控制、日志记录、缓存等需要控制对象访问的场景。

```php
// 抽象主题（定义核心功能）
interface Image {
    public function display(): void;
}

// 真实主题（实际执行功能的对象）
class RealImage implements Image {
    private string $filename;
    
    public function __construct(string $filename) {
        $this->filename = $filename;
        $this->loadFromDisk(); // 模拟从磁盘加载图片（成本高）
    }
    
    private function loadFromDisk(): void {
        echo "加载图片：{$this->filename}（耗时操作）\n";
    }
    
    public function display(): void {
        echo "显示图片：{$this->filename}\n";
    }
}

// 代理主题（控制对真实主题的访问）
class ProxyImage implements Image {
    private ?RealImage $realImage = null;
    private string $filename;
    
    public function __construct(string $filename) {
        $this->filename = $filename;
    }
    
    public function display(): void {
        // 延迟加载：只有当需要显示时才创建真实对象
        if ($this->realImage === null) {
            $this->realImage = new RealImage($this->filename);
        }
        $this->realImage->display();
    }
}

// 使用示例
// 1. 使用代理加载图片（延迟加载）
$proxyImage = new ProxyImage("test.jpg");
echo "准备显示图片...\n";
$proxyImage->display(); // 此时才加载图片并显示
// 输出：
// 准备显示图片...
// 加载图片：test.jpg（耗时操作）
// 显示图片：test.jpg

// 2. 再次显示（直接使用已创建的真实对象）
$proxyImage->display();
// 输出：
// 显示图片：test.jpg
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