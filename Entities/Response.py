from html_package.HTMLManager import HTMLManager


class Response:
    code_massage = {
        "200": "OK",
        "206": "Partial Content",
        "301": "Redirect",
        "400": "Bad Request",
        "401": "Unauthorized",
        "403": "Forbidden",
        "404": "Not Found",
        "405": "Method Not Allowed",
        "416": "Range Not Satisfiable",
        "502": "Bad Gateway",
        "503": "Service Temporarily Unavailable"
    }

    def __init__(self):
        self.http_version: str = "HTTP/1.1"
        self.statusCode: str = "200"
        self.statusMessage: str = "OK"
        self.file: bool = False
        self.headers: dict = {
            "Content-Type": "text/html; charset=utf-8"
        }
        self.htmlM: HTMLManager = HTMLManager()
        self.file_content: bytes = b""
        self.body: str = self.htmlM.generate_html()

        self.need_connection = True

    def setContentType(self, type: str):
        self.headers["Content-Type"] = type

    def parse_resp_to_str(self) -> str:
        # Create the HTTP response
        start_line = self.http_version + " " + self.statusCode + " " + self.statusMessage + "\r\n"
        if not self.file:
            self.headers["Content-Length"] = str(len(self.body.encode("utf-8")))
        else:
            self.headers["Content-Length"] = len(self.file_content)
        headers_line = ""
        for key in self.headers:
            headers_line = headers_line + key + ": " + str(self.headers[key]) + "\r\n"
        empty_line = "\r\n"
        return start_line + headers_line + empty_line
