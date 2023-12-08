class Command:
    def __init__(self):
        self.close_conn = False  # 直接返回，直到关闭连接
        self.resp_imm = False  # 无需往下操作，立刻返回

