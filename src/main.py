import uvicorn
from fastapi import FastAPI
from .api.routes import router
from .cli.commands import app as cli_app

# 创建 FastAPI 应用
app = FastAPI(title="Background Removal API")
app.include_router(router)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        # 如果有命令行参数，运行 CLI 应用
        cli_app()
    else:
        # 否则运行 API 服务器
        uvicorn.run(app, host="0.0.0.0", port=8000)