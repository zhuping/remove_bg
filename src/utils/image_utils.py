from PIL import Image
import io
from concurrent.futures import ThreadPoolExecutor
import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

def compress_image(image: Image.Image, max_size: int) -> Image.Image:
    """压缩图片尺寸"""
    if max(image.size) > max_size:
        ratio = max_size / max(image.size)
        new_size = tuple(int(dim * ratio) for dim in image.size)
        image = image.resize(new_size, Image.Resampling.LANCZOS)
    return image

def get_image_data(image: Image.Image) -> bytes:
    """获取图片的二进制数据"""
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()

class TaskQueue:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.tasks: Dict[str, Any] = {}

    async def add_task(self, task_id: str, func, *args, **kwargs):
        """添加任务到队列"""
        try:
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(
                self.executor,
                func,
                *args,
                **kwargs
            )
            self.tasks[task_id] = future
            return future
        except Exception as e:
            logger.error(f"Error adding task {task_id}: {str(e)}")
            raise

    async def get_task_result(self, task_id: str):
        """获取任务结果"""
        future = self.tasks.get(task_id)
        if not future:
            return None
        try:
            if future.done():
                return await future
            return None
        except Exception as e:
            logger.error(f"Error getting task result {task_id}: {str(e)}")
            return None

task_queue = TaskQueue() 