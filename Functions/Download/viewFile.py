from Entities import Request, Response, Command, Configuration
import os
import mimetypes

from Functions.Download.breakpoint import breakpointtransmission


def viewFile(req: Request, resp: Response, cmd: Command, config: Configuration):
    req.arg_path_para()
    path = req.file_path

    req.arg_path_para()
    print('path:', req.path, '\npara', req.paras_dict,'\nfile_path:', req.file_path)
    # print('file_path:', req.file_path)
    if path.endswith('/'):
        project_directory = f'./data{path}'
        # check if the directory exists
        try:
            items = os.listdir(project_directory)
        except (NotADirectoryError, FileNotFoundError):
            resp.body = '404 Not Found'
            responseCode(resp, cmd, "404")
            print('there is no', project_directory)
            return
        # check parameters is valid
        # flag = 0 is invalid
        # flag = 1|2 is valid, 1 is return html, 2 is simply return the list
        para = req.paras_dict.get('sustech-http', '0')

        flag = 0
        if len(req.paras_dict) <= 1:
            if para == '0':
                flag = 1
            elif para == '1':
                flag = 2
            for key in req.paras_dict.keys():
                if key != 'sustech-http':
                    flag = 0
                    break


        if not flag:
            resp.body = f'400 Bad Request'
            responseCode(resp, cmd, "400")
            print(resp.body)
            return
        folders = []
        files = []
        for item in items:
            item_path = os.path.join(project_directory, item)
            if os.path.isdir(item_path):
                folders.append(item + '/')
                if flag == 1:
                    resp.htmlM.add_directory(item + '/')
            elif os.path.isfile(item_path):
                files.append(item)
                if flag == 1:
                    resp.htmlM.add_file(item)
        if flag == 1:
            resp.htmlM.back_path = os.path.dirname(os.path.dirname(path))
            resp.htmlM.current_path = os.path.dirname(path)
            if resp.htmlM.back_path == '/':
                resp.htmlM.back_path = ''
            if resp.htmlM.current_path == '/':
                resp.htmlM.current_path = ''
            resp.body = resp.htmlM.generate_html()
        else:
            # resp.body = '[' + ', '.join(folders + files) + ']'
            resp.body = '[' + ', '.join(f'"{item}"' for item in (folders + files)) + ']'
            # resp.body = folders + files
    else:
        if req.method.upper() != 'GET':
            resp.body = '405 Method Not Allowed'
            responseCode(resp, cmd, "405")
            print('405 Method Not Allowed')
            return
        # check parameters is valid
        chunked_num = req.paras_dict.get('chunked', '0')
        if len(req.paras_dict) > 1 or chunked_num not in {'0', '1'} or len(
                req.paras_dict) == 1 and req.paras_dict.keys() != {'chunked'}:
            resp.body = f'400 Bad Request'
            responseCode(resp, cmd, "400")
            print(resp.body)
            return
        # check if the file exists
        file_path = f'./data{path}'
        if not os.path.isfile(file_path):
            resp.body = f'404 Not Found'
            responseCode(resp, cmd, "404")
            print('there is no', file_path)
            return
        # normal file
        resp.file = True
        if chunked_num == '0':
            try:
                with open(file_path, 'rb') as file:
                    binary_content = file.read()
            except FileNotFoundError:
                resp.file = False
                resp.body = f'404 Not Found {file_path}'
                responseCode(resp, cmd, "404")
                print('there is no', file_path)
                return
            if "range" in req.headers:
                print('it has range')
                if not breakpointtransmission(req, file_path, resp, cmd):
                    resp.file = False
                    resp.body = '416 Range Not Satisfiable'
                    responseCode(resp, cmd, "416")
                    print('Range Not Satisfiable')
                    return
            else:
                print('it dose not have range')
                resp.file_content = binary_content
                resp.set_content_length(len(binary_content))
            mini_type = mimetypes.guess_type(file_path)[0]
            mini_type = mini_type if mini_type else 'application/octet-stream'
            resp.set_content_type(mini_type)
        else:
            cmd.chunked = True
            resp.set_content_type('application/octet-stream')
            resp.headers['Transfer-Encoding'] = 'chunked'
            resp.chunk_path = file_path


def responseCode(res: Response, cmd: Command, code: str):
    res.statusCode = code
    res.statusMessage = res.code_massage[code]
    if not code.startswith("2"):
        cmd.resp_imm = True
