# 主动学习和损失追踪功能说明

## 主动学习功能

### 功能描述
主动学习是一种机器学习方法，通过选择最有价值的未标记样本进行标记，从而减少标记成本并提高模型性能。本项目实现了三种主动学习查询策略：

1. **Entropy (熵)**：选择预测熵最高的样本，即模型最不确定的样本。
2. **Margin (边缘)**：选择预测概率最高的两个类之间差异最小的样本。
3. **Least Confidence (最低置信度)**：选择模型对预测结果最不自信的样本。

### 使用方法

在训练时添加以下命令行参数来启用主动学习：

```bash
python code/train_MCF.py --active_learning True --query_strategy entropy --num_query 10 --query_interval 500
```

参数说明：
- `--active_learning`：是否启用主动学习，默认为False
- `--query_strategy`：选择查询策略，可选值为'entropy'、'margin'、'least_confidence'，默认为'entropy'
- `--num_query`：每次查询选择的样本数量，默认为10
- `--query_interval`：查询间隔（迭代次数），默认为500

## 损失追踪功能

### 功能描述
损失追踪功能用于记录训练过程中损失函数的变化，包括v_loss、r_loss、v_supervised_loss和r_supervised_loss。训练结束后，损失历史将保存为npy文件，以便后续分析和可视化。

### 使用方法

损失追踪功能默认启用，无需额外参数。训练结束后，损失历史将保存到模型快照目录下的`loss_history.npy`文件中。

### 示例代码

以下示例代码展示了如何加载和可视化损失历史：

```python
import numpy as np
import matplotlib.pyplot as plt

# 加载损失历史
loss_history = np.load('model/MCF_flod0/loss_history.npy', allow_pickle=True).item()

# 绘制损失曲线
plt.figure(figsize=(10, 6))
plt.plot(loss_history['iter'], loss_history['v_loss'], label='v_loss')
plt.plot(loss_history['iter'], loss_history['r_loss'], label='r_loss')
plt.plot(loss_history['iter'], loss_history['v_supervised_loss'], label='v_supervised_loss')
plt.plot(loss_history['iter'], loss_history['r_supervised_loss'], label='r_supervised_loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')
plt.title('Training Loss History')
plt.legend()
plt.show()
```

## 数据集获取

项目使用Pancreas数据集，可以从以下链接获取：
- [TCIA Pancreas-CT数据集](https://www.cancerimagingarchive.net/collection/pancreas-ct/)

下载后，请将数据集放置在`dataset/Pancreas`目录下，并确保文件结构符合项目要求。