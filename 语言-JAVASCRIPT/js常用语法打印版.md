// ==============================================
// JavaScript 核心语法速查 (A4纸打印版)
// 涵盖变量、数据类型、控制流、函数、对象、DOM等核心知识点
// ==============================================

// 1. 变量声明与数据类型
let num = 10;                // 块级作用域变量 (推荐)
const PI = 3.14159;          // 常量 (不可重新赋值)
var str = "Hello JavaScript";// 函数级作用域变量 (兼容旧代码)
let isTrue = true;           // 布尔值
let emptyVal = null;         // 空值
let undefVal;                // 未定义 (undefined)

// 数据类型检测
let typeCheck = typeof num;  // "number"
let arr = [1, 2, 3, "JS"];   // 数组
let obj = {                  // 对象 (键值对)
    name: "张三",
    age: 20,
    isStudent: false
};

// 2. 字符串操作
let strConcat = str + "!";   // 拼接
let strTemplate = `数值：${num}，PI：${PI.toFixed(2)}`; // 模板字符串
let strSlice = str.slice(0, 5); // 切片 (Hello)

// 3. 数组常用方法
arr.push(4);                // 尾部添加元素
arr.pop();                  // 尾部删除元素
arr.forEach((item, index) => { // 遍历
    // console.log(index, item);
});
let newArr = arr.map(item => item * 2); // 映射转换

// 4. 控制流语句
// 条件判断
let score = 85;
let grade;
if (score >= 90) {
    grade = "优秀";
} else if (score >= 80) {
    grade = "良好";
} else {
    grade = "及格";
}

// 三元运算符 (简化if-else)
let isAdult = obj.age >= 18 ? "成年" : "未成年";

// 循环语句
// for循环
let sum = 0;
for (let i = 1; i <= 10; i++) {
    sum += i; // 1-10累加
}

// while循环
let count = 0;
while (count < 5) {
    count++;
    if (count === 3) continue; // 跳过本次循环
    if (count === 5) break;    // 终止循环
}

// for...in (遍历对象属性)
for (let key in obj) {
    // console.log(key + ": " + obj[key]);
}

// for...of (遍历可迭代对象)
for (let item of arr) {
    // console.log(item);
}

// 5. 函数定义与使用
// 函数声明
function calculate(a, b, op = "+") { // 默认参数
    /**
     * 简单计算器
     * @param {number} a - 第一个数
     * @param {number} b - 第二个数
     * @param {string} op - 操作符，默认"+"
     * @returns {number|string} 计算结果
     */
    switch (op) {
        case "+": return a + b;
        case "-": return a - b;
        default: return "不支持的操作";
    }
}

// 函数表达式
const square = function(x) {
    return x * x;
};

// 箭头函数 (ES6)
const cube = x => x * x * x; // 简洁写法
const add = (a, b) => {      // 多行写法
    return a + b;
};

// 调用函数
let addResult = calculate(10, 5);
let squareResult = square(6);

// 6. 异常处理
try {
    let res = 10 / 0;        // Infinity，不会报错
    // let res = 10 / "a";   // 会触发错误
} catch (error) {
    console.error("错误信息：", error.message);
} finally {
    console.log("无论是否异常，都会执行");
}

// 7. 面向对象 (ES6 Class)
class Person {
    constructor(name, age) { // 构造函数
        this.name = name;
        this.age = age;
    }

    introduce() {            // 实例方法
        return `我叫${this.name}，今年${this.age}岁`;
    }

    static sayHello() {      // 静态方法
        return "你好！";
    }
}

// 创建实例
let person = new Person("李四", 25);
let intro = person.introduce();
let hello = Person.sayHello();

// 8. DOM操作 (浏览器环境)
// if (document) { // 确保在浏览器环境执行
//     // 获取元素
//     let div = document.getElementById("myDiv");
//     let btns = document.querySelectorAll("button");

//     // 修改样式
//     div.style.color = "red";
//     div.classList.add("active");

//     // 绑定事件
//     div.addEventListener("click", () => {
//         alert("点击了Div");
//     });
// }

// 9. 异步编程基础
// 定时器
setTimeout(() => {
    // console.log("1秒后执行");
}, 1000);

// Promise (异步处理)
const promise = new Promise((resolve, reject) => {
    let success = true;
    if (success) {
        resolve("操作成功");
    } else {
        reject("操作失败");
    }
});

// 调用Promise
promise.then(res => {
    // console.log(res);
}).catch(err => {
    // console.log(err);
});

// ==============================================
// 打印关键结果 (验证语法执行)
// ==============================================
console.log("1. 模板字符串：", strTemplate);
console.log("2. 1-10累加和：", sum);
console.log("3. 加法结果：", addResult);
console.log("4. 平方结果：", squareResult);
console.log("5. 人物介绍：", intro);