# -*- coding: utf-8 -*-
"""
用户生日和祝福数据管理系统 - Web管理界面
基于Flask框架
"""

import os
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, get_flashed_messages
from db_manager import DBManager
from config import Config
from email_service import send_birthday_email

# 创建Flask应用
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'birthday-wisher-secret-key-2024')
app.config['JSON_AS_ASCII'] = False

# 模板和静态文件路径
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
static_dir = os.path.join(os.path.dirname(__file__), 'static')


# ========== 辅助函数 ==========

def get_db():
    """获取数据库连接"""
    return DBManager()


def parse_date(date_str):
    """解析多种日期格式"""
    if isinstance(date_str, datetime):
        return date_str

    # 支持的日期格式
    formats = [
        '%Y-%m-%d',      # 2003-01-17
        '%Y/%m/%d',      # 2003/01/17
        '%Y/%-m/%-d',    # 2003/1/17 (需要特殊处理)
        '%Y.%m.%d',      # 2003.01.17
        '%Y.%-m.%-d',    # 2003.1.17
    ]

    # 先尝试标准格式
    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue

    # 处理个位数月份/日期的情况 (如 2003/1/17)
    try:
        date_str = date_str.replace('/', '-')
        parts = date_str.split('-')
        if len(parts) == 3:
            year, month, day = parts
            return datetime(int(year), int(month), int(day))
    except:
        pass

    raise ValueError(f"无法解析日期: {date_str}")


def normalize_date(date_str):
    """将各种日期格式统一为 YYYY-MM-DD"""
    if isinstance(date_str, str):
        dt = parse_date(date_str)
        return dt.strftime('%Y-%m-%d')
    return date_str


def format_date(date_str):
    """格式化日期显示"""
    if isinstance(date_str, str):
        try:
            dt = parse_date(date_str)
            return dt.strftime('%Y年%m月%d日')
        except:
            return date_str
    return date_str


def calculate_age(dob):
    """计算年龄"""
    today = datetime.now()
    dob = parse_date(dob) if isinstance(dob, str) else dob
    age = today.year - dob.year
    if today.month < dob.month or (today.month == dob.month and today.day < dob.day):
        age -= 1
    return age


def calculate_next_birthday(dob):
    """计算距离下一个生日的天数"""
    today = datetime.now()
    dob = parse_date(dob) if isinstance(dob, str) else dob

    next_birthday = datetime(today.year, dob.month, dob.day)
    if next_birthday < today:
        next_birthday = datetime(today.year + 1, dob.month, dob.day)

    days_left = (next_birthday - today).days
    return days_left


# ========== 路由 ==========

@app.route('/')
def index():
    """首页 - 仪表盘"""
    db = get_db()
    try:
        # 获取统计数据
        stats = db.get_user_stats()

        # 获取即将过生日的用户（未来30天内）
        users = db.get_all_users()
        upcoming_birthdays = []
        today = datetime.now()

        for user in users:
            try:
                dob = parse_date(user['dob']) if isinstance(user['dob'], str) else user['dob']
                next_birthday = datetime(today.year, dob.month, dob.day)
                if next_birthday < today:
                    next_birthday = datetime(today.year + 1, dob.month, dob.day)

                days_left = (next_birthday - today).days
                if days_left <= 30:
                    user['days_until_birthday'] = days_left
                    user['age'] = calculate_age(user['dob'])
                    user['next_birthday_date'] = next_birthday.strftime('%m-%d')
                    user['dob_short'] = f"{dob.month:02d}-{dob.day:02d}"
                    upcoming_birthdays.append(user)
            except Exception:
                # 跳过日期解析失败的记录
                continue

        # 按天数排序
        upcoming_birthdays.sort(key=lambda x: x['days_until_birthday'])

        # 获取最近的发送日志
        recent_logs = db.get_send_logs(limit=10)

        # 祝福语统计
        wishes = db.get_all_wishes()
        active_wishes = [w for w in wishes if w.get('is_active', 1)]

        return render_template('index.html',
                             stats=stats,
                             upcoming_birthdays=upcoming_birthdays[:10],
                             recent_logs=recent_logs,
                             wish_count=len(wishes),
                             active_wish_count=len(active_wishes))
    finally:
        db.close()


