# 配置 Systemd 管理 FastAPI 服务
1. 创建 Systemd 服务文件
cd /etc/systemd/system/
sudo vi /etc/systemd/system/voice.service

2. 编写 Systemd 配置
```ini
[Unit]
Description=Voice Production Service
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/gits/human-ai
Environment="APP_ENV=prod"
Environment="GOOGLE_APPLICATION_CREDENTIALS=/home/ec2-user/.my/human-ai-454609-bf84b910d612.json"

# 通过 venv 的 Python 解释器启动服务
ExecStart=/home/ec2-user/gits/human-ai/.venv/bin/uvicorn src.main_web:app --port 8080 --workers 2

Restart=always
RestartSec=3

# 日志配置（可选）
StandardOutput=append:/var/log/fastapi/voice.log
StandardError=append:/var/log/fastapi/voice-error.log

[Install]
WantedBy=multi-user.target
```

3. 关键配置说明
User 和 Group:
建议使用非 root 用户（如 ec2-user 或新建用户 fastapi），确保权限最小化。

WorkingDirectory:
必须设置为项目根目录，否则可能无法正确加载模块（如 src.main_web）。

Environment:
直接在服务文件中定义环境变量（如 APP_ENV=prod），避免手动导出。

ExecStart:
通过虚拟环境的绝对路径调用 uvicorn（即 /path/to/venv/bin/uvicorn），无需手动激活 venv。

日志路径:
如果使用 file:/var/log/fastapi.log，需确保用户有写入权限：

```shell
sudo mkdir fastapi
sudo chown ec2-user:ec2-user fastapi
sudo touch /var/log/fastapi/fastapi.log /var/log/fastapi/fastapi-error.log
sudo chown ec2-user:ec2-user /var/log/fastapi/fastapi*.log
```

4. 启动服务并设置开机自启
```shell
# 重新加载 Systemd 配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start voice

# 设置开机自启
sudo systemctl enable voice
```

5. 常用管理命令
```shell
# 查看服务状态：
sudo systemctl status voice
# 查看实时日志：
journalctl -u voice -f
# 重启服务：
sudo systemctl restart voice
# 停止服务：
sudo systemctl stop voice
```

6. 验证服务是否正常运行
```shell
# 检查服务是否监听端口 8080：
ss -tuln | grep 8080
# 测试 API 接口：
curl http://localhost:8080/
```


7. 安全优化建议
专用用户权限（可选）：
```shell
# 新建用户和组
sudo useradd -M -s /bin/false fastapi
# 将项目目录所有权赋予该用户
sudo chown -R fastapi:fastapi /home/ec2-user/gits/human-ai
# 修改服务文件中的 User 和 Group
User=fastapi
Group=fastapi
```


日志轮转（使用 logrotate）:
创建 /etc/logrotate.d/fastapi：
```shell
/var/log/fastapi.log
/var/log/fastapi-error.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 fastapi fastapi
}
```

8. 故障排查
权限问题：
如果出现 Permission denied，检查用户对项目目录、日志文件和 venv 的权限。

模块加载失败：
确保 WorkingDirectory 正确，且 src.main_web:app 路径有效。

环境变量未生效：
在服务文件中添加多变量：
```ini
Environment="APP_ENV=prod"
Environment="DATABASE_URL=postgresql://user:pass@host/db"
```

9. SSL证书（Let's Encrypt）

sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com


upstream fastapi_cluster {
    server unix:/opt/fastapi/app1.sock;
    server unix:/opt/fastapi/app2.sock;
    keepalive 32;
}


10. 创建轮转配置
新建配置文件 /etc/logrotate.d/voice
sudo vi /etc/logrotate.d/voice
/var/log/voice/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 ec2-user ec2-user
    sharedscripts
    postrotate
        systemctl restart voice
    endscript
}

/var/log/your-service/*.log {
    daily               # 按天轮转
    missingok           # 日志不存在时不报错
    rotate 30          # 保留 30 个旧日志
    compress            # 压缩旧日志（gzip）
    delaycompress       # 延迟压缩，保留最近一次未压缩的日志
    notifempty          # 空日志不轮转
    create 0644 ec2-user ec2-user  # 新日志文件权限和所有者
    sharedscripts       # 执行全局脚本
    postrotate
        systemctl restart your-service.service  # 轮转后重启服务（可选）
    endscript
}

logrotate -vf /etc/logrotate.d/voice









