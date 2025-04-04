import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

class EmailService:
    def __init__(self, smtp_server="smtp.163.com", port=25):
        self.smtp_server = smtp_server
        self.port = port
        
    def send_email(self, sender, auth_code, receiver, subject, content, content_type="plain"):
        """
        发送邮件
        
        参数:
            sender: 发件人邮箱
            auth_code: 邮箱授权码
            receiver: 收件人邮箱，可以是字符串或列表
            subject: 邮件主题
            content: 邮件内容
            content_type: 内容类型，'plain'或'html'
        
        返回:
            成功返回True，失败返回错误信息
        """
        try:
            # 创建邮件对象
            message = MIMEMultipart()
            # 设置发件人
            message['From'] = sender
            # 设置收件人
            if isinstance(receiver, list):
                message['To'] = ','.join(receiver)
            else:
                message['To'] = receiver
            # 设置邮件主题
            message['Subject'] = Header(subject, 'utf-8')
            
            # 添加邮件正文
            message.attach(MIMEText(content, content_type, 'utf-8'))
            
            # 连接SMTP服务器
            smtp_obj = smtplib.SMTP(self.smtp_server, self.port)
            # 显示调试信息
            smtp_obj.set_debuglevel(1)
            # 登录邮箱
            smtp_obj.login(sender, auth_code)
            # 发送邮件
            if isinstance(receiver, list):
                smtp_obj.sendmail(sender, receiver, message.as_string())
            else:
                smtp_obj.sendmail(sender, [receiver], message.as_string())
            # 关闭连接
            smtp_obj.quit()
            
            return True
        except Exception as e:
            return str(e)