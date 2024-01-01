import base64
import mimetypes

from Entities import Request, Response, Command, Configuration
import os


def uplAndDel(req: Request, resp: Response, cmd: Command, config: Configuration):
    # 判断请求类型
    if req.method.upper() != 'POST':
        resp.body = '405 Method Not Allowed'
        response_code(resp, cmd, "405")
        print('405 Method Not Allowed')
        return

    req.arg_path_para()
    path = req.file_path
    print('path:', path, '\npara', req.paras_dict)
    print('file_path:', req.file_path)
    if config.user is None or config.password is None:
        value: str = req.headers.get("authorization")
        code: str
        _, code = value.split(" ")
        decode_data = base64.b64decode(code).decode("utf-8")
        username, password = decode_data.split(":")  # type: str, str
    else:
        username = config.user
        password = config.password
    if not 'path=' in req.path:
        resp.body = '400 Bad Request'
        response_code(resp, cmd, "400")
        print('400 Bad Request')
        return
    username_input = req.path.split("=")[1]
    print('username_input:'+username_input)
    if username_input.startswith('/'):
        username_input = username_input.split("/")[1]
    else:
        username_input = username_input.split("/")[0]

    if username_input != username:
        resp.body = '403 Forbidden'
        response_code(resp, cmd, "403")
        print('403 Forbidden')
        return

    # 判断任务
    if path == '/upload':
        # 判断path是否正确提供
        if len(req.paras_dict) == 0 or req.paras_dict['path'] == '':
            resp.body = '400 Bad Request'
            response_code(resp, cmd, "400")
            print('400 Bad Request')
            return
        print('upload')

        # 检查目录是否存在，如果不存在则创建
        filepath = './data/' + username
        if not os.path.exists(filepath):
            os.makedirs(filepath)
            print('create dir')

        filepath = './data/' + req.paras_dict['path'] + '/'
        filepath = filepath[:-1]
        print(filepath)
        if not os.path.exists(filepath):
            resp.body = '404 Not Found'
            response_code(resp, cmd, "404")
            print('404 Not Found')
            return


        boundary = req.headers['content-type'].split('boundary=')[1].encode()
        parts = req.upload_data.split(b'--' + boundary + b'\r\n')

        for part in parts[1:]:  # 忽略开头和结尾的边界
            headers, body = part.split(b'\r\n\r\n', 1)
            headers = headers.decode('utf-8')
            disposition = headers.split('Content-Disposition: ')[1].split('\r\n')[0]
            filename = disposition.split('filename="')[1].split('"')[0]

            # 解析文件内容
            if boundary in body:
                body = body.split(boundary + b'--')[0]
                file_content = body[:-4]  # 去掉末尾的\r\n--
            else:
                file_content = body

            # 保存文件到已知路径
            filepath = filepath + filename
            with open(filepath, 'wb') as f:
                f.write(file_content)

        # boundary = req.headers['content-type'].split('boundary=')[1].encode()
        # filename = b''
        # content = b''
        # parts = req.upload_data.split(b'--' + boundary + b'\r\n')
        # for part in parts:
        #     part = part.strip()
        #     if part.startswith(b'Content-Disposition:'):
        #         filename = part.split(b'filename="')[1].split(b'"')[0]
        #         # content_disposition = part.split(b'Content-Disposition: ')[1].split(b'\r\n')[0]
        #         contents = part.split(b'\r\n\r\n')
        #         if len(contents) >= 2:
        #             content = contents[-1].split(b'--' + boundary + b'--')[0]
        #         else:
        #             content = ''
        #
        # # 保存文件
        # if filename == b'':
        #     resp.body = '400 Bad Request'
        #     response_code(resp, cmd, "400")
        #     print('400 Bad Request')
        #     return
        # with open(filepath + '/' + filename.decode('utf-8'), 'wb') as f:
        #     f.write(content)


    elif path == '/delete':
        # 判断path是否正确提供
        if len(req.paras_dict) == 0 or req.paras_dict['path'] == '' or "/" not in req.paras_dict['path']:
            resp.body = '400 Bad Request'
            response_code(resp, cmd, "400")
            print('400 Bad Request')
            return
        print('delete')
        filepath = './data/' + req.path.split('=')[1]
        print(filepath)
        if os.path.exists(filepath):
            os.remove(filepath)
        else:
            resp.body = '404 Not Found'
            response_code(resp, cmd, "404")
            print('404 Not Found')
            return
    else:
        resp.body = '400 Bad Request'
        response_code(resp, cmd, "400")
        print('400 Bad Request')
        return


def response_code(res: Response, cmd: Command, code: str):
    res.statusCode = code
    res.statusMessage = res.code_massage[code]
    if not code.startswith("2"):
        cmd.resp_imm = True


# def parse_multipart_form_data(data, boundary):
#     print('data\n' + data)
#     parts = data.split('--' + boundary)
#     for part in parts[1:-1]:
#         part = part.strip()
#         if part.startswith('Content-Disposition:'):
#             filename = part.split('filename="')[1].split('"')[0]
#             content_disposition = part.split('Content-Disposition: ')[1].split('\r\n')[0]
#             contents = part.split('\r\n')
#             if len(contents) >= 2:
#                 content = contents[2]
#             else:
#                 content = ''
#             return filename, content_disposition, content
#     return None, None, None


def parse_multipart_form_data(data, boundary):
    # print('data\n' + data)
    parts = data.split(b'--' + boundary)
    for part in parts[1:-1]:
        part = part.strip()
        if part.startswith(b'Content-Disposition:'):
            filename = part.split(b'filename="')[1].split('"')[0]
            content_disposition = part.split(b'Content-Disposition: ')[1].split('\r\n')[0]
            # 对于非文本内容，直接获取其全部内容，不进行分割
            if b'application/octet-stream' in content_disposition:
                content = part.split('\r\n--' + boundary)[0]
            else:
                contents = part.split('\r\n')
                if len(contents) >= 2:
                    content = contents[2]
                else:
                    content = ''
            return filename, content_disposition, content
    return None, None, None