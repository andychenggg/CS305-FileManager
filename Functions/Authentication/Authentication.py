from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration
import base64

userPass = {
    "user1": "pass1"
}


def authorize(req: Request, resp: Response, cmd: Command, config: Configuration):
    value: str = req.headers.get("authorization")
    if value is not None:
        code: str
        _, code = value.split(" ")
        decode_data = base64.b64decode(code).decode("utf-8")
        username, password = decode_data.split(":")  # type: str, str
        if userPass.get(username) is not None and userPass[username] == password:
            return
    if config.is_first_time:
        config.is_first_time = False
        cmd.resp_imm = True
        resp.statusCode = "401"
        resp.statusMessage = resp.code_massage[resp.statusCode]
        resp.headers["WWW-Authenticated"] = "Basic realm=\"Authorization Required\""
        resp.body = "Access to this resource requires authentication"
    else:
        cmd.resp_imm = True
        resp.statusCode = "401"
        resp.statusMessage = resp.code_massage[resp.statusCode]
        resp.body = "Access to this resource requires authentication"
