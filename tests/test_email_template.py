# -*- coding: utf-8 -*-
"""
邮件模板单元测试
"""

import unittest
import os
import tempfile
from email_template import EmailTemplate, init_default_templates
from db_manager import DBManager


class TestEmailTemplate(unittest.TestCase):
    """邮件模板测试"""

    def setUp(self):
        """每个测试前的设置"""
        # 创建临时数据库
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')

        # 修改配置使用临时数据库
        from config import Config
        self.original_db_path = Config.DB_SQLITE_PATH
        Config.DB_SQLITE_PATH = self.db_path

        # 初始化数据库
        init_default_templates()

        self.tpl = EmailTemplate()

    def tearDown(self):
        """每个测试后的清理"""
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_default_template_exists(self):
        """测试默认模板存在"""
        template = self.tpl.get_template('default')
        self.assertIsNotNone(template)
        self.assertEqual(template['name'], 'default')

    def test_render_template(self):
        """测试模板渲染"""
        variables = {
            'name': '张三',
            'wish': '生日快乐！',
            'from_name': '测试助手',
            'year': '2024'
        }

        result = self.tpl.render('default', variables)

        self.assertIn('张三', result['subject'])
        self.assertIn('张三', result['html'])
        self.assertIn('生日快乐！', result['html'])

    def test_render_with_variables(self):
        """测试变量替换"""
        variables = {
            'name': '李四',
            'wish': '祝你生日快乐！',
            'from_name': '系统',
            'year': '2025',
            'age': '30'
        }

        result = self.tpl.render('default', variables)

        self.assertIn('李四', result['html'])
        self.assertIn('祝你生日快乐！', result['html'])

    def test_preview(self):
        """测试预览功能"""
        preview = self.tpl.preview('default')

        self.assertIn('subject', preview)
        self.assertIn('html', preview)
        self.assertIn('text', preview)

    def test_validate_valid_template(self):
        """测试验证有效模板"""
        valid_template = """
        <html>
        <body>
            <h1>你好 {name}</h1>
            <p>{wish}</p>
        </body>
        </html>
        """

        errors = self.tpl.validate_template(valid_template)
        self.assertEqual(len(errors), 0)

    def test_validate_missing_name(self):
        """测试验证缺少name变量"""
        invalid_template = """
        <html>
        <body>
            <h1>你好</h1>
            <p>{wish}</p>
        </body>
        </html>
        """

        errors = self.tpl.validate_template(invalid_template)
        self.assertTrue(any('name' in e for e in errors))

    def test_validate_missing_wish(self):
        """测试验证缺少wish变量"""
        invalid_template = """
        <html>
        <body>
            <h1>你好 {name}</h1>
            <p>欢迎</p>
        </body>
        </html>
        """

        errors = self.tpl.validate_template(invalid_template)
        self.assertTrue(any('wish' in e for e in errors))

    def test_list_templates(self):
        """测试列出模板"""
        templates = self.tpl.list_templates()
        self.assertGreater(len(templates), 0)

    def test_create_template(self):
        """测试创建模板"""
        result = self.tpl.create_template(
            name='test_template',
            title='测试模板',
            subject='测试 {name}',
            html_template='<html><body>{name} - {wish}</body></html>',
            description='测试用模板'
        )

        self.assertTrue(result)

        # 验证模板已创建
        template = self.tpl.get_template('test_template')
        self.assertIsNotNone(template)

    def test_update_template(self):
        """测试更新模板"""
        # 先创建一个模板
        self.tpl.create_template(
            name='update_test',
            title='原标题',
            subject='原主题',
            html_template='<p>{name}</p>'
        )

        # 获取模板ID
        template = self.tpl.get_template('update_test')

        # 更新模板
        result = self.tpl.update_template(
            template['id'],
            title='新标题',
            subject='新主题'
        )

        self.assertTrue(result)

        # 验证更新
        updated = self.tpl.get_template_by_id(template['id'])
        self.assertEqual(updated['title'], '新标题')

    def test_delete_template(self):
        """测试删除模板"""
        # 创建模板
        self.tpl.create_template(
            name='delete_test',
            title='待删除',
            subject='测试',
            html_template='<p>{name}</p>'
        )

        # 获取模板ID
        template = self.tpl.get_template('delete_test')

        # 删除模板
        result = self.tpl.delete_template(template['id'])
        self.assertTrue(result)

        # 验证删除
        deleted = self.tpl.get_template_by_id(template['id'])
        self.assertIsNone(deleted)

    def test_duplicate_template(self):
        """测试复制模板"""
        result = self.tpl.duplicate_template(
            template_id=1,  # default template
            new_name='copied_template'
        )

        self.assertTrue(result)

        # 验证复制
        copied = self.tpl.get_template('copied_template')
        self.assertIsNotNone(copied)


class TestEmailTemplateRendering(unittest.TestCase):
    """邮件模板渲染测试"""

    def test_text_version_generation(self):
        """测试纯文本版本生成"""
        tpl = EmailTemplate()

        variables = {
            'name': '测试用户',
            'wish': '生日快乐！',
            'from_name': '系统'
        }

        text = tpl._generate_text_version(variables)

        self.assertIn('测试用户', text)
        self.assertIn('生日快乐！', text)
        self.assertIn('系统', text)


if __name__ == '__main__':
    unittest.main()
