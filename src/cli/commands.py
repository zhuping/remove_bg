import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.table import Table
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import time
from datetime import datetime

from ..core.image_processor import ImageProcessor
from ..utils.helpers import setup_directories, get_supported_image_files
from ..core.config import SUPPORTED_FORMATS

app = typer.Typer(help="Background removal tool using rembg")
console = Console()

def process_images_parallel(
    input_paths: list[Path],
    output_dir: Path,
    max_workers: int,
    alpha_matting: bool,
    progress: Progress
) -> tuple[int, int]:
    """并行处理多个图片，返回成功和失败的数量"""
    successful = 0
    failed = 0
    
    # 创建进度条任务
    task = progress.add_task(
        "[cyan]Removing backgrounds...", 
        total=len(input_paths)
    )
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for input_path in input_paths:
            # 确定输出文件格式
            if input_path.suffix.lower() in ['.jpg', '.jpeg']:
                output_path = output_dir / f"no_bg_{input_path.stem}.png"
            else:
                output_path = output_dir / f"no_bg_{input_path.name}"
            
            future = executor.submit(
                ImageProcessor.process_image,
                str(input_path),
                str(output_path),
                alpha_matting
            )
            futures.append((future, input_path))
        
        # 处理结果
        for future, input_path in futures:
            try:
                result = future.result()
                if result:
                    successful += 1
                    console.print(f"[green]✓[/green] Processed: {input_path.name}")
                else:
                    failed += 1
                    console.print(f"[red]✗[/red] Failed: {input_path.name}")
            except Exception as e:
                failed += 1
                console.print(f"[red]✗[/red] Error processing {input_path.name}: {str(e)}")
            finally:
                progress.update(task, advance=1)
    
    return successful, failed

def display_summary(duration: float, successful: int, failed: int):
    """显示处理摘要"""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    
    table.add_row("Processing Time", f"{duration:.2f} seconds")
    table.add_row("Successfully Processed", f"[green]{successful}[/green]")
    table.add_row("Failed", f"[red]{failed}[/red]")
    table.add_row("Total Images", str(successful + failed))
    table.add_row("Success Rate", f"{(successful/(successful+failed)*100 if successful+failed > 0 else 0):.1f}%")
    
    console.print("\n", Panel(table, title="Processing Summary", border_style="blue"))

@app.command()
def remove_background(
    input_dir: str = typer.Option(
        "input",
        "--input-dir",
        "-i",
        help="Input directory containing images"
    ),
    output_dir: str = typer.Option(
        "output",
        "--output-dir",
        "-o",
        help="Output directory for processed images"
    ),
    workers: int = typer.Option(
        4,
        "--workers",
        "-w",
        help="Number of worker threads"
    ),
    alpha_matting: bool = typer.Option(
        False,
        "--alpha-matting",
        "-a",
        help="Enable alpha matting for better edges"
    ),
    formats: str = typer.Option(
        "png,jpg,jpeg,webp",
        "--formats",
        "-f",
        help="Comma-separated list of supported formats"
    )
):
    """移除图片背景的命令行工具"""
    start_time = time.time()
    console.print(f"\n[bold blue]Background Removal Tool[/bold blue]")
    console.print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    try:
        # 设置目录
        setup_directories(input_dir, output_dir)
        
        # 解析支持的格式
        supported_formats = {f".{fmt.strip()}" for fmt in formats.lower().split(",")}
        if not supported_formats.issubset(SUPPORTED_FORMATS):
            unsupported = supported_formats - SUPPORTED_FORMATS
            console.print(f"[yellow]Warning: Unsupported formats: {', '.join(unsupported)}[/yellow]")
            supported_formats = supported_formats.intersection(SUPPORTED_FORMATS)
        
        # 获取所有图片文件
        input_dir_path = Path(input_dir)
        output_dir_path = Path(output_dir)
        image_files = get_supported_image_files(input_dir_path, supported_formats)
        
        if not image_files:
            console.print(f"[yellow]No supported images found in {input_dir}[/yellow]")
            return
        
        # 显示处理信息
        console.print(f"[green]Found {len(image_files)} images to process[/green]")
        console.print(f"[blue]Using {workers} worker threads[/blue]\n")
        
        # 创建进度显示
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console
        ) as progress:
            successful, failed = process_images_parallel(
                image_files,
                output_dir_path,
                workers,
                alpha_matting,
                progress
            )
        
        # 显示处理时间和结果统计
        end_time = time.time()
        display_summary(end_time - start_time, successful, failed)

    except Exception as e:
        console.print(f"\n[red]Error: {str(e)}[/red]")
        raise typer.Exit(code=1)

@app.command()
def version():
    """显示版本信息"""
    console.print("[bold blue]Background Removal Tool[/bold blue] v1.0.0")

if __name__ == "__main__":
    app() 