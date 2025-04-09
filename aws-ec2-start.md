# 亚马逊云部署
## python 安装
ssh -i "C:\my\ssh\aws-voice.pem" ec2-user@ec2-43-199-194-87.ap-east-1.compute.amazonaws.com

```shell
sudo dnf -y install python3.12
方法 1：创建软链接（推荐）

# 备份原始 python 命令（如果存在）
sudo mv /usr/bin/python /usr/bin/python.backup 2>/dev/null

# 创建新的软链接
sudo ln -sf /usr/bin/python3.12 /usr/bin/python

# 验证
python --version


方法 2：使用 alternatives 系统
# 添加 Python 3.12 到 alternatives
sudo alternatives --install /usr/bin/python python /usr/bin/python3.12 1

# 设置默认版本
sudo alternatives --set python /usr/bin/python3.12

# 验证
python --version


方法 3：修改用户环境变量（临时生效）
echo 'alias python="python3.12"' >> ~/.bashrc
source ~/.bashrc

# 验证
python --version


```
## nginx 安装
### 直接安装
dnf search nginx
sudo dnf install nginx

### 安装最新版本
sudo yum install yum-utils

sudo vi /etc/yum.repos.d/nginx.repo
[nginx-stable]
name=nginx stable repo
baseurl=http://nginx.org/packages/amzn/2023/$basearch/
gpgcheck=1
enabled=1
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
priority=9

[nginx-mainline]
name=nginx mainline repo
baseurl=http://nginx.org/packages/mainline/amzn/2023/$basearch/
gpgcheck=1
enabled=0
gpgkey=https://nginx.org/keys/nginx_signing.key
module_hotfixes=true
priority=9

By default, the repository for stable nginx packages is used. If you would like to use mainline nginx packages, run the following command:

sudo yum-config-manager --enable nginx-mainline
To install nginx, run the following command:

sudo yum install nginx

sudo systemctl enable nginx
sudo systemctl start nginx

nginx -s quit
nginx -s reload
nginx -s stop
nginx -s reopen

systemctl stop firewalld
############
开机启动：
systemctl enable nginx
systemctl disable ssh.service
systemctl list-units --type=service |grep -i nginx


curl https://get.acme.sh | sh -s email=vsfrank@qq.com
sudo yum install socat 
sudo yum install cronie 
sudo systemctl enable crond.service
sudo systemctl list-units --type=service |grep -i cronie

sudo systemctl start crond.service

sudo nginx -s reload

## 部署
APP_ENV=prod uvicorn src.main_web:app --port 8080 --workers 2




