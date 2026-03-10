-- 创建设备分组表
CREATE TABLE IF NOT EXISTS device_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL COMMENT '分组名称',
    parent_id INT DEFAULT 0 COMMENT '父级分组ID，0表示顶层',
    user_id INT NOT NULL COMMENT '创建人ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_parent_id (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备分组表';

-- 创建设备表
CREATE TABLE IF NOT EXISTS devices (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL COMMENT '设备名称',
    sn VARCHAR(100) NOT NULL UNIQUE COMMENT '网关SN编号',
    status ENUM('online', 'offline') DEFAULT 'offline' COMMENT '网关状态',
    group_id INT DEFAULT NULL COMMENT '所属分组ID',
    address VARCHAR(500) DEFAULT '' COMMENT '所在地址',
    creator_id INT NOT NULL COMMENT '创建人ID',
    remark TEXT COMMENT '备注',
    iccid VARCHAR(50) DEFAULT '' COMMENT 'ICCID',
    sort INT DEFAULT 0 COMMENT '排序号',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES device_groups(id) ON DELETE SET NULL,
    INDEX idx_creator_id (creator_id),
    INDEX idx_group_id (group_id),
    INDEX idx_status (status),
    INDEX idx_sn (sn)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='设备表';

-- 插入测试分组数据
INSERT INTO device_groups (name, parent_id, user_id) VALUES
('默认', 0, 1),
('后纺', 0, 1),
('前纺', 0, 1),
('测试分组', 0, 1);

-- 插入测试设备数据
INSERT INTO devices (name, sn, status, group_id, address, creator_id, remark, sort) VALUES
('AMP-119A(V2)无线报警', '300121111074', 'offline', NULL, '江苏省常州市新北区太湖东路9-1号常州安普', 1, '测试设备1', 0),
('CLC-16R', '110122061135', 'offline', NULL, '', 1, '', 0),
('AMP-174A II.v21流量', '300122071601', 'online', 2, '常州新北区太湖东路9-1号常州安普-西门', 1, '', 10),
('AMP-2000.v21流量', '200121051043', 'online', 2, '常州市新北区太湖东路9-1号常州安普-北门', 1, '', 20),
('AMP-EE01.v21流量报警', '300121051042', 'online', 3, '常州新北区太湖东路9-1号常州安普-东门', 1, '', 5),
('AMP-119F一楼环境温湿度', '200123051025', 'online', 2, '', 1, '', 0),
('AMP-119F一楼南打包区', '200123051020', 'online', 2, '', 1, '', 0),
('AMP-119F一楼北打包区1', '200123051009', 'online', 3, '', 1, '', 0),
('AMP-119F一楼北打包区2', '200123051008', 'online', 3, '', 1, '', 0),
('AMP-119F一楼南侧污绵', '200123051045', 'online', 3, '', 1, '', 0);
