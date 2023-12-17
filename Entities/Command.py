class Command:
    def __init__(self):
        self.close_conn = False  # 直接返回，直到关闭连接
        self.resp_imm = False  # 无需往下操作，立刻返回
        self.skip_auth = False  # 跳过验证，因为有正确的cookie
        self.return_pub_key = False  # 返回公钥

        self.chunked = False  # 分块传输
        self.refresh = False # 刷新页面