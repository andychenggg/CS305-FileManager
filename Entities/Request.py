from html_package.HTMLManager import HTMLManager
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

    def __init__(self, request_str: str):
        self.method: str = ""
        self.path: str = ""
        self.http_version: str = ""
        self.headers: dict = {}
        self.data: str = ""
        self._parse_request(request_str)

    def _parse_request(self, request_str: str):

        # Split request into lines
        lines = request_str.split('\r\n')

        # Parse request line
        request_line = lines[0]
        self.method, self.path, self.http_version = request_line.split()

        # Separate headers and body
        headers_section, _, body_section = request_str.partition('\r\n\r\n')

        # Parse headers, 所有headers的键已经全部转化为小写
        headers_lines = headers_section.split('\r\n')[1:]  # Skip the request line
        for line in headers_lines:
            key, value = line.split(': ', 1)
            self.headers[key.lower()] = value

        # Parse body (data)
        self.data = body_section

