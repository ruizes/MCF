import os
import zipfile
from tqdm import tqdm
from pypandownload import download_file

def download_pancreas_dataset():
    """
    Download Pancreas dataset from TCIA
    """
    # Pancreas-CT dataset download link from Baidu Netdisk
    dataset_url = "https://pan.baidu.com/s/10KcDUU8hz2MbNlQmHgx_gg"
    extract_code = "8tkq"
    
    # Create dataset directory if not exists
    dataset_dir = "d:\\MCF\\dataset\\Pancreas"
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)
    
    # Download dataset
    zip_file_path = os.path.join(dataset_dir, "Pancreas-CT.zip")
    if not os.path.exists(zip_file_path):
        print(f"Downloading Pancreas dataset to {zip_file_path}...")
        gdown.download(dataset_url, zip_file_path, quiet=False)
        print("Download completed successfully!")
    
    # Extract dataset
    print("Extracting dataset...")
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(dataset_dir)
    print("Dataset downloaded and extracted successfully.")
    
    return True

if __name__ == "__main__":
    download_pancreas_dataset()