import uuid


class Configuration:
    # 每一个连接独享的配置
    def __init__(self, thread_index: int):
        self.is_first_time: bool = True
        self.uuid: str = str(uuid.uuid3(uuid.NAMESPACE_OID, str(thread_index)))
