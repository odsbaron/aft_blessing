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


# HTML 邮件模板 - 现代设计风格
EMAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif; line-height: 1.7; color: #1a1a1a; background: #f0f4f8; padding: 20px; }}
        .container {{ max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 60px rgba(0,0,0,0.1), 0 8px 20px rgba(0,0,0,0.06); }}
        .top-gradient {{ height: 180px; background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); position: relative; overflow: hidden; }}
        .top-pattern {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; opacity: 0.1; background-image: radial-gradient(circle at 20% 50%, white 1px, transparent 1px); background-size: 20px 20px; }}
        .floating-icon {{ position: absolute; font-size: 24px; opacity: 0.2; }}
        .icon-1 {{ top: 20px; left: 10%; }} .icon-2 {{ top: 40px; right: 15%; }} .icon-3 {{ top: 80px; left: 20%; }} .icon-4 {{ bottom: 30px; right: 10%; }} .icon-5 {{ top: 120px; left: 40%; }}
        .main-wrapper {{ padding: 0 0 32px; margin-top: -60px; position: relative; z-index: 10; }}
        .year-badge {{ text-align: center; margin-bottom: 20px; }}
        .year-badge span {{ display: inline-block; padding: 10px 28px; background: white; color: #667eea; font-size: 12px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; border-radius: 30px; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3); }}
        .title-section {{ text-align: center; padding: 0 32px 24px; }}
        .title-section h2 {{ font-size: 14px; color: #8898aa; font-weight: 500; letter-spacing: 2px; margin-bottom: 12px; }}
        .title-section h1 {{ font-size: 42px; font-weight: 800; color: #1a1a1a; margin-bottom: 16px; letter-spacing: -1px; }}
        .name-gradient {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .age-display {{ display: inline-flex; align-items: center; gap: 8px; background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%); padding: 12px 28px; border-radius: 50px; margin-top: 8px; }}
        .age-number {{ font-size: 32px; font-weight: 800; background: linear-gradient(135deg, #667eea, #764ba2); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        .age-text {{ font-size: 14px; color: #667eea; font-weight: 600; }}
        .decor-line {{ display: flex; align-items: center; justify-content: center; gap: 16px; margin: 32px 0; padding: 0 32px; }}
        .decor-line .line {{ height: 1px; width: 80px; background: linear-gradient(90deg, transparent, #e2e8f0, transparent); }}
        .decor-line .icons {{ display: flex; gap: 8px; color: #f093fb; font-size: 10px; }}
        .content {{ padding: 0 32px; }}
        .wish-card {{ background: linear-gradient(145deg, #fafbff 0%, #f5f3ff 100%); border-radius: 20px; padding: 40px 36px; position: relative; border: 1px solid rgba(102, 126, 234, 0.1); box-shadow: 0 10px 40px rgba(102, 126, 234, 0.1); }}
        .wish-quote-mark {{ position: absolute; font-family: Georgia, serif; font-size: 80px; color: #667eea; opacity: 0.08; line-height: 1; }}
        .quote-mark-top {{ top: 16px; left: 24px; }} .quote-mark-bottom {{ bottom: -20px; right: 24px; }}
        .wish-text {{ font-size: 18px; line-height: 2; color: #374151; text-align: center; position: relative; z-index: 1; font-weight: 400; }}
        .quote-box {{ margin-top: 28px; padding: 24px 28px; background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); border-radius: 16px; position: relative; border-left: 4px solid #f59e0b; }}
        .quote-box::before {{ content: '💭'; position: absolute; top: -12px; left: 20px; font-size: 24px; }}
        .quote-text {{ font-size: 14px; color: #92400e; line-height: 1.8; font-style: italic; padding-left: 8px; }}
        .stats-bar {{ display: flex; justify-content: center; gap: 16px; margin: 32px 0; padding: 20px; background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 16px; }}
        .stat-item {{ text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #0284c7; }}
        .stat-label {{ font-size: 11px; color: #64748b; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
        .footer {{ background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); padding: 32px; text-align: center; border-top: 1px solid #e2e8f0; }}
        .footer-emoji {{ font-size: 36px; margin-bottom: 16px; }}
        .footer-main {{ font-size: 15px; color: #475569; margin-bottom: 8px; }}
        .footer-sub {{ font-size: 13px; color: #94a3b8; }}
        .footer-tiny {{ font-size: 11px; color: #cbd5e1; margin-top: 16px; }}
        @media only screen and (max-width: 600px) {{ body {{ padding: 12px; }} .title-section h1 {{ font-size: 32px; }} .title-section {{ padding: 0 20px 20px; }} .content {{ padding: 0 20px; }} .wish-card {{ padding: 28px 24px; }} .wish-text {{ font-size: 16px; }} .stats-bar {{ flex-direction: column; gap: 20px; }} .footer {{ padding: 24px 20px; }} }}
    </style>
</head>
<body>
    <div class="container">
        <div class="top-gradient">
            <div class="top-pattern"></div>
            <span class="floating-icon icon-1">✨</span><span class="floating-icon icon-2">🎈</span><span class="floating-icon icon-3">🎉</span><span class="floating-icon icon-4">⭐</span><span class="floating-icon icon-5">🎂</span>
        </div>
        <div class="main-wrapper">
            <div class="year-badge"><span>{year} BIRTHDAY SPECIAL</span></div>
            <div class="title-section">
                <h2>HAPPY BIRTHDAY</h2>
                <h1>亲爱的 <span class="name-gradient">{user_name}</span></h1>
                <div class="age-display"><span class="age-number">✨</span><span class="age-text">生日快乐</span></div>
            </div>
            <div class="decor-line"><div class="line"></div><div class="icons"><span>✦</span><span>✦</span><span>✦</span></div><div class="line"></div></div>
            <div class="content">
                <div class="wish-card">
                    <span class="wish-quote-mark quote-mark-top">"</span>
                    <p class="wish-text">{wish_content}</p>
                    <span class="wish-quote-mark quote-mark-bottom">"</span>
                </div>
                <div class="stats-bar">
                    <div class="stat-item"><div class="stat-value">🌟</div><div class="stat-label">美好年华</div></div>
                    <div class="stat-item"><div class="stat-value">∞</div><div class="stat-label">无限可能</div></div>
                    <div class="stat-item"><div class="stat-value">{year}</div><div class="stat-label">崭新篇章</div></div>
                </div>
                <div class="quote-box"><p class="quote-text">岁月从不败美人，时光温柔待良人。愿你在新的一岁里，眼里有光，心中有爱，脚下有路。</p></div>
            </div>
        </div>
        <div class="footer">
            <div class="footer-emoji">🎂 ✨ 🎈</div>
            <p class="footer-main">来自 <strong>{from_name}</strong> 的生日祝福</p>
            <p class="footer-sub">愿你的每一天都闪闪发光</p>
            <p class="footer-tiny">自动发送 · 请勿直接回复</p>
        </div>
    </div>
</body>
</html>
"""


def build_html_email(user_name, wish_content, year=None):
    """
    构建 HTML 邮件内容

    Args:
        user_name: 用户姓名
        wish_content: 祝福语内容
        year: 年份（可选，默认使用当前年份）

    Returns:
        str: HTML 格式的邮件内容
    """
    import datetime
    if year is None:
        year = datetime.datetime.now().year

    return EMAIL_TEMPLATE.format(
        user_name=user_name,
        wish_content=wish_content,
        from_name=Config.MAIL_FROM_NAME,
        year=year
    )


def build_text_email(user_name, wish_content, year=None):
    """
    构建纯文本邮件内容（备用）

    Args:
        user_name: 用户姓名
        wish_content: 祝福语内容
        year: 年份（可选）

    Returns:
        str: 纯文本格式的邮件内容
    """
    import datetime
    if year is None:
        year = datetime.datetime.now().year

    return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🎂  {year} · 生日特辑
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

亲爱的 {user_name}：

{wish_content}

"岁月不曾改变你的笑容，只让它更加温暖动人。
愿每一个生日，都成为你人生旅途中最美的里程碑。"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

来自 {Config.MAIL_FROM_NAME} 的生日祝福
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
