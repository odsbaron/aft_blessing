# -*- coding: utf-8 -*-
"""
输入验证模块
提供各种输入数据的验证功能
"""

import re
from datetime import datetime
from functools import wraps
from flask import request, jsonify


class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message, field=None):
        self.message = message
        self.field = field
        super().__init__(message)


class Validators:
    """输入验证器"""

    # 邮箱验证正则
    EMAIL_REGEX = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    # 用户名验证（允许中文、字母、数字、下划线）
    USERNAME_REGEX = re.compile(
        r'^[\u4e00-\u9fa5a-zA-Z0-9_]{2,20}$'
    )

    # 日期格式验证
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y.%m.%d'
    ]

    @staticmethod
    def validate_email(email):
        """验证邮箱格式"""
        if not email:
            raise ValidationError("邮箱不能为空", "email")
        if not Validators.EMAIL_REGEX.match(email):
            raise ValidationError("邮箱格式不正确", "email")
        if len(email) > 100:
            raise ValidationError("邮箱长度不能超过100字符", "email")
        return email.lower().strip()

    @staticmethod
    def validate_username(username):
        """验证用户名格式"""
        if not username:
            raise ValidationError("用户名不能为空", "username")
        if not Validators.USERNAME_REGEX.match(username):
            raise ValidationError("用户名只能包含中文、字母、数字、下划线，长度2-20位", "username")
        return username.strip()

    @staticmethod
    def validate_date(date_str):
        """验证日期格式和有效性"""
        if not date_str:
            raise ValidationError("日期不能为空", "dob")

        # 尝试各种日期格式
        for fmt in Validators.DATE_FORMATS:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                # 检查日期合理性（不能是未来）
                if date_obj > datetime.now():
                    raise ValidationError("出生日期不能是未来日期", "dob")
                # 检查年份不能太早
                if date_obj.year < 1900:
                    raise ValidationError("出生日期年份不能早于1900年", "dob")
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue

        raise ValidationError("日期格式不正确，请使用 YYYY-MM-DD 格式", "dob")

    @staticmethod
    def validate_text(text, field_name, max_length=500, min_length=1, required=True):
        """验证文本输入"""
        if required and not text:
            raise ValidationError(f"{field_name}不能为空", field_name)

        text = text.strip() if text else ""

        if min_length and len(text) < min_length:
            raise ValidationError(f"{field_name}长度至少需要{min_length}个字符", field_name)

        if max_length and len(text) > max_length:
            raise ValidationError(f"{field_name}长度不能超过{max_length}个字符", field_name)

        return text

    @staticmethod
    def validate_wish_content(content):
        """验证祝福语内容"""
        return Validators.validate_text(
            content,
            "祝福语",
            max_length=500,
            min_length=5,
            required=True
        )

    @staticmethod
    def validate_id(user_id, field_name="id"):
        """验证ID参数"""
        try:
            user_id = int(user_id)
            if user_id <= 0:
                raise ValidationError(f"{field_name}必须是正整数", field_name)
            return user_id
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}格式不正确", field_name)

    @staticmethod
    def sanitize_html(text):
        """基础的HTML清理（防止XSS）"""
        if not text:
            return ""

        # 移除危险的HTML标签
        dangerous_tags = ['<script', '</script', '<iframe', '</iframe', '<object', '</object']
        for tag in dangerous_tags:
            text = text.replace(tag, '')

        return text


def validate_json_payload(required_fields=None, optional_fields=None):
    """
    JSON请求数据验证装饰器

    Args:
        required_fields: 必需字段列表 {field_name: validator_function}
        optional_fields: 可选字段列表 {field_name: validator_function}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': '请求必须是JSON格式'}), 400

            data = request.get_json()
            if not data:
                return jsonify({'error': '请求体不能为空'}), 400

            errors = {}

            # 验证必需字段
            if required_fields:
                for field, validator in required_fields.items():
                    try:
                        if field not in data:
                            errors[field] = f"{field}是必需的"
                        else:
                            data[field] = validator(data[field])
                    except ValidationError as e:
                        errors[field] = e.message

            # 验证可选字段
            if optional_fields and not errors:
                for field, validator in optional_fields.items():
                    if field in data:
                        try:
                            data[field] = validator(data[field])
                        except ValidationError as e:
                            errors[field] = e.message

            if errors:
                return jsonify({'error': '验证失败', 'errors': errors}), 400

            return f(data=data, *args, **kwargs)

        return decorated_function
    return decorator


def validate_form_data(required_fields=None, optional_fields=None):
    """
    表单数据验证装饰器

    Args:
        required_fields: 必需字段列表 {field_name: validator_function}
        optional_fields: 可选字段列表 {field_name: validator_function}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = {}
            validated_data = {}

            # 验证必需字段
            if required_fields:
                for field, validator in required_fields.items():
                    value = request.form.get(field, '').strip()
                    try:
                        if not value:
                            errors[field] = f"{field}是必需的"
                        else:
                            validated_data[field] = validator(value)
                    except ValidationError as e:
                        errors[field] = e.message

            # 验证可选字段
            if optional_fields and not errors:
                for field, validator in optional_fields.items():
                    value = request.form.get(field, '').strip()
                    if value:
                        try:
                            validated_data[field] = validator(value)
                        except ValidationError as e:
                            errors[field] = e.message

            if errors:
                # 将错误存储以便在模板中显示
                from flask import flash
                for field, error in errors.items():
                    flash(error, 'error')
                # 如果是GET请求通常返回模板，POST请求则返回
                return f(*args, **kwargs)

            # 将验证后的数据合并到request.form中
            request.validated_data = validated_data

            return f(*args, **kwargs)

        return decorated_function
    return decorator


# 预定义的验证器
def validate_email_field(value):
    """邮箱字段验证器"""
    return Validators.validate_email(value)


def validate_username_field(value):
    """用户名字段验证器"""
    return Validators.validate_username(value)


def validate_date_field(value):
    """日期字段验证器"""
    return Validators.validate_date(value)


def validate_text_field(max_length=500, min_length=1, required=True):
    """文本字段验证器工厂"""
    def validator(value):
        return Validators.validate_text(
            value,
            "内容",
            max_length=max_length,
            min_length=min_length,
            required=required
        )
    return validator


if __name__ == "__main__":
    # 测试
    try:
        print(Validators.validate_email("test@example.com"))
        print(Validators.validate_username("张三"))
        print(Validators.validate_date("1990-01-01"))
        print(Validators.validate_wish_content("生日快乐！祝你天天开心！"))
        print(Validators.validate_id("123"))
    except ValidationError as e:
        print(f"验证错误: {e.message} (字段: {e.field})")
