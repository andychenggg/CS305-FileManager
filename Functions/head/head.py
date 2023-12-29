from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration


def head(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.method.lower() == 'head':
        resp.statusCode = '200'
        resp.headers["connection"] = "keep-alive"
        cmd.resp_imm = True
