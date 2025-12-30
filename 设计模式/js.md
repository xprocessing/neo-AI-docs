以下是 JavaScript 中常用设计模式的实现示例，涵盖创建型、结构型和行为型模式：

### 一、创建型模式
#### 1. 单例模式（Singleton）
**核心**：保证一个类只有一个实例，并提供全局访问点。

```javascript
class Singleton {
  constructor(name) {
    this.name = name;
  }

  static getInstance(name) {
    if (!Singleton.instance) {
      Singleton.instance = new Singleton(name);
    }
    return Singleton.instance;
  }
}

// 测试
const instance1 = Singleton.getInstance('实例1');
const instance2 = Singleton.getInstance('实例2');

console.log(instance1 === instance2); // true
console.log(instance1.name); // 实例1（后续调用不改变实例）
```

#### 2. 工厂模式（Factory）
**核心**：提供一个统一的接口，根据传入参数创建不同的对象。

```javascript
class ProductA {
  constructor() {
    this.name = '产品A';
  }
}

class ProductB {
  constructor() {
    this.name = '产品B';
  }
}

class Factory {
  static createProduct(type) {
    switch (type) {
      case 'A':
        return new ProductA();
      case 'B':
        return new ProductB();
      default:
        throw new Error(`不支持的产品类型：${type}`);
    }
  }
}

// 测试
const product1 = Factory.createProduct('A');
const product2 = Factory.createProduct('B');

console.log(product1.name); // 产品A
console.log(product2.name); // 产品B
```

#### 3. 建造者模式（Builder）
**核心**：将复杂对象的构建与表示分离，分步构建对象。

```javascript
class Computer {
  constructor() {
    this.cpu = '';
    this.memory = '';
    this.hardDisk = '';
  }

  toString() {
    return `CPU: ${this.cpu}, 内存: ${this.memory}, 硬盘: ${this.hardDisk}`;
  }
}

class ComputerBuilder {
  constructor() {
    this.computer = new Computer();
  }

  buildCPU(cpu) {
    this.computer.cpu = cpu;
    return this; // 链式调用
  }

  buildMemory(memory) {
    this.computer.memory = memory;
    return this;
  }

  buildHardDisk(hardDisk) {
    this.computer.hardDisk = hardDisk;
    return this;
  }

  getResult() {
    return this.computer;
  }
}

// 测试
const computer = new ComputerBuilder()
  .buildCPU('Intel i7')
  .buildMemory('16GB')
  .buildHardDisk('1TB SSD')
  .getResult();

console.log(computer.toString());
// CPU: Intel i7, 内存: 16GB, 硬盘: 1TB SSD
```

### 二、结构型模式
#### 1. 适配器模式（Adapter）
**核心**：将一个类的接口转换成客户端期望的另一个接口，解决接口不兼容问题。

```javascript
// 旧接口（需要适配的类）
class OldCalculator {
  operation(num1, num2, operator) {
    switch (operator) {
      case '+':
        return num1 + num2;
      case '-':
        return num1 - num2;
      default:
        return 0;
    }
  }
}

// 目标接口（客户端期望的接口）
class NewCalculator {
  add(num1, num2) {
    return num1 + num2;
  }

  subtract(num1, num2) {
    return num1 - num2;
  }
}

// 适配器类（适配旧接口到新接口）
class CalculatorAdapter extends NewCalculator {
  constructor() {
    super();
    this.oldCalculator = new OldCalculator();
  }

  add(num1, num2) {
    return this.oldCalculator.operation(num1, num2, '+');
  }

  subtract(num1, num2) {
    return this.oldCalculator.operation(num1, num2, '-');
  }
}

// 测试
const adapter = new CalculatorAdapter();
console.log(adapter.add(10, 5)); // 15
console.log(adapter.subtract(10, 5)); // 5
```

#### 2. 装饰器模式（Decorator）
**核心**：动态地给对象添加额外功能，不改变原对象结构。

```javascript
// 基础类
class Coffee {
  cost() {
    return 10; // 基础咖啡价格
  }

  description() {
    return '基础咖啡';
  }
}

// 装饰器：牛奶
class MilkDecorator extends Coffee {
  constructor(coffee) {
    super();
    this.coffee = coffee;
  }

  cost() {
    return this.coffee.cost() + 3; // 加牛奶加3元
  }

  description() {
    return `${this.coffee.description()} + 牛奶`;
  }
}

// 装饰器：糖
class SugarDecorator extends Coffee {
  constructor(coffee) {
    super();
    this.coffee = coffee;
  }

  cost() {
    return this.coffee.cost() + 2; // 加糖加2元
  }

  description() {
    return `${this.coffee.description()} + 糖`;
  }
}

// 测试
let coffee = new Coffee();
console.log(coffee.description(), '价格：', coffee.cost());
// 基础咖啡 价格： 10

coffee = new MilkDecorator(coffee);
console.log(coffee.description(), '价格：', coffee.cost());
// 基础咖啡 + 牛奶 价格： 13

coffee = new SugarDecorator(coffee);
console.log(coffee.description(), '价格：', coffee.cost());
// 基础咖啡 + 牛奶 + 糖 价格： 15
```

#### 3. 代理模式（Proxy）
**核心**：为对象提供一个代理，控制对原对象的访问（如权限控制、缓存、日志等）。

