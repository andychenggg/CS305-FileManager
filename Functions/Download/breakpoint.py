import os
import threading

from Entities import Response,Command

boundary = '3d6b6a416f9b5'

def breakpointtransmission(req, file_path, resp: Response, cmd: Command):
    getRange = req.headers['range']
    if 'bytes=' in getRange:
        getRange = getRange.split("=")[1]
    ranges = getRange.split(",")
    with open(file_path, 'rb') as file:
        # 获取文件大小
        file_size = os.path.getsize(file_path)
    for range in ranges:
        if not validate_range(range, file_size):
            return False
    content = process_ranges(ranges,file_path,boundary,file_size)
    # for range in ranges:
    #     content = content + '--'+boundary+'\n'+'Content-type= text/plain\n'
    #     start, end = map(str, range.split('-'))
    #     if start == '':
    #         start = file_size - int(end)
    #         end = file_size-1
    #     elif end == '':
    #         start = int(start)
    #         end = file_size-1
    #     else:
    #         start = int(start)
    #         end = int(end)
    #     content = content + f'Content-range= {start}-{end}/{file_size}\n\n'
    #     response_size = end - start + 1
    #     with open(file_path, 'rb') as file1:
    #         # 将文件指针移动到起始位置
    #         file1.seek(start)
    #         # 获取响应内容
    #         content = content + file1.read(response_size).decode('utf-8')+'\n'
    content = content + '--' + boundary + '--'
    print(content)
    resp.file_content = content.encode()
    resp.set_content_length(len(content))
    resp.body = f'206 Partial Content'
    responseCode(resp, cmd, "206")
    return True

def validate_range(range, file_size):
    # 验证范围是否有效
    if '-' not in range:
        return False
    else:
        start, end = map(str, range.split('-'))
        if start == '':
            if end == '':
                return False
            elif int(end) >= file_size:
                return False
        else:
            if end == '':
                if int(start) >= file_size:
                    return False
            elif int(start) > int(end) or int(start) >= file_size or int(end) >= int(file_size):
                return False
    return True

def responseCode(res: Response, cmd: Command, code: str):
    res.statusCode = code
    res.statusMessage = res.code_massage[code]
    if not code.startswith("2"):
        cmd.resp_imm = True

def process_range(range, file_path, boundary, file_size, results):
    start, end = map(str, range.split('-'))
    if start == '':
        start = file_size - int(end)
        end = file_size - 1
    elif end == '':
        start = int(start)
        end = file_size - 1
    else:
        start = int(start)
        end = int(end)
    content = '--' + boundary + '\nContent-type= text/plain\n'
    content += f'Content-range= {start}-{end}/{file_size}\n\n'
    response_size = end - start + 1
    with open(file_path, 'rb') as file1:
        file1.seek(start)
        content += file1.read(response_size).decode('utf-8') + '\n'
    results.append(content)  # 将结果添加到共享列表中


def process_ranges(ranges, file_path, boundary, file_size):
    results = []  # 创建一个共享列表来存储结果
    threads = []
    for range in ranges:
        t = threading.Thread(target=process_range, args=(range, file_path, boundary, file_size, results))
        threads.append(t)
        t.start()
        # 等待所有线程完成
    for t in threads:
        t.join()
        # 合并所有线程的结果
    final_content = ''.join(results)
    return final_content