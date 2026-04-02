# 1. 导入必要的库
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

# 2. 加载数据集
iris = load_iris()
X = iris.data  # 特征数据（4个特征）
y = iris.target  # 标签（3类鸢尾花：0/1/2）

# 3. 划分训练集和测试集（70%训练，30%测试）
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42  # random_state保证结果可复现
)

# 4. 初始化模型（逻辑回归）
model = LogisticRegression(max_iter=200)  # max_iter增大避免收敛问题

# 5. 训练模型
model.fit(X_train, y_train)

# 6. 模型评估（计算测试集准确率）
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"逻辑回归模型测试集准确率：{accuracy:.2f}")

# 7. 示例预测
sample = [[5.1, 3.5, 1.4, 0.2]]  # 第一类鸢尾花的特征
pred = model.predict(sample)
print(f"示例样本预测类别：{iris.target_names[pred[0]]}")