```javascript
// 原对象（真实主题）
class RealImage {
  constructor(filename) {
    this.filename = filename;
    this.loadFromDisk(); // 模拟从磁盘加载图片（耗时操作）
  }

  display() {
    console.log(`显示图片：${this.filename}`);
  }

  loadFromDisk() {
    console.log(`从磁盘加载图片：${this.filename}`);
  }
}

// 代理对象
class ProxyImage {
  constructor(filename) {
    this.filename = filename;
    this.realImage = null; // 延迟初始化原对象
  }

  display() {
    // 只有当需要显示时，才创建原对象（懒加载）
    if (!this.realImage) {
      this.realImage = new RealImage(this.filename);
    }
    this.realImage.display();
  }
}

// 测试
const image = new ProxyImage('test.jpg');

// 第一次显示：加载图片并显示
image.display();
// 从磁盘加载图片：test.jpg
// 显示图片：test.jpg

// 第二次显示：直接显示（无需重新加载）
image.display();
// 显示图片：test.jpg
```

### 三、行为型模式
#### 1. 观察者模式（Observer）
**核心**：定义对象间的一对多依赖关系，当一个对象状态改变时，所有依赖它的对象都会收到通知并自动更新。

```javascript
class Subject {
  constructor() {
    this.observers = []; // 存储所有观察者
  }

  // 添加观察者
  addObserver(observer) {
    this.observers.push(observer);
  }

  // 移除观察者
  removeObserver(observer) {
    this.observers = this.observers.filter(obs => obs !== observer);
  }

  // 通知所有观察者
  notify(message) {
    this.observers.forEach(observer => observer.update(message));
  }
}

// 观察者1
class Observer1 {
  update(message) {
    console.log(`观察者1收到消息：${message}`);
  }
}

// 观察者2
class Observer2 {
  update(message) {
    console.log(`观察者2收到消息：${message}`);
  }
}

// 测试
const subject = new Subject();
const observer1 = new Observer1();
const observer2 = new Observer2();

subject.addObserver(observer1);
subject.addObserver(observer2);

subject.notify('Hello World!');
// 观察者1收到消息：Hello World!
// 观察者2收到消息：Hello World!

subject.removeObserver(observer1);
subject.notify('Goodbye!');
// 观察者2收到消息：Goodbye!
```

#### 2. 策略模式（Strategy）
**核心**：定义一系列算法，将每个算法封装起来，并使它们可互换。客户端可以根据需要选择不同的算法。

```javascript
// 策略接口（统一算法接口）
class Strategy {
  calculate(num1, num2) {
    throw new Error('子类必须实现 calculate 方法');
  }
}

// 加法策略
class AddStrategy extends Strategy {
  calculate(num1, num2) {
    return num1 + num2;
  }
}

// 减法策略
class SubtractStrategy extends Strategy {
  calculate(num1, num2) {
    return num1 - num2;
  }
}

// 乘法策略
class MultiplyStrategy extends Strategy {
  calculate(num1, num2) {
    return num1 * num2;
  }
}

// 上下文类（使用策略的类）
class Calculator {
  constructor(strategy) {
    this.strategy = strategy;
  }

  setStrategy(strategy) {
    this.strategy = strategy; // 动态切换策略
  }

  compute(num1, num2) {
    return this.strategy.calculate(num1, num2);
  }
}

// 测试
const calculator = new Calculator(new AddStrategy());
console.log('加法：', calculator.compute(10, 5)); // 15

calculator.setStrategy(new SubtractStrategy());
console.log('减法：', calculator.compute(10, 5)); // 5

calculator.setStrategy(new MultiplyStrategy());
console.log('乘法：', calculator.compute(10, 5)); // 50
```

#### 3. 迭代器模式（Iterator）
**核心**：提供一种方法顺序访问聚合对象中的元素，而无需暴露聚合对象的内部结构。

```javascript
// 迭代器接口
class Iterator {
  hasNext() {
    throw new Error('子类必须实现 hasNext 方法');
  }

  next() {
    throw new Error('子类必须实现 next 方法');
  }
}

// 具体迭代器（数组迭代器）
class ArrayIterator extends Iterator {
  constructor(array) {
    super();
    this.array = array;
    this.index = 0;
  }

  hasNext() {
    return this.index < this.array.length;
  }

  next() {
    if (this.hasNext()) {
      return this.array[this.index++];
    }
    return null;
  }
}

// 聚合对象（数组聚合）
class ArrayAggregate {
  constructor(array) {
    this.array = array;
  }

  createIterator() {
    return new ArrayIterator(this.array); // 返回迭代器
  }
}

// 测试
const aggregate = new ArrayAggregate([1, 2, 3, 4, 5]);
const iterator = aggregate.createIterator();

while (iterator.hasNext()) {
  console.log(iterator.next()); // 1, 2, 3, 4, 5
}
```

### 总结
- **创建型模式**：关注对象的创建过程（单例、工厂、建造者）。
- **结构型模式**：关注对象的组合与结构（适配器、装饰器、代理）。
- **行为型模式**：关注对象的行为与交互（观察者、策略、迭代器）。

这些设计模式可以帮助你编写更灵活、可维护和可扩展的 JavaScript 代码，根据实际场景选择合适的模式即可。