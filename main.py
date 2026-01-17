# -*- coding: utf-8 -*-
"""
自动化生日祝福系统 - 主程序入口
每天定时扫描并发送生日祝福邮件
"""

import schedule
import time
import sys
from datetime import datetime
from db_manager import DBManager
from email_service import send_birthday_email
from config import Config


def print_banner():
    """打印程序启动横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║         🎂 自动化生日祝福邮件系统 🎂                   ║
    ║           Auto-Birthday-Wisher v1.0                   ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(banner)


def job_scan_and_send():
    """定时任务：扫描并发送生日邮件"""
    print("\n" + "=" * 55)
    print(f"🔄 开始执行每日扫描任务... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print("=" * 55)

    db = None
    try:
        db = DBManager()

        # 1. 获取今天过生日的用户
        users = db.get_todays_birthdays()

        if not users:
            print("📭 今天暂时没有人过生日。")
            return

        print(f"🎉 发现 {len(users)} 位寿星，准备发送...")

        # 2. 遍历发送邮件
        success_count = 0
        failed_count = 0

        for user in users:
            print(f"\n📧 正在处理: {user['name']} ({user['email']})")

            # 获取随机祝福语
            wish = db.get_random_wish()
            print(f"   祝福语: {wish[:30]}...")

            # 发送邮件
            is_sent, error_msg = send_birthday_email(
                user['email'],
                user['name'],
                wish
            )

            # 更新发送状态
            if is_sent:
                db.update_send_status(user['id'], success=True)
                success_count += 1
            else:
                db.update_send_status(user['id'], success=False, error_msg=error_msg)
                failed_count += 1

        # 3. 输出结果统计
        print("\n" + "=" * 55)
        print(f"📊 本次任务完成:")
        print(f"   ✅ 成功: {success_count} 封")
        print(f"   ❌ 失败: {failed_count} 封")
        print("=" * 55 + "\n")

    except KeyboardInterrupt:
        print("\n⚠️ 任务被用户中断")
        raise

    except Exception as e:
        print(f"\n⚠️ 任务执行出错: {e}")

    finally:
        if db:
            db.close()


def job_backup_database():
    """定时任务：每周备份数据库（可选）"""
    print(f"🔄 [备份] 数据库备份任务执行中... [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    # TODO: 实现数据库备份逻辑
    print("📁 [备份] 备份功能待实现")


def run_once():
    """立即执行一次任务（用于测试）"""
    print("🧪 测试模式：立即执行一次任务\n")
    job_scan_and_send()


def run_daemon():
    """以守护进程模式运行"""
    # 设置定时任务
    schedule.every().day.at(Config.SEND_TIME).do(job_scan_and_send)
    # 可选：每周备份
    # schedule.every().week.at("02:00").do(job_backup_database)

    print(f"📅 定时任务已设置: 每天 {Config.SEND_TIME} 执行")
    print(f"⏰ 当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("⏳ 等待定时任务触发... (按 Ctrl+C 退出)\n")

    # 首次启动时显示统计
    try:
        db = DBManager()
        stats = db.get_user_stats()
        print(f"📊 系统统计:")
        print(f"   - 总用户数: {stats['total_users']}")
        print(f"   - 今日生日: {stats['today_birthdays']}")
        print(f"   - 本月生日: {stats['this_month_birthdays']}")
        db.close()
    except Exception as e:
        print(f"⚠️ 无法获取统计信息: {e}")

    print("")

    # 持续运行
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")


def main():
    """主入口函数"""
    print_banner()

    # 验证配置
    errors = Config.validate()
    if errors:
        print("❌ 配置错误，请检查 .env 文件：")
        for error in errors:
            print(f"   - {error}")
        sys.exit(1)

    # 解析命令行参数
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command in ['--once', '-o', 'test', 'run']:
            # 立即执行一次
            run_once()
        elif command in ['--help', '-h', 'help']:
            # 显示帮助
            print("""
使用方法:
    python main.py              # 以守护进程模式运行
    python main.py --once       # 立即执行一次任务（测试用）
    python main.py -h           # 显示帮助信息
            """)
        else:
            print(f"❌ 未知参数: {command}")
            print("   使用 --help 查看帮助信息")
            sys.exit(1)
    else:
        # 默认：守护进程模式
        run_daemon()


if __name__ == "__main__":
    main()
