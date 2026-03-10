-- 设备详细配置表（扩展devices表）
CREATE TABLE IF NOT EXISTS device_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL UNIQUE COMMENT '设备ID',
    device_model VARCHAR(100) DEFAULT '' COMMENT '设备型号',
    hardware_version VARCHAR(50) DEFAULT '' COMMENT '硬件版本',
    software_version VARCHAR(50) DEFAULT '' COMMENT '软件版本',
    latitude DECIMAL(10, 6) DEFAULT NULL COMMENT '纬度',
    longitude DECIMAL(10, 6) DEFAULT NULL COMMENT '经度',
    coordinate_type ENUM('WGS84', 'GCJ02', 'BD09') DEFAULT 'WGS84' COMMENT '坐标系',
    description TEXT COMMENT '设备描述',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备详细配置表';

-- 网关驱动表
CREATE TABLE IF NOT EXISTS device_drivers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL COMMENT '设备ID',
    driver_name VARCHAR(100) NOT NULL COMMENT '驱动名称',
    protocol VARCHAR(50) NOT NULL COMMENT '协议类型（Modbus RTU/TCP等）',
    port VARCHAR(50) DEFAULT '' COMMENT '网络端口',
    baud_rate INT DEFAULT NULL COMMENT '波特率',
    data_bits INT DEFAULT 8 COMMENT '数据位',
    stop_bits INT DEFAULT 1 COMMENT '停止位',
    parity ENUM('无校验', '奇校验', '偶校验') DEFAULT '无校验' COMMENT '校验位',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='网关驱动表';

-- 变量管理表
CREATE TABLE IF NOT EXISTS device_variables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL COMMENT '设备ID',
    var_name VARCHAR(100) NOT NULL COMMENT '变量名称',
    slave_address INT NOT NULL COMMENT '从站地址',
    data_type VARCHAR(50) NOT NULL COMMENT '数据类型',
    register_type VARCHAR(50) NOT NULL COMMENT '寄存器类型',
    `read_write` VARCHAR(20) NOT NULL COMMENT '读写类型',
    address VARCHAR(50) NOT NULL COMMENT '地址',
    key_name VARCHAR(50) DEFAULT '' COMMENT '键值(key)',
    driver_name VARCHAR(100) DEFAULT '' COMMENT '网关驱动',
    collect_mode VARCHAR(50) DEFAULT '非边缘采集' COMMENT '采集方式',
    sort_order INT DEFAULT 0 COMMENT '排序',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备变量表';

-- 历史报表管理表
CREATE TABLE IF NOT EXISTS device_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL COMMENT '设备ID',
    report_name VARCHAR(100) NOT NULL COMMENT '报表名称',
    report_type VARCHAR(50) NOT NULL COMMENT '报表类型',
    variable_count INT DEFAULT 0 COMMENT '关联变量数量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='历史报表表';

-- 报告管理表
CREATE TABLE IF NOT EXISTS device_alarms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    device_id INT NOT NULL COMMENT '设备ID',
    alarm_name VARCHAR(100) NOT NULL COMMENT '报告名称',
    resolution VARCHAR(50) DEFAULT '' COMMENT '分辨率',
    page_type VARCHAR(50) DEFAULT '' COMMENT '页面类型',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE,
    INDEX idx_device_id (device_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='报告管理表';

-- 插入测试数据
-- 假设设备ID=1的设备已存在

-- 设备详细配置测试数据
INSERT INTO device_configs (device_id, device_model, hardware_version, software_version, latitude, longitude, coordinate_type, description) VALUES
(1, 'AMP-119A3', 'v1.0', 'v1.0.35', 31.761356, 119.959886, 'WGS84', '测试设备详细配置');

-- 网关驱动测试数据
INSERT INTO device_drivers (device_id, driver_name, protocol, port, baud_rate, data_bits, stop_bits, parity) VALUES
(1, 'AMP-119A3', 'Modbus RTU', 'RS485', 9600, 8, 1, '无校验');

-- 变量管理测试数据
INSERT INTO device_variables (device_id, var_name, slave_address, data_type, register_type, `read_write`, address, key_name, driver_name, collect_mode, sort_order) VALUES
(1, '工作状态', 1, '16位整型(无符号)', '保持寄存器(4x)', '只读', '1', '', 'AMP-119A3', '非边缘采集', 1),
(1, '自检时间-分', 10, '16位整型(无符号)', '保持寄存器(4x)', '读写', '10', '', 'AMP-119A3', '非边缘采集', 10),
(1, '自检时间-时', 9, '16位整型(无符号)', '保持寄存器(4x)', '读写', '9', '', 'AMP-119A3', '非边缘采集', 9),
(1, '故障中5-备号', 8, '16位整型(无符号)', '保持寄存器(4x)', '只读', '8', '', 'AMP-119A3', '非边缘采集', 8),
(1, '故障中4-水短板', 7, '16位整型(无符号)', '保持寄存器(4x)', '只读', '7', '', 'AMP-119A3', '非边缘采集', 7),
(1, '故障中3-液位故障', 6, '16位整型(无符号)', '保持寄存器(4x)', '只读', '6', '', 'AMP-119A3', '非边缘采集', 6);

-- 历史报表测试数据
INSERT INTO device_reports (device_id, report_name, report_type, variable_count) VALUES
(1, '火花探测计数', '周期积累', 1);

-- 报告管理测试数据  
INSERT INTO device_alarms (device_id, alarm_name, resolution, page_type) VALUES
(1, '组态画面', '1920 x 1080', '主页面');
