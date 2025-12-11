# 基于半监督学习的医学图像分割 - 主动学习扩展

## 功能说明

本项目是在原有半监督医学图像分割项目的基础上，添加了以下两个功能：

1. **主动学习**：使用主动学习算法对数据集进行筛选，筛选出最有价值的数据放入训练集的有标签数据子集。
2. **损失追踪**：动态追踪训练过程中损失函数的变化，并将损失历史保存到文件中。

## 数据集准备

### Pancreas数据集获取

请从以下链接获取Pancreas数据集：
[TCIA Pancreas-CT](https://www.cancerimagingarchive.net/collection/pancreas-ct/)

### 数据集结构

将获取的数据集解压到`dataset/Pancreas`文件夹中，数据集结构如下：

```
dataset/Pancreas/
├── Flods/
│   ├── test0.list
│   ├── test1.list
│   ├── test2.list
│   ├── test3.list
│   ├── train0.list
│   ├── train1.list
│   ├── train2.list
│   └── train3.list
├── case0001/
│   └── mri_norm2.h5
├── case0002/
│   └── mri_norm2.h5
└── ...
```

## 运行训练代码

### 基本训练

```bash
python code/train_MCF.py
```

### 带主动学习的训练

```bash
python code/train_MCF.py --active_learning True --query_strategy entropy --num_query 10 --query_interval 500
```

### 参数说明

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--active_learning` | 是否使用主动学习 | False |
| `--query_strategy` | 主动学习查询策略 | 'entropy' |
| `--num_query` | 每次查询的样本数量 | 10 |
| `--query_interval` | 查询间隔（迭代次数） | 500 |
| `--root_path` | 数据集路径 | '../dataset/Pancreas' |
| `--exp` | 实验名称 | 'MCF_flod0' |
| `--max_iterations` | 最大迭代次数 | 6000 |
| `--batch_size` | 批大小 | 4 |
| `--labeled_bs` | 有标签样本的批大小 | 2 |
| `--base_lr` | 基础学习率 | 0.01 |
| `--deterministic` | 是否使用确定性训练 | 1 |
| `--seed` | 随机种子 | 1337 |
| `--gpu` | 使用的GPU编号 | '0' |

### 主动学习查询策略

支持以下三种查询策略：

1. **entropy**：基于熵的查询策略，选择熵最大的样本。
2. **least_confidence**：基于最低置信度的查询策略，选择模型最不确定的样本。
3. **margin**：基于边缘的查询策略，选择两个最高预测概率之间差距最小的样本。

## 结果输出

### 模型保存

训练结束后，模型将保存到`../model/MCF_flod0/`文件夹中。

### 损失历史

训练过程中的损失历史将保存到`../model/MCF_flod0/loss_history.npy`文件中，可以使用numpy加载并分析损失变化。

```python
import numpy as np

loss_history = np.load('loss_history.npy', allow_pickle=True).item()
print(loss_history['v_loss'])  # VNet的损失历史
print(loss_history['r_loss'])  # ResNet的损失历史
```

### TensorBoard日志

训练过程中的日志将保存到`../model/MCF_flod0/log/`文件夹中，可以使用TensorBoard查看：

```bash
tensorboard --logdir ../model/MCF_flod0/log/
```

## 注意事项

1. 确保已经安装了所有依赖库，可以使用`pip install -r requirements.txt`安装。
2. 确保GPU可用，并且已经安装了CUDA和cuDNN。
3. 主动学习会增加训练时间，因为需要额外的推理时间来查询样本。
