from fastapi.templating import Jinja2Templates
from pathlib import Path

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# print("BASE_DIR"+BASE_DIR)
print("BASE_DIR: ", BASE_DIR)

# 创建模板实例
templates = Jinja2Templates(
    directory=str(BASE_DIR / "src" / "templates"),
    # 可选：添加自定义过滤器或全局变量
    autoescape=True,
    auto_reload=True
)

# 添加全局变量
templates.env.globals.update({
    "site_name": "Web Cloud",
    "static_url": "/static"
})
