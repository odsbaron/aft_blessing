# -*- coding: utf-8 -*-
"""
邮件模板管理模块
支持创建、编辑、预览和使用自定义邮件模板
"""

import re
from typing import Dict, List, Optional
from db_manager import DBManager


class EmailTemplate:
    """邮件模板类"""

    # 默认模板 - 现代设计风格
    DEFAULT_TEMPLATE = {
        'name': 'default',
        'title': '现代设计模板',
        'subject': '🎉 {name}，生日快乐！',
        'html_template': """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Helvetica Neue', 'Microsoft YaHei', 'PingFang SC', Arial, sans-serif;
            line-height: 1.7;
            color: #1a1a1a;
            background: #f0f4f8;
            padding: 20px;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: #ffffff;
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1), 0 8px 20px rgba(0,0,0,0.06);
        }}

        /* 顶部渐变区域 */
        .top-gradient {{
            height: 180px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            position: relative;
            overflow: hidden;
        }}
        .top-pattern {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: 0.1;
            background-image: radial-gradient(circle at 20% 50%, white 1px, transparent 1px);
            background-size: 20px 20px;
        }}
        .floating-icon {{
            position: absolute;
            font-size: 24px;
            opacity: 0.2;
        }}
        .icon-1 {{ top: 20px; left: 10%; }}
        .icon-2 {{ top: 40px; right: 15%; }}
        .icon-3 {{ top: 80px; left: 20%; }}
        .icon-4 {{ bottom: 30px; right: 10%; }}
        .icon-5 {{ top: 120px; left: 40%; }}

        /* 主体内容区 */
        .main-wrapper {{
            padding: 0 0 32px;
            margin-top: -60px;
            position: relative;
            z-index: 10;
        }}

        /* 年份徽章 */
        .year-badge {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .year-badge span {{
            display: inline-block;
            padding: 10px 28px;
            background: white;
            color: #667eea;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 3px;
            text-transform: uppercase;
            border-radius: 30px;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
        }}

        /* 标题区域 */
        .title-section {{
            text-align: center;
            padding: 0 32px 24px;
        }}
        .title-section h2 {{
            font-size: 14px;
            color: #8898aa;
            font-weight: 500;
            letter-spacing: 2px;
            margin-bottom: 12px;
        }}
        .title-section h1 {{
            font-size: 42px;
            font-weight: 800;
            color: #1a1a1a;
            margin-bottom: 16px;
            letter-spacing: -1px;
        }}
        .name-gradient {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        /* 年龄展示 */
        .age-display {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #f0f4ff 0%, #faf5ff 100%);
            padding: 12px 28px;
            border-radius: 50px;
            margin-top: 8px;
        }}
        .age-number {{
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .age-text {{
            font-size: 14px;
            color: #667eea;
            font-weight: 600;
        }}

        /* 装饰线 */
        .decor-line {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 16px;
            margin: 32px 0;
            padding: 0 32px;
        }}
        .decor-line .line {{
            height: 1px;
            width: 80px;
            background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        }}
        .decor-line .icons {{
            display: flex;
            gap: 8px;
            color: #f093fb;
            font-size: 10px;
        }}

        /* 内容区域 */
        .content {{ padding: 0 32px; }}

        /* 祝福语卡片 */
        .wish-card {{
            background: linear-gradient(145deg, #fafbff 0%, #f5f3ff 100%);
            border-radius: 20px;
            padding: 40px 36px;
            position: relative;
            border: 1px solid rgba(102, 126, 234, 0.1);
            box-shadow: 0 10px 40px rgba(102, 126, 234, 0.1);
        }}
        .wish-quote-mark {{
            position: absolute;
            font-family: Georgia, serif;
            font-size: 80px;
            color: #667eea;
            opacity: 0.08;
            line-height: 1;
        }}
        .quote-mark-top {{ top: 16px; left: 24px; }}
        .quote-mark-bottom {{ bottom: -20px; right: 24px; }}
        .wish-text {{
            font-size: 18px;
            line-height: 2;
            color: #374151;
            text-align: center;
            position: relative;
            z-index: 1;
            font-weight: 400;
        }}

        /* 引用区域 */
        .quote-box {{
            margin-top: 28px;
            padding: 24px 28px;
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 16px;
            position: relative;
            border-left: 4px solid #f59e0b;
        }}
        .quote-box::before {{
            content: '💭';
            position: absolute;
            top: -12px;
            left: 20px;
            font-size: 24px;
        }}
        .quote-text {{
            font-size: 14px;
            color: #92400e;
            line-height: 1.8;
            font-style: italic;
            padding-left: 8px;
        }}

        /* 统计信息条 */
        .stats-bar {{
            display: flex;
            justify-content: center;
            gap: 16px;
            margin: 32px 0;
            padding: 20px;
            background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
            border-radius: 16px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 700;
            color: #0284c7;
        }}
        .stat-label {{
            font-size: 11px;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 4px;
        }}

        /* 底部 */
        .footer {{
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 32px;
            text-align: center;
            border-top: 1px solid #e2e8f0;
        }}
        .footer-emoji {{ font-size: 36px; margin-bottom: 16px; }}
        .footer-main {{
            font-size: 15px;
            color: #475569;
            margin-bottom: 8px;
        }}
        .footer-sub {{
            font-size: 13px;
            color: #94a3b8;
        }}
        .footer-tiny {{
            font-size: 11px;
            color: #cbd5e1;
            margin-top: 16px;
        }}

        /* 响应式 */
        @media only screen and (max-width: 600px) {{
            body {{ padding: 12px; }}
            .title-section h1 {{ font-size: 32px; }}
            .title-section {{ padding: 0 20px 20px; }}
            .content {{ padding: 0 20px; }}
            .wish-card {{ padding: 28px 24px; }}
            .wish-text {{ font-size: 16px; }}
            .stats-bar {{ flex-direction: column; gap: 20px; }}
            .footer {{ padding: 24px 20px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 顶部渐变装饰区 -->
        <div class="top-gradient">
            <div class="top-pattern"></div>
            <span class="floating-icon icon-1">✨</span>
            <span class="floating-icon icon-2">🎈</span>
            <span class="floating-icon icon-3">🎉</span>
            <span class="floating-icon icon-4">⭐</span>
            <span class="floating-icon icon-5">🎂</span>
        </div>

        <div class="main-wrapper">
            <!-- 年份徽章 -->
            <div class="year-badge">
                <span>{year} BIRTHDAY SPECIAL</span>
            </div>

            <!-- 标题区 -->
            <div class="title-section">
                <h2>HAPPY BIRTHDAY</h2>
                <h1>亲爱的 <span class="name-gradient">{name}</span></h1>
                <div class="age-display">
                    <span class="age-number">{age}</span>
                    <span class="age-text">岁了！</span>
                </div>
            </div>

            <!-- 装饰线 -->
            <div class="decor-line">
                <div class="line"></div>
                <div class="icons">
                    <span>✦</span><span>✦</span><span>✦</span>
                </div>
                <div class="line"></div>
            </div>

            <!-- 内容区 -->
            <div class="content">
                <!-- 祝福语卡片 -->
                <div class="wish-card">
                    <span class="wish-quote-mark quote-mark-top">"</span>
                    <p class="wish-text">{wish}</p>
                    <span class="wish-quote-mark quote-mark-bottom">"</span>
                </div>

                <!-- 统计信息 -->
                <div class="stats-bar">
                    <div class="stat-item">
                        <div class="stat-value">{age}</div>
                        <div class="stat-label">美好年华</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">∞</div>
                        <div class="stat-label">无限可能</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">{year}</div>
                        <div class="stat-label">崭新篇章</div>
                    </div>
                </div>

                <!-- 引用区 -->
                <div class="quote-box">
                    <p class="quote-text">岁月从不败美人，时光温柔待良人。愿你在新的一岁里，眼里有光，心中有爱，脚下有路。</p>
                </div>
            </div>
        </div>

        <!-- 底部 -->
        <div class="footer">
            <div class="footer-emoji">🎂 ✨ 🎈</div>
            <p class="footer-main">来自 <strong>{from_name}</strong> 的生日祝福</p>
            <p class="footer-sub">愿你的每一天都闪闪发光</p>
            <p class="footer-tiny">自动发送 · 请勿直接回复</p>
        </div>
    </div>
</body>
</html>""",
        'is_active': True
    }

    # 可用变量
    VARIABLES = {
        'name': '收件人姓名',
        'wish': '祝福语内容',
        'from_name': '发件人名称',
        'year': '当前年份',
        'age': '收件人年龄（需要提供DOB）',
        'nft_section': 'NFT领取部分（如有）'
    }

    def __init__(self, db: DBManager = None):
        self.db = db or DBManager()

    def render(self, template_name: str, variables: Dict) -> Dict[str, str]:
        """
        渲染邮件模板

        Args:
            template_name: 模板名称
            variables: 模板变量

        Returns:
            dict: {subject, html, text}
        """
        template = self.get_template(template_name)
        if not template:
            template = self.DEFAULT_TEMPLATE

        # 替换变量
        subject = template['subject']
        html_content = template['html_template']

        for key, value in variables.items():
            placeholder = '{' + key + '}'
            subject = subject.replace(placeholder, str(value))
            html_content = html_content.replace(placeholder, str(value))

        return {
            'subject': subject,
            'html': html_content,
            'text': self._generate_text_version(variables)
        }

    def _generate_text_version(self, variables: Dict) -> str:
        """生成纯文本版本"""
        year = variables.get('year', '2024')
        name = variables.get('name', '朋友')
        wish = variables.get('wish', '生日快乐！')
        from_name = variables.get('from_name', '生日祝福助手')

        return f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     🎂  {year} · 生日特辑
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

