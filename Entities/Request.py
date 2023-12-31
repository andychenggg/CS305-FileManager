class Request:
    # content_type = "Content-Type"
    # content_length = "Content-Length"
    # Connection = "Connection"
    # set_cookie = "Set-Cookie"
    # cookie = "Cookie"
    # www_authentication = "WWW-Authentication"
    # authorization = "Authorization"
    # transfer_encoding = "Transfer-Encoding"
    # Range = "Range"
    # content_range = " Content-Range"

    def __init__(self, request_str: bytes):
        self.method: str = ""
        self.path: str = ""
        self.file_path: str = ""
        self.http_version: str = ""
        self.headers: dict = {}
        self.data: str = ""
        self.upload_data: bytes = b''
        self._parse_request(request_str)
        self.paras_dict = {}


    def arg_path_para(self):
        """
        解析 URL 中的查询参数（Query Parameters）并将它们存储在字典中。
        这个函数首先检查 URL 路径（self.path）中是否包含 '?' 字符，如果包含，则提取 '?' 后面的部分作为参数字符串。
        然后，它会根据 '&' 字符分割参数字符串，进一步将每个参数根据 '=' 分割为键（key）和值（value）。
        这些键值对被存储在 self.paras_dict 字典中。如果 '=' 后没有值，则相应的字典值为空字符串。

        注意：这个函数不返回任何值，而是直接修改类实例的 self.paras_dict 字典。
            同时该函数仅会在 self.paras_dict 为空时执行。

        @param self: 类实例的引用，用于访问和修改类的成员变量。
        """
        if len(self.paras_dict) != 0:
            return
        split_index = self.path.find('?')
        if split_index == -1:
            self.file_path = self.path
        else:
            params_str = self.path[split_index + 1:]
            self.file_path = self.path[:split_index]
            params = params_str.split('&')
            for para in params:
                key_value = para.split('=', 1)
                if len(key_value) == 2:
                    self.paras_dict[key_value[0].lower()] = key_value[1]
                else:
                    self.paras_dict[key_value[0].lower()] = ''

    def _parse_request(self, request_str: bytes):

        # Split request into lines
        lines = request_str.split(b'\r\n')

        # Parse request line
        request_line = lines[0]
        self.method, self.path, self.http_version = request_line.decode('utf-8').split()

        # Separate headers and body
        headers_section, _, body_section = request_str.partition(b'\r\n\r\n')

        # Parse headers, 所有headers的键已经全部转化为小写
        headers_lines = headers_section.decode('utf-8').split('\r\n')[1:]  # Skip the request line
        for line in headers_lines:
            key, value = line.split(': ', 1)
            self.headers[key.lower()] = value

        # Parse body (data)
        try:
            self.data = body_section.decode('utf-8')
            self.upload_data = body_section
        except UnicodeDecodeError:
            self.upload_data = body_section


