-- 变量管理表字段升级 v2
-- 新增字段：description, variable_type, driver_id, cycle_collect, collect_interval, unit, min_value, max_value, default_value, expression
-- 修改字段：slave_address 允许 NULL, register_type 允许 NULL, address 允许 NULL

-- 1. 新增字段
ALTER TABLE device_variables
    ADD COLUMN IF NOT EXISTS description VARCHAR(255) DEFAULT '' COMMENT '变量描述' AFTER var_name,
    ADD COLUMN IF NOT EXISTS variable_type VARCHAR(20) DEFAULT 'device' COMMENT '变量类型: device/middle/internal' AFTER description,
    ADD COLUMN IF NOT EXISTS driver_id INT DEFAULT NULL COMMENT '关联驱动ID' AFTER key_name,
    ADD COLUMN IF NOT EXISTS cycle_collect TINYINT DEFAULT 1 COMMENT '周期采集: 1=开启 0=关闭' AFTER driver_name,
    ADD COLUMN IF NOT EXISTS collect_interval INT DEFAULT 1000 COMMENT '采集周期(毫秒)' AFTER cycle_collect,
    ADD COLUMN IF NOT EXISTS unit VARCHAR(20) DEFAULT '' COMMENT '单位' AFTER collect_mode,
    ADD COLUMN IF NOT EXISTS min_value DECIMAL(15,4) DEFAULT NULL COMMENT '量程下限' AFTER unit,
    ADD COLUMN IF NOT EXISTS max_value DECIMAL(15,4) DEFAULT NULL COMMENT '量程上限' AFTER min_value,
    ADD COLUMN IF NOT EXISTS default_value VARCHAR(100) DEFAULT '' COMMENT '默认值' AFTER max_value,
    ADD COLUMN IF NOT EXISTS expression VARCHAR(500) DEFAULT '' COMMENT '计算表达式(中间变量用)' AFTER default_value;

-- 2. 修改允许NULL的字段
ALTER TABLE device_variables
    MODIFY COLUMN slave_address INT DEFAULT 0 COMMENT '从站地址',
    MODIFY COLUMN register_type VARCHAR(50) DEFAULT 'holding_register' COMMENT '寄存器类型',
    MODIFY COLUMN address VARCHAR(50) DEFAULT '' COMMENT '地址';

-- 3. 添加外键（如果不存在）
-- ALTER TABLE device_variables ADD CONSTRAINT fk_var_driver FOREIGN KEY (driver_id) REFERENCES device_drivers(id) ON DELETE SET NULL;

-- 4. 添加索引
CREATE INDEX IF NOT EXISTS idx_var_type ON device_variables(variable_type);
CREATE INDEX IF NOT EXISTS idx_var_driver_id ON device_variables(driver_id);
