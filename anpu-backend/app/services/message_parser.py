def parse_hex_data(hex_str: str):
    """
    解析 Modbus 风格的十六进制报文
    例：01030E00130000004600000001000100A225
    """
    try:
        hex_str = hex_str.strip()

        # 最少要有：地址1字节 + 功能码1字节 + 长度1字节 + CRC2字节
        if len(hex_str) < 10:
            return []

        # 去掉前3字节（01 03 0E）和最后2字节CRC
        payload = hex_str[6:-4]

        values = []
        for i in range(0, len(payload), 4):
            chunk = payload[i:i + 4]
            if len(chunk) == 4:
                values.append(int(chunk, 16))

        return values

    except Exception as e:
        print("❌ 解析报文失败:", e)
        return []