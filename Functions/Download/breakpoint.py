import os

from Entities import Response,Command

boundary = '3d6b6a416f9b5'

def breakpointtransmission(req, file_path, resp: Response, cmd: Command):
    ranges = req.headers['range'].split(",")
    with open(file_path, 'rb') as file:
        # 获取文件大小
        file_size = os.path.getsize(file_path)
    for range in ranges:
        if not validate_range(range, file_size):
            resp.body = f'416 Range Not Satisfiable'
            responseCode(resp, cmd, "416")
            print('Range Not Satisfiable', range)
            return
    content = ''
    for range in ranges:
        content = content + '--'+boundary+'\n'+'Content-type= text/plain\n'
        start, end = map(int, range.split('-'))
        content = content + f'Content-range= {start}-{end}/{file_size}\n\n'
        response_size = end - start + 1
        with open(file_path, 'rb') as file1:
            # 将文件指针移动到起始位置
            file1.seek(start)
            # 获取响应内容
            content = content + file1.read(response_size).decode('utf-8')+'\n'

    content = content + '--' + boundary + '--'
    resp.file_content = content.encode()
    resp.set_content_length(len(content))

def validate_range(range, file_size):
    # 验证范围是否有效
    if '-' not in range:
        return False
    else:
        start, end = map(int, range.split('-'))
        if start == '' and end == '':
            return False
        elif (start == '' and end >= file_size) or (end == '' and start >= file_size):
            return False
        elif start > end or start >= file_size or end >= file_size:
            return False
    return True

def responseCode(res: Response, cmd: Command, code: str):
    res.statusCode = code
    res.statusMessage = res.code_massage[code]
    if not code.startswith("2"):
        cmd.resp_imm = True
