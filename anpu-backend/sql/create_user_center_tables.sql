-- 用户中心相关表

-- 1. 用户资料扩展表(补充users表)
CREATE TABLE IF NOT EXISTS user_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT NOT NULL COMMENT '用户ID',
    contact_person VARCHAR(50) COMMENT '联系人',
    address VARCHAR(255) COMMENT '详细地址',
    phone VARCHAR(20) COMMENT '手机号',
    security_question_set BOOLEAN DEFAULT FALSE COMMENT '是否设置密保问题',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户资料扩展表';

-- 2. 系统设置表
CREATE TABLE IF NOT EXISTS user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT NOT NULL COMMENT '用户ID',
    message_types JSON COMMENT '接收消息类型 ["保留消息","工单消息","到期提醒","系统公告"]',
    notify_types JSON COMMENT '消息提醒方式 ["弹窗提醒","声音提醒","浏览器标签闪烁"]',
    layout_type VARCHAR(20) DEFAULT '原始比例' COMMENT '组态页面排版',
    kg_display VARCHAR(20) DEFAULT '列表展示' COMMENT 'KG信息展示',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    UNIQUE KEY uk_user_id (user_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户系统设置表';

-- 3. 操作日志表
CREATE TABLE IF NOT EXISTS operation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT NOT NULL COMMENT '操作用户ID',
    account VARCHAR(50) NOT NULL COMMENT '操作账号',
    object VARCHAR(100) COMMENT '操作对象',
    type VARCHAR(50) NOT NULL COMMENT '操作类型',
    content TEXT COMMENT '操作内容',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '操作时间',
    INDEX idx_user_id (user_id),
    INDEX idx_account (account),
    INDEX idx_type (type),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='操作日志表';

-- 4. 意见反馈表
CREATE TABLE IF NOT EXISTS user_feedbacks (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    user_id INT NOT NULL COMMENT '用户ID',
    type VARCHAR(20) NOT NULL COMMENT '反馈类型: function-功能问题, suggestion-优化建议, other-其他',
    content TEXT NOT NULL COMMENT '反馈内容',
    status VARCHAR(20) DEFAULT 'pending' COMMENT '处理状态: pending-待处理, processing-处理中, resolved-已解决',
    reply TEXT COMMENT '回复内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_user_id (user_id),
    INDEX idx_type (type),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='意见反馈表';

-- 为已有用户创建默认数据
INSERT INTO user_profiles (user_id, phone) 
SELECT id, '' FROM users WHERE id NOT IN (SELECT user_id FROM user_profiles);

INSERT INTO user_settings (user_id, message_types, notify_types) 
SELECT id, 
    '["保留消息","工单消息","到期提醒","系统公告"]',
    '["弹窗提醒","浏览器标签闪烁"]'
FROM users WHERE id NOT IN (SELECT user_id FROM user_settings);