# ========== 用户管理 ==========

@app.route('/users')
def users_list():
    """用户列表"""
    db = get_db()
    try:
        users = db.get_all_users()

        # 为每个用户计算额外信息
        for user in users:
            user['age'] = calculate_age(user['dob'])
            user['days_until_birthday'] = calculate_next_birthday(user['dob'])
            user['dob_formatted'] = format_date(user['dob'])
            # 添加短日期格式 (月-日)
            try:
                dt = parse_date(user['dob'])
                user['dob_short'] = f"{dt.month:02d}-{dt.day:02d}"
            except:
                user['dob_short'] = user['dob']

        # 获取搜索和筛选参数
        search = request.args.get('search', '')
        sort_by = request.args.get('sort', 'name')

        # 搜索过滤
        if search:
            users = [u for u in users if search.lower() in u['name'].lower() or search.lower() in u['email'].lower()]

        # 排序
        if sort_by == 'name':
            users.sort(key=lambda x: x['name'])
        elif sort_by == 'birthday':
            # 按月日排序
            def get_month_day(user):
                try:
                    dt = parse_date(user['dob'])
                    return (dt.month, dt.day)
                except:
                    return (12, 31)  # 无法解析的排到最后
            users.sort(key=lambda x: (get_month_day(x), x['name']))
        elif sort_by == 'days':
            users.sort(key=lambda x: x['days_until_birthday'])

        return render_template('users.html', users=users, search=search, sort_by=sort_by)
    finally:
        db.close()


