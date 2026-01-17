# -*- coding: utf-8 -*-
"""
用户批量导入脚本
支持从 CSV/Excel 文件批量导入用户数据
"""

import pandas as pd
import sys
import os
from datetime import datetime
from db_manager import DBManager


def normalize_date(date_str):
    """将各种日期格式统一为 YYYY-MM-DD"""
    date_str = str(date_str).strip()

    # 支持的日期格式
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y.%m.%d']

    # 先尝试标准格式
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except:
            continue

    # 处理个位数月份/日期的情况 (如 2003/1/17)
    try:
        date_str = date_str.replace('/', '-').replace('.', '-')
        parts = date_str.split('-')
        if len(parts) == 3:
            year, month, day = parts
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    except:
        pass

    raise ValueError(f"无法解析日期: {date_str}")


def import_from_csv(file_path):
    """
    从 CSV 文件导入用户

    Args:
        file_path: CSV 文件路径

    Returns:
        dict: 导入结果统计
    """
    print(f"📂 正在读取文件: {file_path}")

    try:
        # 读取 CSV 文件
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            df = pd.read_csv(file_path, encoding='gbk')
        except Exception as e:
            return {'success': False, 'error': f"文件编码错误: {e}"}
    except Exception as e:
        return {'success': False, 'error': f"读取文件失败: {e}"}

    # 验证必要的列
    required_columns = ['name', 'email', 'dob']
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return {
            'success': False,
            'error': f"CSV 缺少必要列: {', '.join(missing)}\n需要的列: {', '.join(required_columns)}"
        }

    print(f"✅ 文件读取成功，共 {len(df)} 条记录\n")

    # 导入数据
    db = DBManager()
    success_count = 0
    skip_count = 0
    error_list = []

    try:
        for idx, row in df.iterrows():
            try:
                name = str(row['name']).strip()
                email = str(row['email']).strip()
                dob = str(row['dob']).strip()

                # 验证邮箱格式
                if '@' not in email:
                    error_list.append(f"第 {idx+2} 行: 无效的邮箱地址 - {email}")
                    skip_count += 1
                    continue

                # 验证并规范化日期格式
                try:
                    dob = normalize_date(dob)
                except Exception as e:
                    error_list.append(f"第 {idx+2} 行: 无效的日期格式 - {dob}")
                    skip_count += 1
                    continue

                # 插入数据库
                if db.add_user(name, email, dob):
                    success_count += 1
                    print(f"✅ [{success_count}] {name} - {email}")
                else:
                    skip_count += 1
                    print(f"⏭️  [跳过] {email} (已存在)")

            except Exception as e:
                skip_count += 1
                error_list.append(f"第 {idx+2} 行: {str(e)}")

    finally:
        db.close()

    # 输出结果
    print("\n" + "=" * 50)
    print("📊 导入完成:")
    print(f"   ✅ 成功: {success_count} 条")
    print(f"   ⏭️  跳过: {skip_count} 条")
    print(f"   ❌ 错误: {len(error_list)} 条")

    if error_list:
        print("\n❌ 错误详情:")
        for error in error_list[:10]:  # 只显示前10条
            print(f"   {error}")
        if len(error_list) > 10:
            print(f"   ... 还有 {len(error_list)-10} 条错误")

    print("=" * 50)

    return {
        'success': True,
        'total': len(df),
        'success_count': success_count,
        'skip_count': skip_count,
        'error_count': len(error_list)
    }


def import_from_excel(file_path):
    """
    从 Excel 文件导入用户

    Args:
        file_path: Excel 文件路径

    Returns:
        dict: 导入结果统计
    """
    print(f"📂 正在读取 Excel 文件: {file_path}")

    try:
        # 读取 Excel 文件
        df = pd.read_excel(file_path)
    except Exception as e:
        return {'success': False, 'error': f"读取 Excel 文件失败: {e}"}

    # 将 DataFrame 保存为临时 CSV，然后复用导入逻辑
    temp_csv = file_path.replace('.xlsx', '_temp.csv').replace('.xls', '_temp.csv')
    df.to_csv(temp_csv, index=False, encoding='utf-8')

    try:
        result = import_from_csv(temp_csv)
        return result
    finally:
        # 删除临时文件
        if os.path.exists(temp_csv):
            os.remove(temp_csv)


def create_sample_csv(output_path="users_sample.csv"):
    """创建示例 CSV 文件"""
    sample_data = """name,email,dob
张三,zhangsan@example.com,1995-01-17
李四,lisi@example.com,1998-06-23
王五,wangwu@example.com,1992-12-08
赵六,zhaoliu@example.com,2000-03-15
钱七,qianqi@example.com,1988-09-30"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sample_data)

    print(f"✅ 示例文件已创建: {output_path}")
    print("\n你可以编辑这个文件，然后运行:")
    print(f"  python import_users.py {output_path}")


def main():
    """主入口"""
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║         📋 用户批量导入工具 📋                         ║
    ╚═══════════════════════════════════════════════════════╝
    """)

    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python import_users.py <文件路径>           # 导入用户")
        print("  python import_users.py --sample             # 创建示例文件")
        print("\n支持的文件格式: .csv, .xlsx, .xls")
        print("\nCSV 文件格式要求:")
        print("  name, email, dob")
        print("  张三, zhangsan@example.com, 1995-01-17")
        return

    file_path = sys.argv[1]

    if file_path in ['--sample', '-s', 'sample']:
        # 创建示例文件
        create_sample_csv()
        return

    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return

    # 判断文件类型并导入
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == '.csv':
        result = import_from_csv(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        result = import_from_excel(file_path)
    else:
        print(f"❌ 不支持的文件格式: {file_ext}")
        print("   支持的格式: .csv, .xlsx, .xls")
        return

    # 检查结果
    if result and result.get('success'):
        print("\n🎉 导入完成！")
    elif result and not result.get('success'):
        print(f"\n❌ 导入失败: {result.get('error')}")


if __name__ == "__main__":
    main()
