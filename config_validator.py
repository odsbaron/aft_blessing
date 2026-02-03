# -*- coding: utf-8 -*-
"""
配置验证模块
检查系统配置的完整性和安全性
"""

import os
from config import Config


class ConfigValidator:
    """配置验证器"""

    # 必需配置项
    REQUIRED_CONFIGS = {
        'mail': {
            'MAIL_USER': '邮箱用户名',
            'MAIL_AUTH_CODE': '邮箱授权码',
        },
        'database': {
            # 数据库配置可选（SQLite可用默认值）
        }
    }

    # 推荐配置项
    RECOMMENDED_CONFIGS = {
        'SECRET_KEY': '应用密钥（用于会话加密）',
        'MAIL_FROM_NAME': '发件人名称',
        'PINATA_JWT': 'Pinata API密钥（用于IPFS功能）',
        'PRIVATE_KEY': '区块链私钥（用于NFT部署，仅生产环境需要）',
    }

    # 安全警告配置
    SECURITY_WARNINGS = {
        'default_secret_key': 'SECRET_KEY使用默认值，存在安全风险',
        'weak_password': '建议使用复杂密码',
        'http_only': '建议在生产环境使用HTTPS',
    }

    @classmethod
    def validate_all(cls):
        """
        验证所有配置

        Returns:
            dict: {errors: [], warnings: [], recommendations: []}
        """
        result = {
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'score': 100  # 配置安全分数
        }

        # 检查必需配置
        mail_errors = Config.validate()
        result['errors'].extend(mail_errors)
        result['score'] -= len(mail_errors) * 20

        # 检查安全配置
        if Config.SECRET_KEY == 'birthday-wisher-secret-key-2024':
            result['warnings'].append('⚠️ 使用默认SECRET_KEY，请修改为随机值')
            result['score'] -= 10

        # 检查数据库配置
        if Config.DB_TYPE == 'sqlite':
            result['recommendations'].append('ℹ️ 当前使用SQLite数据库，生产环境建议使用MySQL或PostgreSQL')

        # 检查速率限制配置
        rate_limit_ok = (
            hasattr(Config, 'MAX_EMAILS_PER_HOUR') and
            hasattr(Config, 'MAX_EMAILS_PER_DAY') and
            Config.MAX_EMAILS_PER_HOUR > 0 and
            Config.MAX_EMAILS_PER_DAY > 0
        )
        if not rate_limit_ok:
            result['recommendations'].append('ℹ️ 建议配置邮件速率限制以防止触发服务商限制')
        else:
            result['score'] += 5

        # 检查IPFS配置
        has_ipfs = (
            hasattr(Config, 'PINATA_JWT') and Config.PINATA_JWT or
            (hasattr(Config, 'PINATA_API_KEY') and Config.PINATA_API_KEY)
        )
        if not has_ipfs:
            result['recommendations'].append('ℹ️ 未配置IPFS，NFT图片上传功能将不可用')

        # 检查NFT配置
        if not Config.CONTRACT_ADDRESS:
            result['recommendations'].append('ℹ️ 未配置NFT合约地址，需要先部署合约')

        return result

    @classmethod
    def print_report(cls):
        """打印配置验证报告"""
        result = cls.validate_all()

        print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         🔍 配置验证报告 🔍                             ║
    ╚═══════════════════════════════════════════════════════╝
        """)

        # 显示错误
        if result['errors']:
            print("🔴 错误（必须修复）：")
            for error in result['errors']:
                print(f"   - {error}")
            print()
        else:
            print("✅ 必需配置检查通过")

        # 显示警告
        if result['warnings']:
            print("\n🟠 警告（建议修复）：")
            for warning in result['warnings']:
                print(f"   {warning}")

        # 显示推荐
        if result['recommendations']:
            print("\n🔵 建议：")
            for rec in result['recommendations']:
                print(f"   {rec}")

        # 显示分数
        score = max(0, min(100, result['score']))
        grade = 'A' if score >= 90 else 'B' if score >= 70 else 'C' if score >= 50 else 'D'

        print(f"\n📊 配置安全分数: {score}/100 (等级: {grade})")

        if score >= 90:
            print("✅ 配置状态: 优秀")
        elif score >= 70:
            print("🟡 配置状态: 良好")
        elif score >= 50:
            print("🟠 配置状态: 一般")
        else:
            print("🔴 配置状态: 需要改进")

        print("\n" + "=" * 50)

        return result

    @classmethod
    def generate_env_template(cls, output_path='.env.example'):
        """生成环境变量模板文件"""
        template = """# 邮件配置
MAIL_SERVER=smtp.163.com
MAIL_PORT=465
MAIL_USER=your_email@example.com
MAIL_AUTH_CODE=your_authorization_code
MAIL_FROM_NAME=生日祝福助手

# 数据库配置 (DB_TYPE: sqlite, mysql, postgresql)
DB_TYPE=sqlite
# DB_SQLITE_PATH=birthday.db
# DB_HOST=localhost
# DB_PORT=3306
# DB_USER=root
# DB_PASS=your_password
# DB_NAME=birthday_db

# PostgreSQL 连接字符串 (Railway等平台)
# DATABASE_URL=postgresql://user:password@host:port/database

# 安全配置
SECRET_KEY=please_change_this_to_a_random_string

# 速率限制配置
MAX_EMAILS_PER_HOUR=50
MAX_EMAILS_PER_DAY=200
EMAIL_COOLDOWN_SECONDS=300
MIN_EMAIL_INTERVAL=2

# 定时任务配置
SEND_TIME=09:00

# Pinata IPFS配置 (用于NFT图片上传)
PINATA_JWT=your_pinata_jwt_token
# PINATA_API_KEY=your_api_key
# PINATA_API_SECRET=your_api_secret

# 区块链/NFT配置
# NETWORK=amoy  # amoy (测试网) 或 polygon (主网)
# CONTRACT_ADDRESS=your_contract_address
# PRIVATE_KEY=your_wallet_private_key
"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(template)

        print(f"✅ 环境变量模板已生成: {output_path}")


def check_config_on_startup():
    """应用启动时检查配置"""
    result = ConfigValidator.validate_all()

    # 只打印关键问题
    if result['errors']:
        print("\n🔴 配置错误：")
        for error in result['errors']:
            print(f"   - {error}")
        print("\n请检查 .env 文件配置\n")

    if result['warnings']:
        print("\n⚠️ 安全警告：")
        for warning in result['warnings']:
            print(f"   {warning}")
        print()

    return len(result['errors']) == 0


if __name__ == "__main__":
    ConfigValidator.print_report()
    ConfigValidator.generate_env_template()
