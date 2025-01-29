from pathlib import Path
from PIL import Image
import shutil

def setup_directories(directory: Path):
    """创建目录"""
    directory.mkdir(exist_ok=True)

def save_uploaded_file(file_content, file_path: Path):
    """保存上传的文件"""
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file_content, buffer)

def save_image(image: Image.Image, output_path: Path):
    """根据输出文件格式保存图片"""
    if output_path.suffix.lower() in ['.jpg', '.jpeg']:
        bg = Image.new('RGB', image.size, 'white')
        if image.mode == 'RGBA':
            bg.paste(image, mask=image.split()[3])
        else:
            bg.paste(image)
        bg.save(output_path, quality=95)
    else:
        image.save(output_path) 