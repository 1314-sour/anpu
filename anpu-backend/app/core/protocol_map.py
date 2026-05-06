PROTOCOL_FIELDS = [
    {
        "key": "work_status",
        "name": "工作状态",
        "register_address": "0001H",
        "index": 0,
    },
    {
        "key": "probe_no",
        "name": "报警编号",
        "register_address": "0003H",
        "index": 2,
    },
    {
        "key": "comm_address",
        "name": "通讯地址",
        "register_address": "0005H",
        "index": 4,
    },
    {
        "key": "baud_rate",
        "name": "波特率",
        "register_address": "0006H",
        "index": 5,
    },
    {
        "key": "version",
        "name": "版本号",
        "register_address": "0007H",
        "index": 6,
    },
]


NAME_KEY_MAP = {
    "工作状态": "work_status",
    "报警编号": "probe_no",
    "通讯地址": "comm_address",
    "波特率": "baud_rate",
    "版本号": "version",
}


def build_parsed_map(values: list[int]) -> dict:
    result = {}

    for field in PROTOCOL_FIELDS:
        key = field["key"]
        index = field["index"]
        result[key] = values[index] if index < len(values) else None

    return result