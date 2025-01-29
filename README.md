# 背景去除工具

一个使用 rembg 库来去除图片背景的简单 Python 应用。

## 安装步骤

1. 创建虚拟环境：

```bash
python -m venv venv
source venv/bin/activate # Windows 系统使用：venv\Scripts\activate
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

## 使用方法

1. 基本使用：

```bash
python src/main.py
```

2. 指定输入输出目录和工作线程数：

```bash
python src/main.py --input-dir my_images --output-dir results --workers 8
```

3. 启用 alpha matting（可获得更好的边缘效果，但处理速度较慢）：

```bash
python src/main.py --alpha-matting
```

4. 指定支持的文件格式：

```bash
python src/main.py --formats "png,jpg,webp"
```

5. 查看帮助信息：

```bash
python src/main.py --help
```

处理后的图片将保存在 `output` 文件夹中。