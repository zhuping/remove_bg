from pathlib import Path
from PIL import Image
from rembg import remove
from typing import Optional, Tuple
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 常量配置
MAX_IMAGE_SIZE = 4000  # 最大图片尺寸
QUALITY_JPEG = 95     # JPEG保存质量
QUALITY_PNG = 95      # PNG保存质量
DEFAULT_BG_COLOR = 'white'  # 默认背景色

class ImageProcessor:
    """图像处理类，提供图像背景移除和保存功能"""

    @staticmethod
    def compress_image(image: Image.Image, max_size: int = MAX_IMAGE_SIZE) -> Image.Image:
        """
        压缩图片到指定最大尺寸

        Args:
            image: PIL Image对象
            max_size: 最大允许的尺寸

        Returns:
            Image.Image: 压缩后的图片
        """
        if max(image.size) <= max_size:
            return image

        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        return image.resize(new_size, Image.Resampling.LANCZOS)

    @staticmethod
    def save_image(
        image: Image.Image,
        output_path: Path,
        bg_color: str = DEFAULT_BG_COLOR
    ) -> None:
        """
        根据输出文件格式保存图片

        Args:
            image: PIL Image对象
            output_path: 输出文件路径
            bg_color: 背景颜色（用于JPG格式）

        Raises:
            ValueError: 当输出路径无效或图片保存失败时
        """
        try:
            start_time = datetime.now()
            logger.info(f"Saving image to {output_path}")

            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 根据文件格式处理
            if output_path.suffix.lower() in ['.jpg', '.jpeg']:
                # 创建背景
                bg = Image.new('RGB', image.size, bg_color)
                
                # 如果图片有透明通道，需要考虑透明度进行混合
                if image.mode == 'RGBA':
                    bg.paste(image, mask=image.split()[3])
                else:
                    bg.paste(image)
                
                # 保存为JPEG
                bg.save(
                    output_path,
                    'JPEG',
                    quality=QUALITY_JPEG,
                    optimize=True
                )
            else:
                # 保存为PNG或其他格式
                image.save(
                    output_path,
                    'PNG',
                    optimize=True,
                    quality=QUALITY_PNG
                )

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Image saved successfully in {duration:.2f} seconds")

        except Exception as e:
            logger.error(f"Error saving image to {output_path}: {str(e)}")
            raise ValueError(f"Failed to save image: {str(e)}")

    @staticmethod
    def process_image(
        input_path: str,
        output_path: str,
        alpha_matting: bool = False,
        alpha_matting_foreground_threshold: int = 240,
        alpha_matting_background_threshold: int = 10,
        alpha_matting_erode_size: int = 10
    ) -> bool:
        """
        处理单个图片，移除背景

        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径
            alpha_matting: 是否使用alpha matting
            alpha_matting_foreground_threshold: alpha matting前景阈值
            alpha_matting_background_threshold: alpha matting背景阈值
            alpha_matting_erode_size: alpha matting腐蚀大小

        Returns:
            bool: 处理是否成功
        """
        try:
            start_time = datetime.now()
            logger.info(f"Processing image: {input_path}")

            # 打开并验证图片
            input_image = Image.open(input_path)
            if not input_image:
                raise ValueError("Failed to open input image")

            # 压缩大图片
            original_size = input_image.size
            if max(original_size) > MAX_IMAGE_SIZE:
                input_image = ImageProcessor.compress_image(input_image, MAX_IMAGE_SIZE)
                logger.info(f"Image resized from {original_size} to {input_image.size}")

            # 移除背景
            output_image = remove(
                input_image,
                alpha_matting=alpha_matting,
                alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
                alpha_matting_background_threshold=alpha_matting_background_threshold,
                alpha_matting_erode_size=alpha_matting_erode_size
            )

            # 保存结果
            ImageProcessor.save_image(output_image, Path(output_path))

            duration = (datetime.now() - start_time).total_seconds()
            logger.info(f"Image processed successfully in {duration:.2f} seconds")
            
            return True

        except Exception as e:
            logger.error(f"Error processing image {input_path}: {str(e)}")
            return False

    @staticmethod
    def get_image_info(image_path: Path) -> Optional[dict]:
        """
        获取图片信息

        Args:
            image_path: 图片路径

        Returns:
            dict: 包含图片信息的字典，如果失败则返回None
        """
        try:
            with Image.open(image_path) as img:
                return {
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'path': str(image_path),
                    'filename': image_path.name
                }
        except Exception as e:
            logger.error(f"Error getting image info for {image_path}: {str(e)}")
            return None

    @staticmethod
    def validate_image(
        image_path: Path,
        max_size: int = MAX_IMAGE_SIZE
    ) -> Tuple[bool, Optional[str]]:
        """
        验证图片是否有效且符合大小限制

        Args:
            image_path: 图片路径
            max_size: 最大允许的图片尺寸

        Returns:
            Tuple[bool, Optional[str]]: (是否有效, 错误信息)
        """
        try:
            with Image.open(image_path) as img:
                if max(img.size) > max_size:
                    return False, f"Image too large (max size: {max_size}px)"
                return True, None
        except Exception as e:
            return False, f"Invalid image: {str(e)}"