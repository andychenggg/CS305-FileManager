from __future__ import annotations

import uuid
from Functions.Https.KeysManager import KeyManager


class Configuration:
    # 每一个连接独享的配置
    def __init__(self, thread_index: int):
        self.is_first_time: bool = True
        self.keysMan: KeyManager | None = None  # 如果不是None，意味着https启动！
        self.user: str | None = None
        self.password: str | None = None
