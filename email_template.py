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

    # 默认模板
    DEFAULT_TEMPLATE = {
        'name': 'default',
        'title': '默认模板',
        'subject': '🎂 {name}，生日快乐！',
        'html_template': """<!DOCTYPE html>
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
            <div class="greeting">亲爱的 {name}</div>
            <div class="decoration">✨ ✨ ✨</div>
            <p class="message">{wish}</p>
            <div class="decoration">✨ ✨ ✨</div>
        </div>
        <div class="footer">
            <p>—— 这是来自 {from_name} 的生日祝福</p>
            <p>这是一封自动发送的邮件，请勿直接回复</p>
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
        return f"""亲爱的 {variables.get('name', '朋友')}：

{variables.get('wish', '生日快乐！')}

✨ ✨ ✨

—— 来自 {variables.get('from_name', '生日祝福助手')} 的生日祝福

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
