-- 删除SN字段的唯一索引，允许多个设备在创建时SN为空
-- SN应该在网关绑定时才填写

ALTER TABLE devices DROP INDEX ix_devices_sn;

-- 如果需要，可以添加普通索引（非唯一）
-- ALTER TABLE devices ADD INDEX idx_devices_sn (sn);
