from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration


def persistent_connection_and_head_process(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.headers["connection"].lower() == "close":
        resp.headers["connection"] = "close"
        cmd.close_conn = True
    else:
        resp.headers["connection"] = "keep-alive"

