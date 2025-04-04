import sys
import os

# 添加项目根目录到系统路径
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.services.email_service import EmailService

def test_send_email():
    # 创建邮件服务实例
    email_service = EmailService()
    
    # 发件人信息
    sender = "vroach@163.com"
    auth_code = "CPuVeKTmq6U2JgX3"
    
    # 收件人信息
    # receiver = "vsfrank@qq.com"
    receiver = "vswork666@gmail.com"

    # 邮件内容
    subject = "测试邮件"
    content = """
    您好！
    
    这是一封测试邮件，用于验证SMTP服务是否正常工作。
    
    祝好！
    """
    
    # 发送邮件
    result = email_service.send_email(sender, auth_code, receiver, subject, content)
    
    if result is True:
        print("邮件发送成功！")
    else:
        print(f"邮件发送失败：{result}")

if __name__ == "__main__":
    test_send_email()