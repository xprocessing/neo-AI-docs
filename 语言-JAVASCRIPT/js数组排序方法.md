你想全面了解 JavaScript 中的数组排序方法，核心就是数组的 `sort()` 内置方法，我会从基础到进阶为你详细讲解，让你彻底掌握它的用法。

### 一、核心方法：`Array.prototype.sort()`
这是 JavaScript 数组专门用于排序的内置方法，**所有数组都可以直接调用**，它的核心特点和使用方式如下：

#### 1. 基础用法（无参数）
直接调用 `arr.sort()`，不传入任何比较函数。
```javascript
const arr1 = [3, 1, 5, 2, 4];
const arr2 = ["b", "a", "d", "c"];
const arr3 = [10, 2, 30, 4];

// 无参数排序
arr1.sort();
arr2.sort();
arr3.sort();

console.log(arr1); // [1, 2, 3, 4, 5]（看起来正常）
console.log(arr2); // ["a", "b", "c", "d"]（字符串排序正常）
console.log(arr3); // [10, 2, 30, 4]（出现问题！）
```

**关键说明**：
- 无参数时，`sort()` 会将数组中的元素**先转换成字符串**，然后按照「Unicode 字符编码顺序」进行排序（不是数值大小）。
- 优势：对 **纯字符串数组** 或 **范围在 0-9 的纯数字数组** 排序时，结果符合预期。
- 缺陷：对 **多位数数字数组** 排序时，会出现逻辑错误（比如上面的 `10` 排在 `2` 前面，因为字符串 `"10"` 的第一个字符 `"1"` 的 Unicode 码小于 `"2"`）。
- 额外注意：`sort()` 是 **原地排序**（会直接修改原始数组，而不是返回一个新的排序数组），如果需要保留原始数组，要先做数组拷贝（比如 `[...arr]`、`arr.slice()`）。

#### 2. 进阶用法（传入比较函数）
这是实际开发中最常用的方式，通过传入自定义比较函数，来指定具体的排序规则，解决无参数排序的缺陷。

##### 比较函数的基本规则
比较函数接收两个必选参数（通常命名为 `a`、`b`），代表数组中任意两个待比较的元素，排序结果由函数的**返回值**决定：
1.  返回 **负数**（`< 0`）：`a` 排在 `b` 前面（`a` 优先级更高）。
2.  返回 **0**：`a` 和 `b` 相对位置保持不变。
3.  返回 **正数**（`> 0`）：`b` 排在 `a` 前面（`b` 优先级更高）。

##### 常见场景示例
###### 场景1：数字数组的升序/降序排序
```javascript
const arr = [10, 2, 30, 4, 15.5];

// 1. 数值升序（从小到大）
arr.sort((a, b) => a - b);
console.log(arr); // [2, 4, 10, 15.5, 30]

// 2. 数值降序（从大到小）
arr.sort((a, b) => b - a);
console.log(arr); // [30, 15.5, 10, 4, 2]
```
**原理**：利用数字减法的结果，直接匹配比较函数的返回值规则，简单高效。

###### 场景2：对象数组按指定属性排序
这就是你之前提问的场景，数组元素是对象，需要按对象的某个属性（如 `totalFee`、`age`、`price`）排序。
```javascript
// 对象数组
const userList = [
  { name: "张三", age: 25, salary: "15000" },
  { name: "李四", age: 30, salary: "20000" },
  { name: "王五", age: 22, salary: "8000" },
  { name: "赵六", age: 28, salary: "abc" } // 无效薪资
];

// 1. 按 age 数值升序（从小到大）
userList.sort((a, b) => a.age - b.age);
console.log("按年龄升序：", userList);

// 2. 按 salary 数值降序（从大到小，带容错处理）
userList.sort((a, b) => {
  const salaryA = parseFloat(a.salary) || 0; // 转数字，无效值取 0
  const salaryB = parseFloat(b.salary) || 0;
  return salaryB - salaryA; // 降序：b - a
});
console.log("按薪资降序：", userList);
```

###### 场景3：字符串数组按中文拼音排序
无参数 `sort()` 无法正确排序中文，此时需要借助 `localeCompare()` 方法，在比较函数中实现中文拼音排序。
```javascript
const chineseArr = ["张三", "李四", "王五", "赵六"];

// 中文拼音升序（兼容大部分浏览器）
chineseArr.sort((a, b) => a.localeCompare(b, "zh-CN"));
console.log(chineseArr); // ["李四", "王五", "张三", "赵六"]
```
**说明**：`localeCompare()` 用于比较两个字符串，传入 `"zh-CN"` 表示按中文简体的拼音规则排序，返回值符合 `sort()` 比较函数的要求。

###### 场景4：按多个条件排序（优先级排序）
当第一个排序条件相等时，按第二个条件排序（比如先按年龄升序，年龄相同则按薪资降序）。
```javascript
const userList2 = [
  { name: "张三", age: 25, salary: 15000 },
  { name: "李四", age: 30, salary: 20000 },
  { name: "王五", age: 25, salary: 18000 },
];

// 先按 age 升序，age 相同则按 salary 降序
userList2.sort((a, b) => {
  // 第一个条件：年龄
  if (a.age !== b.age) {
    return a.age - b.age;
  }
  // 第二个条件：薪资（年龄相同时触发）
  return b.salary - a.salary;
});

console.log(userList2);
// 结果：张三（25/15000）→ 王五（25/18000）→ 李四（30/20000）
```

### 二、补充说明
1.  **原地排序的解决方案**：如果不想修改原始数组，排序前先拷贝数组。
    ```javascript
    const arr = [10, 2, 30];
    // 拷贝数组（两种常用方式）
    const newArr1 = [...arr];
    const newArr2 = arr.slice();
    // 对拷贝后的数组排序
    const sortedArr = newArr1.sort((a, b) => a - b);
    console.log(arr); // 原始数组不变：[10, 2, 30]
    console.log(sortedArr); // 排序后的数组：[2, 10, 30]
    ```
2.  **特殊值处理**：数组中的 `undefined` 会被排到数组末尾（无论升序还是降序）。
3.  **稳定性**：ES6 之后，`sort()` 是**稳定排序**（即两个相等的元素，排序后相对位置不变），这对多条件排序很重要。

### 总结
1.  JavaScript 数组排序的核心是 `sort()` 方法，它是原地排序，会修改原始数组。
2.  无参数 `sort()` 按字符串 Unicode 排序，仅适用于纯字符串或 0-9 数字数组。
3.  传入比较函数是主流用法，通过返回值控制排序规则，支持数字、对象、中文等多种场景。
4.  升序排序（数字/可转数字属性）用 `a - b`，降序用 `b - a`，多条件排序可在比较函数内嵌套判断。