亲爱的 {name}：

{wish}

"岁月不曾改变你的笑容，只让它更加温暖动人。
愿每一个生日，都成为你人生旅途中最美的里程碑。"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

来自 {from_name} 的生日祝福

这是一封自动发送的邮件，请勿直接回复
"""

    def get_template(self, name: str) -> Optional[Dict]:
        """获取指定模板"""
        if name == 'default':
            return self.DEFAULT_TEMPLATE

        if self.db.db_type == 'sqlite':
            templates = self.db._execute(
                "SELECT * FROM email_templates WHERE name = ? AND is_active = 1",
                (name,),
                fetch=True
            )
        else:
            templates = self.db._execute(
                "SELECT * FROM email_templates WHERE name = %s AND is_active = 1",
                (name,),
                fetch=True
            )

        return templates[0] if templates else None

    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        if self.db.db_type == 'sqlite':
            templates = self.db._execute(
                "SELECT * FROM email_templates ORDER BY created_at DESC",
                fetch=True
            )
        else:
            templates = self.db._execute(
                "SELECT * FROM email_templates ORDER BY created_at DESC",
                fetch=True
            )

        return templates

    def create_template(
        self,
        name: str,
        title: str,
        subject: str,
        html_template: str,
        description: str = ''
    ) -> bool:
        """创建新模板"""
        if self.db.db_type == 'sqlite':
            self.db._execute("""
                INSERT INTO email_templates (name, title, subject, html_template, description)
                VALUES (?, ?, ?, ?, ?)
            """, (name, title, subject, html_template, description))
        else:
            self.db._execute("""
                INSERT INTO email_templates (name, title, subject, html_template, description)
                VALUES (%s, %s, %s, %s, %s)
            """, (name, title, subject, html_template, description))

        self.db.conn.commit()
        return True

    def update_template(
        self,
        template_id: int,
        title: str = None,
        subject: str = None,
        html_template: str = None,
        description: str = None,
        is_active: bool = None
    ) -> bool:
        """更新模板"""
        updates = []
        params = []

        if title is not None:
            updates.append("title = ?" if self.db.db_type == 'sqlite' else "title = %s")
            params.append(title)

        if subject is not None:
            updates.append("subject = ?" if self.db.db_type == 'sqlite' else "subject = %s")
            params.append(subject)

        if html_template is not None:
            updates.append("html_template = ?" if self.db.db_type == 'sqlite' else "html_template = %s")
            params.append(html_template)

        if description is not None:
            updates.append("description = ?" if self.db.db_type == 'sqlite' else "description = %s")
            params.append(description)

        if is_active is not None:
            updates.append("is_active = ?" if self.db.db_type == 'sqlite' else "is_active = %s")
            params.append(1 if is_active else 0)

        if not updates:
            return False

        params.append(template_id)
        sql = f"UPDATE email_templates SET {', '.join(updates)} WHERE id = {'?' if self.db.db_type == 'sqlite' else '%s'}"

        self.db._execute(sql, params)
        self.db.conn.commit()
        return True

    def delete_template(self, template_id: int) -> bool:
        """删除模板"""
        if self.db.db_type == 'sqlite':
            self.db._execute("DELETE FROM email_templates WHERE id = ?", (template_id,))
        else:
            self.db._execute("DELETE FROM email_templates WHERE id = %s", (template_id,))

        self.db.conn.commit()
        return True

    def duplicate_template(self, template_id: int, new_name: str) -> bool:
        """复制模板"""
        template = self.get_template_by_id(template_id)
        if not template:
            return False

        return self.create_template(
            name=new_name,
            title=template['title'] + ' (副本)',
            subject=template['subject'],
            html_template=template['html_template'],
            description=template.get('description', '')
        )

    def get_template_by_id(self, template_id: int) -> Optional[Dict]:
        """根据ID获取模板"""
        if self.db.db_type == 'sqlite':
            templates = self.db._execute(
                "SELECT * FROM email_templates WHERE id = ?",
                (template_id,),
                fetch=True
            )
        else:
            templates = self.db._execute(
                "SELECT * FROM email_templates WHERE id = %s",
                (template_id,),
                fetch=True
            )

        return templates[0] if templates else None

    def set_default_template(self, template_id: int) -> bool:
        """设置默认模板"""
        # 先取消所有默认标记
        if self.db.db_type == 'sqlite':
            self.db._execute("UPDATE email_templates SET is_default = 0")
            self.db._execute("UPDATE email_templates SET is_default = 1 WHERE id = ?", (template_id,))
        else:
            self.db._execute("UPDATE email_templates SET is_default = 0")
            self.db._execute("UPDATE email_templates SET is_default = 1 WHERE id = %s", (template_id,))

        self.db.conn.commit()
        return True

    def get_default_template(self) -> Optional[Dict]:
        """获取默认模板"""
        if self.db.db_type == 'sqlite':
            templates = self.db._execute(
                "SELECT * FROM email_templates WHERE is_default = 1 AND is_active = 1",
                fetch=True
            )
        else:
            templates = self.db._execute(
                "SELECT * FROM email_templates WHERE is_default = 1 AND is_active = 1",
                fetch=True
            )

        return templates[0] if templates else None

    def validate_template(self, html_template: str) -> List[str]:
        """验证模板语法，返回错误列表"""
        errors = []

        # 检查必须有 {name} 变量
        if '{name}' not in html_template:
            errors.append("模板必须包含 {name} 变量")

        # 检查必须有 {wish} 变量
        if '{wish}' not in html_template:
            errors.append("模板必须包含 {wish} 变量")

        # 检查HTML结构
        if '</html>' not in html_template.lower():
            errors.append("模板不是完整的HTML文档")

        # 检查未闭合的标签
        open_tags = re.findall(r'<(\w+)[^>]*>', html_template)
        close_tags = re.findall(r'</(\w+)>', html_template)

        # 简单检查（忽略自闭合标签）
        for tag in ['div', 'span', 'p', 'h1', 'h2', 'h3', 'td']:
            if open_tags.count(tag) > close_tags.count(tag):
                errors.append(f"<{tag}> 标签可能未正确闭合")

        return errors

    def preview(self, template_name: str) -> Dict:
        """预览模板（使用示例数据）"""
        sample_data = {
            'name': '张三',
            'wish': '生日快乐！愿你的每一天都充满阳光和欢笑！',
            'from_name': '生日祝福助手',
            'year': '2024',
            'age': '25'
        }

        return self.render(template_name, sample_data)


def init_default_templates():
    """初始化默认模板到数据库"""
    db = DBManager()
    try:
        # 创建表
        if db.db_type == 'sqlite':
            db._execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    title TEXT NOT NULL,
                    subject TEXT NOT NULL,
                    html_template TEXT NOT NULL,
                    description TEXT,
                    is_active INTEGER DEFAULT 1,
                    is_default INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        else:
            db._execute("""
                CREATE TABLE IF NOT EXISTS email_templates (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL UNIQUE,
                    title VARCHAR(100) NOT NULL,
                    subject VARCHAR(200) NOT NULL,
                    html_template TEXT NOT NULL,
                    description TEXT,
                    is_active TINYINT(1) DEFAULT 1,
                    is_default TINYINT(1) DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)

        db.conn.commit()

        # 检查是否有模板，没有则添加默认模板
        templates = db._execute(
            "SELECT COUNT(*) as count FROM email_templates",
            fetch=True
        )

        if templates[0]['count'] == 0:
            tpl = EmailTemplate()
            tpl.create_template(
                name='default',
                title='默认模板',
                subject='🎂 {name}，生日快乐！',
                html_template=EmailTemplate.DEFAULT_TEMPLATE['html_template'],
                description='系统默认的生日祝福邮件模板'
            )

            # 设置为默认
            if db.db_type == 'sqlite':
                db._execute("UPDATE email_templates SET is_default = 1 WHERE name = 'default'")
            else:
                db._execute("UPDATE email_templates SET is_default = 1 WHERE name = 'default'")
            db.conn.commit()

            print("✅ 已初始化默认邮件模板")

    finally:
        db.close()


# 测试代码
if __name__ == "__main__":
    # 初始化模板
    init_default_templates()

    # 测试渲染
    tpl = EmailTemplate()
    result = tpl.preview('default')
    print("主题:", result['subject'])
    print("HTML预览:", result['html'][:200])
