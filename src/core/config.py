from pathlib import Path

# API 配置
API_HOST = "0.0.0.0"
API_PORT = 8000

# 文件配置
TEMP_DIR = Path("temp")
SUPPORTED_FORMATS = {".png", ".jpg", ".jpeg", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# 图片处理配置
MAX_IMAGE_SIZE = 1920  # 最大图片尺寸
JPEG_QUALITY = 85     # JPEG压缩质量

# 处理配置
DEFAULT_WORKERS = 4
DEFAULT_ALPHA_MATTING = False 