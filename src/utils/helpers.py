from pathlib import Path
from typing import Set, List
import shutil
import logging
from datetime import datetime, timedelta
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories(*dirs: str) -> None:
    """
    创建必要的目录

    Args:
        *dirs: 需要创建的目录路径

    Raises:
        OSError: 当目录创建失败时
    """
    for dir_path in dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"Directory created/verified: {dir_path}")
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {str(e)}")
            raise OSError(f"Failed to create directory {dir_path}: {str(e)}")

def get_supported_image_files(directory: Path, formats: Set[str]) -> List[Path]:
    """
    获取指定目录下支持格式的图片文件

    Args:
        directory: 目录路径
        formats: 支持的文件格式集合（如 {'.png', '.jpg'}）

    Returns:
        List[Path]: 符合格式的图片文件路径列表
    """
    try:
        image_files = [
            f for f in directory.iterdir()
            if f.is_file() and f.suffix.lower() in formats
        ]
        logger.info(f"Found {len(image_files)} supported images in {directory}")
        return image_files
    except Exception as e:
        logger.error(f"Error scanning directory {directory}: {str(e)}")
        return []

def clean_temp_files(temp_dir: Path, max_age_hours: int = 24) -> None:
    """
    清理临时文件

    Args:
        temp_dir: 临时文件目录
        max_age_hours: 文件最大保留时间（小时）
    """
    try:
        if not temp_dir.exists():
            return

        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for file_path in temp_dir.iterdir():
            if not file_path.is_file():
                continue

            file_modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_modified_time < cutoff_time:
                try:
                    file_path.unlink()
                    logger.info(f"Removed old temp file: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temp file {file_path}: {str(e)}")

    except Exception as e:
        logger.error(f"Error cleaning temp directory {temp_dir}: {str(e)}")

def get_file_size(file_path: Path) -> int:
    """
    获取文件大小（字节）

    Args:
        file_path: 文件路径

    Returns:
        int: 文件大小（字节）
    """
    try:
        return file_path.stat().st_size
    except Exception as e:
        logger.error(f"Error getting file size for {file_path}: {str(e)}")
        return 0

def ensure_unique_filename(file_path: Path) -> Path:
    """
    确保文件名唯一，如果存在则添加数字后缀

    Args:
        file_path: 原始文件路径

    Returns:
        Path: 唯一的文件路径
    """
    if not file_path.exists():
        return file_path

    counter = 1
    while True:
        new_path = file_path.parent / f"{file_path.stem}_{counter}{file_path.suffix}"
        if not new_path.exists():
            return new_path
        counter += 1

def safe_file_move(src: Path, dst: Path) -> bool:
    """
    安全地移动文件

    Args:
        src: 源文件路径
        dst: 目标文件路径

    Returns:
        bool: 是否成功
    """
    try:
        # 确保目标目录存在
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果目标文件已存在，确保唯一文件名
        if dst.exists():
            dst = ensure_unique_filename(dst)
        
        # 移动文件
        shutil.move(str(src), str(dst))
        logger.info(f"File moved successfully: {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"Error moving file {src} to {dst}: {str(e)}")
        return False

def get_directory_size(directory: Path) -> int:
    """
    获取目录总大小（字节）

    Args:
        directory: 目录路径

    Returns:
        int: 目录总大小（字节）
    """
    try:
        total_size = 0
        for dirpath, _, filenames in os.walk(str(directory)):
            for filename in filenames:
                file_path = Path(dirpath) / filename
                total_size += file_path.stat().st_size
        return total_size
    except Exception as e:
        logger.error(f"Error calculating directory size for {directory}: {str(e)}")
        return 0

def validate_directory_space(directory: Path, required_space: int) -> bool:
    """
    验证目录是否有足够的空间

    Args:
        directory: 目录路径
        required_space: 需要的空间（字节）

    Returns:
        bool: 是否有足够空间
    """
    try:
        total, used, free = shutil.disk_usage(str(directory))
        return free >= required_space
    except Exception as e:
        logger.error(f"Error checking disk space for {directory}: {str(e)}")
        return False 