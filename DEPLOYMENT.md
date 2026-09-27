# 雪漫画 CineGacha 部署指南

## 📋 目录

1. [环境要求](#环境要求)
2. [快速部署](#快速部署)
3. [配置说明](#配置说明)
4. [启动服务](#启动服务)
5. [验证部署](#验证部署)
6. [生产环境部署](#生产环境部署)
7. [常见问题](#常见问题)

---

## 环境要求

### 必需依赖

- **Python**: 3.10+ (推荐 3.11)
- **Conda**: 用于环境管理
- **Git**: 版本控制

### 系统要求

- **操作系统**: Windows 10/11, Linux, macOS
- **内存**: 最少 2GB，推荐 4GB+
- **磁盘**: 最少 1GB 可用空间

---

## 快速部署

### 1. 激活 Conda 环境

```bash
conda activate cinegacha
```

### 2. 安装依赖

依赖已在 conda 环境中安装，验证安装：

```bash
# 检查 Python 版本
python --version  # 应显示 Python 3.10.x 或更高

# 检查 Flask
python -c "import flask; print(f'Flask {flask.__version__}')"

# 检查 SQLAlchemy
python -c "import sqlalchemy; print(f'SQLAlchemy {sqlalchemy.__version__}')"
```

### 3. 初始化数据库

```bash
# 数据库会在首次启动时自动创建
# 如需手动初始化：
python -c "from cinegacha import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('✅ 数据库初始化成功')"
```

### 4. 启动开发服务器

```bash
# 方式1：使用 Flask 命令（推荐）
flask run

# 方式2：使用 Python 模块
python -m flask run

# 方式3：指定主机和端口
flask run --host=0.0.0.0 --port=5000 --debug
```

服务启动后，访问：http://localhost:5000

---

## 配置说明

### 配置文件位置

配置文件位于 `cinegacha/config.py`

### 环境变量（可选）

如需覆盖默认配置，可设置环境变量：

```bash
# Windows (PowerShell)
$env:FLASK_APP="cinegacha"
$env:FLASK_ENV="development"
$env:FERNET_KEY="your-secret-key-here"

# Windows (CMD)
set FLASK_APP=cinegacha
set FLASK_ENV=development
set FERNET_KEY=your-secret-key-here

# Linux/macOS
export FLASK_APP=cinegacha
export FLASK_ENV=development
export FERNET_KEY=your-secret-key-here
```

### 数据库路径

默认数据库文件：`data/cinegacha.db`

如需修改，编辑 `cinegacha/config.py`：

```python
class DevelopmentConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your-custom-path.db'
```

---

## 启动服务

### 开发模式（推荐用于开发）

```bash
# 启用调试模式
flask run --debug

# 或设置环境变量后启动
export FLASK_DEBUG=1
flask run
```

开发模式特性：
- ✅ 代码修改自动重载
- ✅ 详细错误信息
- ✅ 交互式调试器

### 生产模式

```bash
# 使用 gunicorn（Linux/macOS）
gunicorn -w 4 -b 0.0.0.0:5000 cinegacha:create_app()

# 使用 waitress（Windows 推荐）
waitress-serve --host=0.0.0.0 --port=5000 cinegacha:create_app()
```

---

## 验证部署

### 1. 访问首页

打开浏览器访问：http://localhost:5000

应看到"雪漫画 CineGacha"首页。

### 2. 运行测试套件

```bash
# 运行所有测试
pytest

# 运行测试并显示覆盖率
pytest --cov=cinegacha --cov-report=term-missing

# 运行特定测试
pytest tests/test_models/ -v
```

期望结果：
```
============================= 86 passed in 2.11s ==============================
```

### 3. 测试 API 端点

```bash
# 创建小说
curl -X POST http://localhost:5000/api/novels \
  -H "Content-Type: application/json" \
  -d '{"name":"测试小说","content":"这是测试内容"}'

# 列表小说
curl http://localhost:5000/api/novels

# 清洗小说（替换 {id} 为实际ID）
curl -X POST http://localhost:5000/api/novels/{id}/clean
```

### 4. 检查数据库

```bash
# 使用 SQLite 命令行工具
sqlite3 data/cinegacha.db

# 查看表结构
.tables

# 查询数据
SELECT * FROM novels;
SELECT * FROM roles;
SELECT * FROM scripts_list;

# 退出
.quit
```

---

## 生产环境部署

### 1. 使用 Gunicorn（Linux/macOS）

#### 安装 Gunicorn

```bash
pip install gunicorn
```

#### 创建 systemd 服务文件

```bash
sudo nano /etc/systemd/system/cinegacha.service
```

添加内容：

```ini
[Unit]
Description=CineGacha Flask Application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/cinegacha
Environment="PATH=/path/to/conda/envs/cinegacha/bin"
Environment="FLASK_APP=cinegacha"
Environment="FLASK_ENV=production"
ExecStart=/path/to/conda/envs/cinegacha/bin/gunicorn -w 4 -b 127.0.0.1:5000 cinegacha:create_app()

[Install]
WantedBy=multi-user.target
```

#### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable cinegacha
sudo systemctl start cinegacha
sudo systemctl status cinegacha
```

### 2. 使用 Nginx 反向代理

#### 安装 Nginx

```bash
sudo apt update
sudo apt install nginx
```

#### 配置 Nginx

```bash
sudo nano /etc/nginx/sites-available/cinegacha
```

添加内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/cinegacha/cinegacha/static;
        expires 30d;
    }
}
```

#### 启用配置

```bash
sudo ln -s /etc/nginx/sites-available/cinegacha /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. 使用 Waitress（Windows）

#### 安装 Waitress

```bash
pip install waitress
```

#### 创建启动脚本

创建 `start_production.py`：

```python
from waitress import serve
from cinegacha import create_app

app = create_app('production')
print("🚀 CineGacha 生产服务器启动...")
print("📍 访问地址: http://0.0.0.0:5000")
serve(app, host='0.0.0.0', port=5000, threads=4)
```

#### 运行

```bash
python start_production.py
```

### 4. Docker 部署（可选）

#### 创建 Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 复制应用
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "cinegacha:create_app()"]
```

#### 构建和运行

```bash
docker build -t cinegacha .
docker run -d -p 5000:5000 --name cinegacha cinegacha
```

---

## 常见问题

### Q1: 端口被占用

**问题**: `Address already in use`

**解决方案**:

```bash
# 查看占用端口的进程（Linux/macOS）
lsof -i :5000

# 终止进程
kill -9 <PID>

# 或使用其他端口
flask run --port=5001
```

### Q2: 数据库锁定

**问题**: `database is locked`

**解决方案**:

```bash
# 删除数据库并重新创建
rm data/cinegacha.db
python -c "from cinegacha import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Q3: 模块导入错误

**问题**: `ModuleNotFoundError: No module named 'cinegacha'`

**解决方案**:

```bash
# 确保在项目根目录
cd /path/to/cinegacha

# 设置 PYTHONPATH（Linux/macOS）
export PYTHONPATH=/path/to/cinegacha

# 或设置环境变量（Windows CMD）
set PYTHONPATH=C:\path\to\cinegacha

# 或使用 Python 模块方式运行
python -m flask run
```

### Q4: 测试失败

**问题**: 测试用例失败

**解决方案**:

```bash
# 清理缓存
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -name "*.pyc" -delete

# 重新运行测试
pytest -v --tb=short

# 查看详细信息
pytest -v --tb=long
```

### Q5: 中文乱码

**问题**: 网页显示乱码

**解决方案**:

确保所有 HTML 模板包含：

```html
<meta charset="UTF-8">
```

Python 文件顶部添加：

```python
# -*- coding: utf-8 -*-
```

---

## 备份与恢复

### 备份数据库

```bash
# 复制数据库文件
cp data/cinegacha.db data/cinegacha_backup_$(date +%Y%m%d).db

# 或使用 SQLite 导出
sqlite3 data/cinegacha.db .dump > backup.sql
```

### 恢复数据库

```bash
# 从备份文件恢复
cp data/cinegacha_backup_20260125.db data/cinegacha.db

# 或从 SQL 文件恢复
sqlite3 data/cinegacha.db < backup.sql
```

---

## 性能优化建议

### 1. 数据库优化

```bash
# 分析数据库
sqlite3 data/cinegacha.db "ANALYZE;"

# 重建索引
sqlite3 data/cinegacha.db "REINDEX;"
```

### 2. 使用生产数据库

对于生产环境，建议替换 SQLite 为 PostgreSQL：

```python
class ProductionConfig:
    SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/cinegacha'
```

### 3. 启用缓存

安装 Flask-Caching：

```bash
pip install Flask-Caching
```

配置缓存：

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
```

---

## 监控与日志

### 查看日志

```bash
# 开发模式日志直接输出到终端

# 生产环境日志（systemd）
sudo journalctl -u cinegacha -f

# 查看最近100行
sudo journalctl -u cinegacha -n 100
```

### 性能监控

安装 Flask-Profiler：

```bash
pip install flask_profiler
```

配置：

```python
app.config['flask_profiler'] = {
    'enabled': True,
    'storage': {
        'engine': 'sqlite'
    }
}
```

访问：http://localhost:5000/flask-profiler/

---

## 安全建议

### 1. 使用 HTTPS

生产环境必须使用 HTTPS，配置 SSL 证书：

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # ... 其他配置
}
```

### 2. 更改密钥

生成新的 FERNET_KEY：

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

### 3. 限制访问

配置防火墙：

```bash
# 仅允许本地访问开发服务器
flask run --host=127.0.0.1

# 生产环境使用防火墙规则
sudo ufw allow from your-ip to any port 5000
```

---

## 联系与支持

- **文档**: 查看 `docs/` 目录
- **测试**: 运行 `pytest` 验证部署
- **问题**: 检查日志文件

---

**部署完成！开始使用雪漫画 CineGacha 🎨**
