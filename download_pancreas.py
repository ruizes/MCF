import requests
import os
import zipfile
from tqdm import tqdm

# Pancreas数据集h5文件下载链接（TCIA官方网站）
dataset_url = "https://wiki.cancerimagingarchive.net/display/Public/Pancreas-CT"

# 数据集保存路径
save_path = "d:\\MCF\\dataset\\Pancreas"

# 创建保存目录
if not os.path.exists(save_path):
    os.makedirs(save_path)

# 下载数据集
print("开始下载Pancreas数据集...")
print("请访问以下链接下载Pancreas数据集：")
print(dataset_url)
print("下载完成后将文件解压到：", save_path)
print("然后手动将h5文件复制到该目录下。")