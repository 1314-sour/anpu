-- 消息表
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL COMMENT '用户ID',
    title VARCHAR(255) NOT NULL COMMENT '消息标题',
    content TEXT COMMENT '消息内容',
    type VARCHAR(50) NOT NULL COMMENT '消息类型:reserved=报警消息,workorder=工单消息,expire=到期提醒,system=系统公告',
    is_read BOOLEAN DEFAULT FALSE COMMENT '是否已读',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    read_at TIMESTAMP NULL COMMENT '阅读时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_type (user_id, type),
    INDEX idx_user_read (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='消息表';

-- 插入测试数据
INSERT INTO messages (user_id, title, content, type, is_read, created_at, read_at) VALUES
-- admin用户的未读消息
(1, 'AMP-119A(V2)测试交易报警', '设备AMP-119A(V2)测试发生交易异常,请及时处理', 'reserved', FALSE, '2025-12-05 14:03:42', NULL),
(1, 'AMP-2000(v2)无线变量报警', '设备AMP-2000(v2)无线变量超出正常范围', 'reserved', FALSE, '2025-12-04 17:10:41', NULL),
(1, '设备到期提醒', '您的设备AMP-119A将于7天后到期,请及时续费', 'expire', FALSE, '2025-12-03 10:00:00', NULL),
(1, '系统维护通知', '系统将于12月10日凌晨2点进行维护,预计2小时', 'system', FALSE, '2025-12-02 09:00:00', NULL),
(1, '工单处理通知', '您提交的工单#12345已被处理', 'workorder', FALSE, '2025-12-01 15:30:00', NULL),

-- admin用户的已读消息  
(1, 'AMP-0331-v21无线变量报警', '设备AMP-0331-v21无线变量异常', 'reserved', TRUE, '2025-11-28 15:20:56', '2025-11-29 10:00:00'),
(1, '新功能上线通知', '平台已上线设备批量管理功能', 'system', TRUE, '2025-11-25 10:00:00', '2025-11-25 14:00:00'),
(1, '工单完成通知', '工单#12340已完成处理', 'workorder', TRUE, '2025-11-20 16:00:00', '2025-11-21 09:00:00'),
(1, '设备续费成功', '设备AMP-2000已成功续费1年', 'expire', TRUE, '2025-11-15 11:00:00', '2025-11-15 11:30:00'),
(1, 'AMP-2000(v2)无线变量报警', '设备AMP-2000(v2)无线变量已恢复正常', 'reserved', TRUE, '2025-11-10 14:46:24', '2025-11-10 15:00:00');
