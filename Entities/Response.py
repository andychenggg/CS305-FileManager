
class Response:
    statusCode = {
        200: "OK",
        206: "Partial Content",
        301: "Redirect",
        400: "Bad Request",
        401: "Unauthorized",
        403: "Forbidden",
        404: "Not Found",
        405: "Method Not Allowed",
        416: "Range Not Satisfiable",
        502: "Bad Gateway",
        503: "Service Temporarily Unavailable"
    }
    http_version = "HTTP/1.1"
