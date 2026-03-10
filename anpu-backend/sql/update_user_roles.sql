-- 用户角色迁移SQL脚本
-- 将原有的 admin/user 角色迁移为新的四种角色
-- 新角色: super_admin(超级管理员), anpu_staff(安普员工), enterprise_admin(企业管理员), enterprise_staff(企业员工)

-- 1. 首先修改role字段长度以支持新的角色名称
ALTER TABLE users MODIFY COLUMN role VARCHAR(30) DEFAULT 'enterprise_staff';

-- 2. 将原有的admin角色迁移为super_admin（超级管理员）
UPDATE users SET role = 'super_admin' WHERE role = 'admin';

-- 3. 将原有的user角色迁移为enterprise_staff（企业员工）
UPDATE users SET role = 'enterprise_staff' WHERE role = 'user';

-- 4. 验证迁移结果
SELECT role, COUNT(*) as count FROM users GROUP BY role;

-- 注意事项:
-- 1. 执行此脚本前请先备份数据库
-- 2. 如果需要创建不同角色的测试用户，可以使用以下SQL：
/*
-- 创建超级管理员账号 (密码需要使用bcrypt加密后的值)
INSERT INTO users (username, email, hashed_password, nickname, role, is_active)
VALUES ('superadmin', 'superadmin@anpu.com', '$2b$12$...', '超级管理员', 'super_admin', 1);

-- 创建安普员工账号
INSERT INTO users (username, email, hashed_password, nickname, role, is_active)
VALUES ('anpustaff', 'staff@anpu.com', '$2b$12$...', '安普员工', 'anpu_staff', 1);

-- 创建企业管理员账号
INSERT INTO users (username, email, hashed_password, nickname, role, is_active)
VALUES ('enterpriseadmin', 'admin@enterprise.com', '$2b$12$...', '企业管理员', 'enterprise_admin', 1);

-- 创建企业员工账号
INSERT INTO users (username, email, hashed_password, nickname, role, is_active)
VALUES ('enterprisestaff', 'staff@enterprise.com', '$2b$12$...', '企业员工', 'enterprise_staff', 1);
*/
