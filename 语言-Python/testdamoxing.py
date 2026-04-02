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