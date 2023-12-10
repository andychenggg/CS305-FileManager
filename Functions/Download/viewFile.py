from Entities import Request, Response, Command, Configuration


def viewFile(req: Request, resp: Response, cmd: Command, config: Configuration):
    web_url: str = req.path
    split_url = web_url.strip().split('?')
    path = split_url[0]
    para = split_url[1] if len(split_url) > 1 else ''
    print('path:', path, '\npara', para)

