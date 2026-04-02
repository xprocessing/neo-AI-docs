训练**真正的视觉大模型（如ViT-L/14、ResNet-152等）**需要海量数据（如ImageNet-21k）和极高的算力（多GPU/TPU），普通环境无法实现。因此我们采用**“预训练大模型 + 迁移学习/微调”**的方案（这是实际应用中最常用的方式），用轻量代码实现：基于预训练的视觉大模型（如ResNet50/ViT）做图片分类，支持输入本地图片测试，还包含简单的微调示例。


### 一、准备工作：安装依赖
```bash
pip install torch torchvision pillow matplotlib
```


### 二、核心示例：用预训练视觉大模型做图片预测
我们选择**ResNet50（经典视觉大模型）**，它在ImageNet上预训练过，能识别1000类物体。直接用预训练模型测试图片，无需训练（若需微调可看后续步骤）。

#### 代码实现
```python
import torch
from torchvision import models, transforms
from PIL import Image
import matplotlib.pyplot as plt

# 1. 加载预训练的ResNet50大模型（ImageNet预训练）
model = models.resnet50(pretrained=True)
model.eval()  # 切换到评估模式（关闭dropout等）

# 2. 图片预处理（必须和预训练时的预处理一致）
preprocess = transforms.Compose([
    transforms.Resize(256),  # 缩放图片短边到256
    transforms.CenterCrop(224),  # 中心裁剪到224x224
    transforms.ToTensor(),  # 转成Tensor（0-1）
    transforms.Normalize(  # 按ImageNet均值/方差归一化
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])

# 3. 加载并预处理本地图片（替换成你的图片路径）
img_path = "test.jpg"  # 比如放一张猫/狗/苹果的图片
img = Image.open(img_path).convert("RGB")
plt.imshow(img)
plt.axis("off")
plt.show()

# 预处理图片
input_tensor = preprocess(img)
input_batch = input_tensor.unsqueeze(0)  # 增加batch维度（模型需要batch输入）

# 4. 预测（禁用梯度计算加速）
with torch.no_grad():
    output = model(input_batch)

# 5. 解析预测结果（取概率最高的类别）
_, pred_idx = torch.max(output, 1)
pred_idx = pred_idx.item()

# 加载ImageNet类别标签（1000类）
with open("imagenet_classes.txt", "w") as f:  # 先创建标签文件（也可直接下载）
    f.write("""tench, Tinca tinca
goldfish, Carassius auratus
...（完整标签可从https://gist.github.com/yrevar/942d3a0ac09ec9e5eb3a下载）""")

# 读取标签
with open("imagenet_classes.txt") as f:
    classes = [line.strip() for line in f.readlines()]

print(f"预测结果：{classes[pred_idx]}")
```

#### 补充：ImageNet标签获取
如果不想手动创建标签文件，可直接下载：  
```python
# 自动下载ImageNet标签
import requests
labels_url = "https://gist.githubusercontent.com/yrevar/942d3a0ac09ec9e5eb3a/raw/238f720ff059c1f82f368259d1ca4ffa5dd8f9f5/imagenet1000_clsidx_to_labels.txt"
labels = eval(requests.get(labels_url).text)
classes = [labels[i] for i in range(1000)]
```


### 三、进阶：简单微调预训练大模型（用CIFAR10数据集）
如果想体验“训练大模型”的过程，我们用CIFAR10（10类小数据集）对ResNet50做微调（冻结大部分层，只训练最后一层）：

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader

# 1. 数据加载与预处理
transform_train = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

# 加载CIFAR10数据集
train_dataset = datasets.CIFAR10(root="./data", train=True, download=True, transform=transform_train)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)

# 2. 加载预训练ResNet50，替换最后一层（适配CIFAR10的10类）
model = models.resnet50(pretrained=True)
# 冻结所有特征提取层（只训练最后一层）
for param in model.parameters():
    param.requires_grad = False
# 替换全连接层
model.fc = nn.Linear(model.fc.in_features, 10)

# 3. 训练设置
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.fc.parameters(), lr=0.001)  # 只优化最后一层

# 4. 微调训练（仅训练5轮，演示用）
epochs = 5
for epoch in range(epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * inputs.size(0)
    
    epoch_loss = running_loss / len(train_loader.dataset)
    print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}")

print("微调完成！")

# 5. 用微调后的模型测试自定义图片
# （复用前面的图片预处理代码）
img_path = "cat.jpg"  # CIFAR10包含猫、狗、飞机等10类
img = Image.open(img_path).convert("RGB")
input_tensor = preprocess(img).unsqueeze(0).to(device)

with torch.no_grad():
    output = model(input_tensor)
_, pred_idx = torch.max(output, 1)
cifar_classes = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]
print(f"微调后预测结果：{cifar_classes[pred_idx.item()]}")
```


### 关键说明
1. **“大模型”的实际应用**：我们用的ResNet50/ViT属于视觉大模型，直接用预训练权重即可做高精度预测；微调仅需训练最后几层，普通电脑（甚至CPU）也能运行。  
2. **图片要求**：测试图片可以是任意RGB图片（如手机拍的猫、狗、杯子等），预处理后输入模型即可。  
3. **算力优化**：如果没有GPU，用CPU也能运行（预测速度稍慢）。

通过这种方式，你既体验了“大模型”的使用，又能输入图片测试结果，且无需复杂的训练环境~