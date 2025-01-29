from fastapi import APIRouter, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pathlib import Path
import asyncio
from PIL import Image
import io
import time
from datetime import datetime
import shutil

from ..core.config import (
    TEMP_DIR, SUPPORTED_FORMATS, 
    MAX_FILE_SIZE, MAX_IMAGE_SIZE
)
from ..core.image_processor import ImageProcessor
from ..utils.helpers import setup_directories
from ..utils.image_utils import compress_image
from .models import TaskStatus, TaskResponse, TaskStatusResponse

router = APIRouter()
tasks_status = {}

async def process_image_async(task: TaskStatus, input_path: str, output_path: str, alpha_matting: bool = False):
    """异步处理图片"""
    try:
        task.status = "processing"
        task.progress = 10
        
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(
            None, 
            ImageProcessor.process_image,
            input_path, 
            output_path, 
            alpha_matting
        )
        
        if success:
            task.status = "completed"
            task.progress = 100
            task.result_path = output_path
        else:
            task.status = "failed"
            task.error = "Failed to process image"
            
    except Exception as e:
        task.status = "failed"
        task.error = str(e)
        task.progress = 0

@router.post("/remove-background", response_model=TaskResponse)
async def remove_background(file: UploadFile, background_tasks: BackgroundTasks):
    """上传图片并开始处理"""
    start_time = time.time()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Received file: {file.filename}")
    
    # 验证文件格式
    if Path(file.filename).suffix.lower() not in SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail="Unsupported file format")
    
    # 读取并验证文件大小
    file_data = await file.read()
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")
    
    try:
        # 压缩图片
        image = Image.open(io.BytesIO(file_data))
        original_size = image.size
        image = compress_image(image, MAX_IMAGE_SIZE)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Image size: {original_size} -> {image.size}")
        
        # 创建新任务
        task = TaskStatus()
        tasks_status[task.id] = task
        
        # 确保目录存在
        setup_directories(TEMP_DIR)
        
        # 保存压缩后的图片
        input_path = TEMP_DIR / f"input_{task.id}.png"
        output_path = TEMP_DIR / f"output_{task.id}.png"
        
        image.save(input_path)
        
        end_time = time.time()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Preprocessing completed in {end_time - start_time:.2f} seconds")
        
        # 异步处理图片
        background_tasks.add_task(
            process_image_async,
            task,
            str(input_path),
            str(output_path),
            False
        )
        
        return TaskResponse(task_id=task.id)
        
    except Exception as e:
        end_time = time.time()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Error processing file after {end_time - start_time:.2f} seconds: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/task/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(task_id: str):
    """获取任务状态"""
    task = tasks_status.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return TaskStatusResponse(
        status=task.status,
        progress=task.progress,
        error=task.error
    )

@router.get("/result/{task_id}")
async def get_result(task_id: str):
    """获取处理结果"""
    task = tasks_status.get(task_id)
    if not task:
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Task not found",
                "task_id": task_id
            }
        )
    
    if task.status != "completed":
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Task not completed",
                "task_id": task_id,
                "status": task.status,
                "progress": task.progress
            }
        )
    
    if not task.result_path or not Path(task.result_path).exists():
        raise HTTPException(
            status_code=404,
            detail={
                "message": "Result file not found",
                "task_id": task_id
            }
        )
    
    return FileResponse(
        task.result_path,
        media_type="image/png",
        filename=f"background_removed_{task_id}.png"
    ) 