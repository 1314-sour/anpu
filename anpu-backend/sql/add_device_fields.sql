-- 添加设备表缺失字段
ALTER TABLE devices
ADD COLUMN image_url VARCHAR(500) DEFAULT '' COMMENT '设备图片URL',
ADD COLUMN latitude DECIMAL(10, 6) DEFAULT NULL COMMENT '纬度',
ADD COLUMN longitude DECIMAL(10, 6) DEFAULT NULL COMMENT '经度',
ADD COLUMN coordinate_type ENUM('西', '东') DEFAULT '东' COMMENT '坐标分类',
ADD COLUMN top_order_unit ENUM('默示', '隐藏') DEFAULT '默示' COMMENT '顶部菜单栏',
ADD COLUMN default_value_type ENUM('自定义', '集后采集值') DEFAULT '自定义' COMMENT '缺错值类型',
ADD COLUMN default_value VARCHAR(100) DEFAULT '0' COMMENT '缺错值',
ADD COLUMN device_number VARCHAR(100) DEFAULT '' COMMENT '设备编号',
ADD COLUMN manufacture_date DATE DEFAULT NULL COMMENT '出厂日期',
ADD COLUMN install_date DATE DEFAULT NULL COMMENT '安装日期',
ADD COLUMN warranty_years VARCHAR(50) DEFAULT '' COMMENT '保修年限',
ADD COLUMN warranty_unit ENUM('年', '月') DEFAULT '年' COMMENT '保修单位',
ADD COLUMN manufacturer VARCHAR(200) DEFAULT '' COMMENT '生产厂商';
