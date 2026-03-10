"""
创建四种角色的测试用户
运行方式: python create_role_users.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from sqlalchemy import text
import bcrypt

def get_password_hash(password: str) -> str:
    """获取密码哈希值"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# 角色常量定义
class UserRole:
    SUPER_ADMIN = "super_admin"
    ANPU_STAFF = "anpu_staff"
    ENTERPRISE_ADMIN = "enterprise_admin"
    ENTERPRISE_STAFF = "enterprise_staff"
    
    ROLE_NAMES = {
        SUPER_ADMIN: "超级管理员",
        ANPU_STAFF: "安普员工",
        ENTERPRISE_ADMIN: "企业管理员",
        ENTERPRISE_STAFF: "企业员工",
    }


def create_test_users():
    """创建四种角色的测试用户"""
    db = SessionLocal()
    
    test_users = [
        {
            "username": "superadmin",
            "email": "superadmin@anpu.com",
            "password": "123456",
            "nickname": "超级管理员",
            "role": UserRole.SUPER_ADMIN
        },
        {
            "username": "anpustaff",
            "email": "staff@anpu.com", 
            "password": "123456",
            "nickname": "安普员工",
            "role": UserRole.ANPU_STAFF
        },
        {
            "username": "enterpriseadmin",
            "email": "admin@enterprise.com",
            "password": "123456",
            "nickname": "企业管理员",
            "role": UserRole.ENTERPRISE_ADMIN
        },
        {
            "username": "enterprisestaff",
            "email": "staff@enterprise.com",
            "password": "123456",
            "nickname": "企业员工",
            "role": UserRole.ENTERPRISE_STAFF
        }
    ]
    
    try:
        for user_data in test_users:
            # 使用原生SQL检查用户是否已存在
            result = db.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": user_data["username"]}
            ).fetchone()
            
            hashed_pwd = get_password_hash(user_data["password"])
            
            if result:
                # 更新现有用户的角色
                db.execute(
                    text("UPDATE users SET role = :role, nickname = :nickname WHERE username = :username"),
                    {"role": user_data["role"], "nickname": user_data["nickname"], "username": user_data["username"]}
                )
                print(f"更新用户: {user_data['username']} -> 角色: {user_data['role']}")
            else:
                # 创建新用户
                db.execute(
                    text("""INSERT INTO users (username, email, hashed_password, nickname, role, is_active) 
                            VALUES (:username, :email, :hashed_password, :nickname, :role, 1)"""),
                    {
                        "username": user_data["username"],
                        "email": user_data["email"],
                        "hashed_password": hashed_pwd,
                        "nickname": user_data["nickname"],
                        "role": user_data["role"]
                    }
                )
                print(f"创建用户: {user_data['username']} -> 角色: {user_data['role']}")
        
        db.commit()
        print("\n✓ 测试用户创建/更新完成!")
        print("\n测试账号信息:")
        print("-" * 50)
        print(f"{'用户名':<20} {'角色':<20} {'密码'}")
        print("-" * 50)
        for user in test_users:
            role_name = UserRole.ROLE_NAMES.get(user["role"], user["role"])
            print(f"{user['username']:<20} {role_name:<20} {user['password']}")
        
    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
    finally:
        db.close()


def migrate_existing_users():
    """将现有用户的角色迁移到新角色"""
    db = SessionLocal()
    
    try:
        # 将 admin 角色迁移为 super_admin
        result = db.execute(
            text("UPDATE users SET role = :new_role WHERE role = :old_role"),
            {"new_role": UserRole.SUPER_ADMIN, "old_role": "admin"}
        )
        print(f"已将 admin 用户迁移为 super_admin")
        
        # 将 user 角色迁移为 enterprise_staff
        result = db.execute(
            text("UPDATE users SET role = :new_role WHERE role = :old_role"),
            {"new_role": UserRole.ENTERPRISE_STAFF, "old_role": "user"}
        )
        print(f"已将 user 用户迁移为 enterprise_staff")
        
        db.commit()
        print("\n✓ 用户角色迁移完成!")
        
    except Exception as e:
        db.rollback()
        print(f"错误: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 50)
    print("用户角色系统迁移脚本")
    print("=" * 50)
    
    print("\n1. 迁移现有用户角色...")
    migrate_existing_users()
    
    print("\n2. 创建测试用户...")
    create_test_users()
    
    print("\n" + "=" * 50)
    print("完成!")
