from Entities import Request, Response, Command, Configuration
import os


def viewFile(req: Request, resp: Response, cmd: Command, config: Configuration):
    web_url: str = req.path
    if req.method.upper() != 'GET':
        resp.body = '405 Method Not Allowed'
        responseCode(resp, cmd, "405")
        print('405 Method Not Allowed')
        return

    split_url = web_url.strip().split('?')
    path = split_url[0]
    para = split_url[1] if len(split_url) > 1 else 'sustech-http=0'
    print('path:', path, '\npara', para)
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
        flag = 0
        if para.lower().startswith('sustech-http'):
            split_para = para.strip().split('=')
            if len(split_para) == 2 and (split_para[1].strip() == '1' or split_para[1].strip() == '0'):
                flag = int(split_para[1].strip()) + 1
        if not flag:
            resp.body = f'400 Bad Request in {para}'
            responseCode(resp, cmd, "400")
            print(resp.body)
            return
        folders = []
        files = []
        # TODO 在html加个 . 和 ..
        for item in items:
            item_path = os.path.join(project_directory, item)
            if os.path.isdir(item_path):
                folders.append(item+'/')
                if flag == 1:
                    resp.htmlM.add_directory(item+'/')
            elif os.path.isfile(item_path):
                files.append(item)
                if flag == 1:
                    resp.htmlM.add_file(item)
        if flag == 1:
            resp.body = resp.htmlM.generate_html()
        else:
            resp.body = '['+', '.join(folders + files)+']'

    else:
        pass


def responseCode(res: Response, cmd: Command, code: str):
    res.statusCode = code
    res.statusMessage = res.code_massage[code]
    if not code.startswith("2"):
        cmd.resp_imm = True
