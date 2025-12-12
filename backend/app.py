from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import numpy as np
import torch
import sys
sys.path.append('D:\\MCF\\code')
from networks.vnet import VNet
from networks.ResNet34 import Resnet34
import h5py
import nibabel as nib

app = Flask(__name__)
CORS(app)

# 加载预训练模型
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# 创建模型
model_vnet = VNet(n_channels=1, n_classes=2, normalization='batchnorm', has_dropout=True)
model_resnet = Resnet34(n_channels=1, n_classes=2, normalization='batchnorm', has_dropout=True)

# 加载预训练权重
model_vnet.load_state_dict(torch.load('../model/MCF_flod0/vnet_best_model.pth'))
model_resnet.load_state_dict(torch.load('../model/MCF_flod0/resnet_best_model.pth'))

model_vnet.to(device)
model_resnet.to(device)

model_vnet.eval()
model_resnet.eval()

# 图像预处理
def preprocess_image(image_path):
    # 读取医学图像
    if image_path.endswith('.h5'):
        with h5py.File(image_path, 'r') as f:
            image = f['image'][:]
    elif image_path.endswith('.nii') or image_path.endswith('.nii.gz'):
        nib_image = nib.load(image_path)
        image = nib_image.get_fdata()
    else:
        raise ValueError('不支持的图像格式')
    
    # 归一化
    image = (image - np.mean(image)) / np.std(image)
    
    # 添加通道维度
    image = np.expand_dims(image, axis=0)
    
    # 转换为PyTorch张量
    image = torch.from_numpy(image).float().to(device)
    
    return image

# 分割图像
def segment_image(image):
    with torch.no_grad():
        v_output = model_vnet(image)
        r_output = model_resnet(image)
        
        # 融合两个模型的输出
        output = (v_output + r_output) / 2
        
        # 转换为分割掩码
        mask = torch.argmax(output, dim=1)
        
        return mask.cpu().numpy()

# 保存分割结果
def save_segmentation_result(mask, output_path):
    # 转换为NIfTI格式
    nib_mask = nib.Nifti1Image(mask, np.eye(4))
    nib.save(nib_mask, output_path)
    
    return output_path

# 路由
@app.route('/segment', methods=['POST'])
def segment():
    if 'image' not in request.files:
        return jsonify({'error': '未上传图像文件'}), 400
    
    image_file = request.files['image']
    image_type = request.form.get('type', 'ct')
    
    # 保存上传的图像
    image_path = os.path.join('uploads', image_file.filename)
    image_file.save(image_path)
    
    try:
        # 预处理图像
        image = preprocess_image(image_path)
        
        # 分割图像
        mask = segment_image(image)
        
        # 保存分割结果
        output_path = os.path.join('outputs', 'segmentation.nii.gz')
        save_segmentation_result(mask, output_path)
        
        return jsonify({'result': output_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/outputs/<path:filename>')
def download_output(filename):
    return send_from_directory('outputs', filename)

if __name__ == '__main__':
    # 创建目录
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)