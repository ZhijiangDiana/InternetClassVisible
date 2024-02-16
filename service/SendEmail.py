import smtplib
import threading
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import SENDER_EMAIL, SENDER_PASSWORD


class EmailService:
    __instance = None
    __lock = threading.Lock()

    _sender_email = SENDER_EMAIL
    _sender_password = SENDER_PASSWORD

    _smtp_server = 'smtp.qq.com'
    _smtp_port = 587

    _subject = '给我做青年大学习！'
    _message = MIMEMultipart("related")

    def __new__(cls):
        with cls.__lock:
            if cls.__instance is None:
                cls.__instance = super().__new__(cls)
                self = cls.__instance

                cls._init(self)
                print("邮件系统启动完成")

        return cls.__instance

    def _init(self):
        # 邮件内容
        with open(r"email.html", 'r', encoding='utf-8') as f:
            body = f.read()

        # 构建邮件
        self._message['Subject'] = self._subject
        self._message['From'] = self._sender_email
        # 邮件正文部分
        content = MIMEText(body, 'html', 'utf-8')
        self._message.attach(content)
        # 图片部分
        with open(r"email.png", 'rb') as pic:
            img = MIMEImage(pic.read())
        img.add_header("Content-ID", "imageid")
        self._message.attach(img)

    # TODO 未测试
    async def send_email(self, receivers: list):
        self._message['To'] = ";".join(receivers)
        # self._message['Cc'] = ";".join(receivers)

        # 发送邮件
        try:
            with smtplib.SMTP(self._smtp_server, self._smtp_port) as server:
                server.starttls()
                server.login(self._sender_email, self._sender_password)
                server.sendmail(self._sender_email, [self._message['To']], self._message.as_string())
                server.close()
            print('邮件发送成功')
        except smtplib.SMTPException as e:
            print('邮件发送失败:', str(e))