@app.route('/users/add', methods=['GET', 'POST'])
def users_add():
    """添加用户"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        dob = request.form.get('dob', '')

        # 验证
        if not name or not email or not dob:
            flash('请填写完整信息', 'error')
        else:
            # 规范化日期格式
            try:
                dob = normalize_date(dob)
            except ValueError as e:
                flash(f'日期格式错误：{str(e)}', 'error')
                return render_template('users_form.html', user=None)

            db = get_db()
            try:
                db.add_user(name, email, dob)
                flash(f'用户 {name} 添加成功！', 'success')
                return redirect(url_for('users_list'))
            except Exception as e:
                flash(f'添加失败：{str(e)}', 'error')
            finally:
                db.close()

    return render_template('users_form.html', user=None)


@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def users_edit(user_id):
    """编辑用户"""
    db = get_db()
    try:
        if request.method == 'POST':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            dob = request.form.get('dob', '')
            last_sent_year = request.form.get('last_sent_year')

            # 验证
            if not name or not email or not dob:
                flash('请填写完整信息', 'error')
            else:
                # 规范化日期格式
                try:
                    dob = normalize_date(dob)
                except ValueError as e:
                    flash(f'日期格式错误：{str(e)}', 'error')
                    # 重新获取用户信息
                    if db.db_type == 'sqlite':
                        users = db._execute("SELECT * FROM users WHERE id=?", (user_id,), fetch=True)
                    else:
                        users = db._execute("SELECT * FROM users WHERE id=%s", (user_id,), fetch=True)
                    user = users[0] if users else None
                    return render_template('users_form.html', user=user)

                try:
                    if db.db_type == 'sqlite':
                        sql = """UPDATE users SET name=?, email=?, dob=?, last_sent_year=?, updated_at=datetime('now')
                                WHERE id=?"""
                        db._execute(sql, (name, email, dob, int(last_sent_year) if last_sent_year else None, user_id))
                    else:
                        sql = """UPDATE users SET name=%s, email=%s, dob=%s, last_sent_year=%s, updated_at=NOW()
                                WHERE id=%s"""
                        db._execute(sql, (name, email, dob, int(last_sent_year) if last_sent_year else None, user_id))
                    db.conn.commit()
                    flash(f'用户 {name} 更新成功！', 'success')
                    return redirect(url_for('users_list'))
                except Exception as e:
                    flash(f'更新失败：{str(e)}', 'error')
        else:
            # 获取用户信息
            if db.db_type == 'sqlite':
                users = db._execute("SELECT * FROM users WHERE id=?", (user_id,), fetch=True)
            else:
                users = db._execute("SELECT * FROM users WHERE id=%s", (user_id,), fetch=True)

            if users:
                user = users[0]
                # 添加表单友好的日期格式
                try:
                    user['dob_for_form'] = normalize_date(user['dob'])
                except:
                    user['dob_for_form'] = user['dob']
                return render_template('users_form.html', user=user)
            else:
                flash('用户不存在', 'error')
                return redirect(url_for('users_list'))
    finally:
        db.close()

    return redirect(url_for('users_list'))


@app.route('/users/delete/<int:user_id>', methods=['POST'])
def users_delete(user_id):
    """删除用户"""
    db = get_db()
    try:
        # 先获取用户名用于提示
        if db.db_type == 'sqlite':
            users = db._execute("SELECT name FROM users WHERE id=?", (user_id,), fetch=True)
        else:
            users = db._execute("SELECT name FROM users WHERE id=%s", (user_id,), fetch=True)

        if users:
            name = users[0]['name']
            # 删除用户（级联删除相关日志）
            if db.db_type == 'sqlite':
                db._execute("DELETE FROM users WHERE id=?", (user_id,))
            else:
                db._execute("DELETE FROM users WHERE id=%s", (user_id,))
            db.conn.commit()
            flash(f'用户 {name} 已删除', 'success')
        else:
            flash('用户不存在', 'error')
    except Exception as e:
        flash(f'删除失败：{str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('users_list'))


@app.route('/users/batch-import', methods=['GET', 'POST'])
def users_batch_import():
    """批量导入用户"""
    if request.method == 'POST':
        # 检查文件上传
        if 'file' not in request.files:
            flash('请选择文件', 'error')
            return redirect(url_for('users_batch_import'))

        file = request.files['file']
        if file.filename == '':
            flash('请选择文件', 'error')
            return redirect(url_for('users_batch_import'))

        # 处理CSV文件
        if file and file.filename.endswith('.csv'):
            try:
                import csv
                from io import StringIO

                content = StringIO(file.read().decode('utf-8'))
                reader = csv.DictReader(content)

                db = get_db()
                success_count = 0
                duplicate_count = 0
                error_count = 0

                try:
                    for row in reader:
                        name = row.get('name', '').strip()
                        email = row.get('email', '').strip()
                        dob = row.get('dob', '').strip()

                        if name and email and dob:
                            try:
                                # 规范化日期格式
                                dob = normalize_date(dob)
                            except ValueError:
                                error_count += 1
                                continue

                            # 检查是否已存在
                            if db.db_type == 'sqlite':
                                existing = db._execute("SELECT id FROM users WHERE email=?", (email,), fetch=True)
                            else:
                                existing = db._execute("SELECT id FROM users WHERE email=%s", (email,), fetch=True)

                            if not existing:
                                db.add_user(name, email, dob)
                                success_count += 1
                            else:
                                duplicate_count += 1

                    msg = f'导入完成！成功：{success_count}条'
                    if duplicate_count:
                        msg += f'，重复：{duplicate_count}条'
                    if error_count:
                        msg += f'，格式错误：{error_count}条'
                    flash(msg, 'success')
                finally:
                    db.close()

            except Exception as e:
                flash(f'导入失败：{str(e)}', 'error')
        else:
            flash('请上传CSV文件', 'error')

    return render_template('users_import.html')


# ========== 祝福语管理 ==========

@app.route('/wishes')
def wishes_list():
    """祝福语列表"""
    db = get_db()
    try:
        wishes = db.get_all_wishes()

        # 按分类分组
        categories = {}
        for wish in wishes:
            category = wish.get('category', 'general')
            if category not in categories:
                categories[category] = []
            categories[category].append(wish)

        # 分类名称映射
        category_names = {
            'general': '通用',
            'formal': '正式',
            'warm': '温馨',
            'humor': '幽默',
            'poetic': '诗意'
        }

        return render_template('wishes.html', wishes=wishes, categories=categories, category_names=category_names)
    finally:
        db.close()


@app.route('/wishes/add', methods=['POST'])
def wishes_add():
    """添加祝福语"""
    content = request.form.get('content', '').strip()
    category = request.form.get('category', 'general')

    if content:
        db = get_db()
        try:
            db.add_wish(content, category)
            flash('祝福语添加成功！', 'success')
        except Exception as e:
            flash(f'添加失败：{str(e)}', 'error')
        finally:
            db.close()
    else:
        flash('请输入祝福语内容', 'error')

    return redirect(url_for('wishes_list'))


@app.route('/wishes/delete/<int:wish_id>', methods=['POST'])
def wishes_delete(wish_id):
    """删除祝福语"""
    db = get_db()
    try:
        if db.db_type == 'sqlite':
            db._execute("DELETE FROM wishes WHERE id=?", (wish_id,))
        else:
            db._execute("DELETE FROM wishes WHERE id=%s", (wish_id,))
        db.conn.commit()
        flash('祝福语已删除', 'success')
    except Exception as e:
        flash(f'删除失败：{str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('wishes_list'))


@app.route('/wishes/toggle/<int:wish_id>', methods=['POST'])
def wishes_toggle(wish_id):
    """启用/禁用祝福语"""
    db = get_db()
    try:
        if db.db_type == 'sqlite':
            db._execute("UPDATE wishes SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=?", (wish_id,))
        else:
            db._execute("UPDATE wishes SET is_active = CASE WHEN is_active=1 THEN 0 ELSE 1 END WHERE id=%s", (wish_id,))
        db.conn.commit()
        flash('状态已更新', 'success')
    except Exception as e:
        flash(f'操作失败：{str(e)}', 'error')
    finally:
        db.close()

    return redirect(url_for('wishes_list'))


# ========== 发送日志 ==========

@app.route('/logs')
def logs_list():
    """发送日志"""
    db = get_db()
    try:
        logs = db.get_send_logs(limit=200)

        # 统计
        success_count = sum(1 for log in logs if log.get('status') == 'success')
        failed_count = len(logs) - success_count

        return render_template('logs.html', logs=logs, success_count=success_count, failed_count=failed_count)
    finally:
        db.close()


# ========== 手动发送 ==========

@app.route('/send', methods=['GET', 'POST'])
def send_test():
    """手动发送测试邮件"""
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        name = request.form.get('name', '').strip()
        wish = request.form.get('wish', '')

        if not email or not name:
            flash('请输入收件人姓名和邮箱', 'error')
        else:
            # 如果没有指定祝福语，随机获取
            if not wish:
                db = get_db()
                wish = db.get_random_wish()
                db.close()

            # 发送邮件
            is_sent, error_msg = send_birthday_email(email, name, wish)

            if is_sent:
                flash('邮件发送成功！', 'success')
            else:
                flash(f'发送失败：{error_msg}', 'error')

    return render_template('send.html')


# ========== API接口 ==========

@app.route('/api/stats')
def api_stats():
    """获取统计信息API"""
    db = get_db()
    try:
        stats = db.get_user_stats()
        return jsonify(stats)
    finally:
        db.close()


@app.route('/api/upcoming-birthdays')
def api_upcoming_birthdays():
    """获取即将过生日的用户API"""
    db = get_db()
    try:
        users = db.get_all_users()
        today = datetime.now()
        upcoming = []

        for user in users:
            dob = datetime.strptime(user['dob'], '%Y-%m-%d') if isinstance(user['dob'], str) else user['dob']
            next_birthday = datetime(today.year, dob.month, dob.day)
            if next_birthday < today:
                next_birthday = datetime(today.year + 1, dob.month, dob.day)

            days_left = (next_birthday - today).days
            if days_left <= 30:
                user['days_until_birthday'] = days_left
                user['age'] = calculate_age(user['dob'])
                upcoming.append(user)

        upcoming.sort(key=lambda x: x['days_until_birthday'])
        return jsonify(upcoming[:10])
    finally:
        db.close()


# ========== 错误处理 ==========

@app.errorhandler(404)
def not_found(error):
    return render_template('error.html', error='页面不存在'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('error.html', error='服务器错误'), 500


# ========== 启动 ==========

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     🎂 用户生日和祝福数据管理系统 🎂                   ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    # 检查配置
    errors = Config.validate()
    if errors:
        print("❌ 配置错误：")
        for error in errors:
            print(f"   - {error}")
    else:
        print("✅ 配置加载成功")
        print(f"🌐 管理界面地址: http://127.0.0.1:5001")
        print("📝 按 Ctrl+C 停止服务\n")

    app.run(host='0.0.0.0', port=5001, debug=True)
