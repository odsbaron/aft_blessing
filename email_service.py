# -*- coding: utf-8 -*-
"""
邮件服务模块
处理邮件发送相关功能
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from config import Config
from rate_limiter import get_rate_limiter, RateLimitExceeded


# 速率限制器实例
_rate_limiter = get_rate_limiter()


# HTML 邮件模板
EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: 'Helvetica Neue', 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f5f5f5; margin: 0; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 32px; font-weight: bold; }}
        .content {{ padding: 40px 30px; }}
        .cake {{ font-size: 72px; text-align: center; margin: 20px 0; }}
        .greeting {{ text-align: center; font-size: 20px; color: #667eea; margin-bottom: 20px; font-weight: bold; }}
        .message {{ font-size: 16px; line-height: 1.8; color: #555; text-align: center; padding: 0 10px; }}
        .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #888; font-size: 12px; border-top: 1px solid #eee; }}
        .footer p {{ margin: 5px 0; }}
        .decoration {{ text-align: center; color: #ddd; font-size: 24px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎂 生日快乐！</h1>
        </div>
        <div class="content">
            <div class="cake">🎂</div>
            <div class="greeting">亲爱的 {user_name}</div>
            <div class="decoration">✨ ✨ ✨</div>
            <p class="message">{wish_content}</p>
            <div class="decoration">✨ ✨ ✨</div>
        </div>
        <div class="footer">
            <p>—— 这是来自 {from_name} 的生日祝福</p>
            <p>这是一封自动发送的邮件，请勿直接回复</p>
        </div>
    </div>
</body>
</html>
"""


def build_html_email(user_name, wish_content):
    """
    构建 HTML 邮件内容

    Args:
        user_name: 用户姓名
        wish_content: 祝福语内容

    Returns:
        str: HTML 格式的邮件内容
    """
    return EMAIL_TEMPLATE.format(
        user_name=user_name,
        wish_content=wish_content,
        from_name=Config.MAIL_FROM_NAME
    )


def build_text_email(user_name, wish_content):
    """
    构建纯文本邮件内容（备用）

    Args:
        user_name: 用户姓名
        wish_content: 祝福语内容

    Returns:
        str: 纯文本格式的邮件内容
    """
    return f"""亲爱的 {user_name}：

{wish_content}

✨ ✨ ✨

—— 来自 {Config.MAIL_FROM_NAME} 的生日祝福

这是一封自动发送的邮件，请勿直接回复
"""


def send_birthday_email(to_email, user_name, wish_content, check_rate_limit=True):
    """
    发送生日邮件

    Args:
        to_email: 收件人邮箱
        user_name: 收件人姓名
        wish_content: 祝福语内容
        check_rate_limit: 是否检查速率限制（默认True）

    Returns:
        tuple: (是否成功, 错误信息)
    """
    # 速率限制检查
    if check_rate_limit:
        can_send, reason = _rate_limiter.check_limit(to_email)
        if not can_send:
            error = f"速率限制: {reason}"
            print(f"⏱️ [发送受限] {to_email} - {reason}")
            return False, error

    try:
        # 创建多部分邮件
        msg = MIMEMultipart('alternative')

        # 设置邮件头
        msg['From'] = formataddr(
            (Header(Config.MAIL_FROM_NAME, 'utf-8').encode(), Config.MAIL_USER)
        )
        msg['To'] = formataddr(
            (Header(user_name, 'utf-8').encode(), to_email)
        )
        msg['Subject'] = Header(f"🎂 {user_name}，生日快乐！", 'utf-8')

        # 纯文本版本（备用）
        text_content = build_text_email(user_name, wish_content)
        msg.attach(MIMEText(text_content, 'plain', 'utf-8'))

        # HTML 版本（首选）
        html_content = build_html_email(user_name, wish_content)
        msg.attach(MIMEText(html_content, 'html', 'utf-8'))

        # 连接 SMTP 服务器并发送
        server = smtplib.SMTP_SSL(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.login(Config.MAIL_USER, Config.MAIL_AUTH_CODE)
        server.sendmail(Config.MAIL_USER, [to_email], msg.as_string())
        server.quit()

        # 记录成功发送
        if check_rate_limit:
            _rate_limiter.record_sent(to_email)

        print(f"✅ [发送成功] {user_name} -> {to_email}")
        return True, None

    except smtplib.SMTPAuthenticationError as e:
        error = f"认证失败：请检查邮箱授权码是否正确"
        print(f"❌ [发送失败] {to_email} - {error}")
        return False, error

    except smtplib.SMTPException as e:
        error = f"SMTP 错误: {str(e)}"
        print(f"❌ [发送失败] {to_email} - {error}")
        return False, error

    except Exception as e:
        error = f"未知错误: {str(e)}"
        print(f"❌ [发送失败] {to_email} - {error}")
        return False, error


def send_test_email(to_email):
    """
    发送测试邮件

    Args:
        to_email: 收件人邮箱

    Returns:
        bool: 是否发送成功
    """
    wish_content = "这是一封测试邮件。您的生日祝福系统已配置成功！"
    success, error = send_birthday_email(to_email, "测试用户", wish_content)
    return success


# 批量发送（带速率限制）
def send_batch_emails(email_list):
    """
    批量发送邮件

    Args:
        email_list: 邮件列表，格式为 [(email, name, wish), ...]

    Returns:
        dict: 统计信息 {success: 成功数, failed: 失败数, errors: 错误列表}
    """
    result = {
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for email, name, wish in email_list:
        success, error = send_birthday_email(email, name, wish)
        if success:
            result['success'] += 1
        else:
            result['failed'] += 1
            result['errors'].append({'email': email, 'error': error})

    return result


# 测试代码
if __name__ == "__main__":
    # 测试配置验证
    errors = Config.validate()
    if errors:
        print("❌ 配置错误：")
        for error in errors:
            print(f"  - {error}")
        print("\n请先创建 .env 文件并配置正确的邮箱信息")
    else:
        print("✅ 配置正常")
        print(f"邮件服务器: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
        print(f"发件人: {Config.MAIL_USER}")

        # 可选：发送测试邮件
        print("\n如需发送测试邮件，请运行：")
        print("  python -c \"from email_service import send_test_email; send_test_email('your_email@example.com')\"")
