from backend.infrastructure.database import db
from backend.models.student_extension import StudentExtension
from backend.models.student import Student
import sys
import os

# 获取当前脚本的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录路径（假设脚本在 scripts/ 目录下）
project_root = os.path.dirname(script_dir)
# 将项目根目录添加到 Python 路径
sys.path.append(project_root)

# 然后再导入其他模块


def create_test_students(num=100):
    for i in range(1, num+1):
        # 创建学生基本信息
        student = Student(
            education_id=f"E{i:04d}",
            name=f"测试学生{i}",
            gender="男" if i % 2 == 0 else "女",
            school="测试学校",
            class_name=f"{i%10+1}班"
        )
        db.session.add(student)
        db.session.commit()

        # 创建学生扩展信息
        extension = StudentExtension(
            student_id=student.id,
            data_year="2023",
            age=10 + i % 5,  # 年龄范围 10-14 岁
            vision_level="临床前期近视" if i % 3 == 0 else "轻度近视"
        )
        db.session.add(extension)
    db.session.commit()
    print(f"成功生成 {num} 条测试数据")


if __name__ == "__main__":
    create_test_students(num=50)  # 生成 50 条测试数据
