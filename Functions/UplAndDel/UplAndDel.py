import base64

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

    value: str = req.headers.get("authorization")
    code: str
    _, code = value.split(" ")
    decode_data = base64.b64decode(code).decode("utf-8")
    username, password = decode_data.split(":")  # type: str, str
    username_input = req.path.split("=")[1]
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
        boundary = req.headers['content-type'].split('boundary=')[1]
        filename, content_disposition, content = parse_multipart_form_data(req.data, boundary)

        # 检查目录是否存在，如果不存在则创建
        filepath = './data/' + req.paras_dict['path']
        filepath = filepath[:-1]
        print(filepath)
        if not os.path.exists(filepath):
            os.makedirs(filepath)
            print('yes')
        # 保存文件
        with open(filepath + '/' + filename, 'w') as f:
            f.write(content)

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


def parse_multipart_form_data(data, boundary):
    print('data\n' + data)
    parts = data.split('--' + boundary)
    for part in parts[1:-1]:
        part = part.strip()
        if part.startswith('Content-Disposition:'):
            filename = part.split('filename="')[1].split('"')[0]
            content_disposition = part.split('Content-Disposition: ')[1].split('\r\n')[0]
            contents = part.split('\r\n')
            if len(contents) >= 2:
                content = contents[2]
            else:
                content = ''
            return filename, content_disposition, content
    return None, None, None
