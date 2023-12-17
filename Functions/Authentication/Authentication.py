import sys

from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration
import base64
import json
import uuid
from datetime import datetime, timedelta

# userPass = {
#     "user1": "pass1"
# }

with open("Functions/Authentication/userPass.json", "r") as f:
    userPass = dict(json.load(f))


def authorize(req: Request, resp: Response, cmd: Command, config: Configuration):
    req, resp, cmd, config = check_cookies(req, resp, cmd, config)
    if cmd.skip_auth:
        set_cookie(req, resp, cmd, config)
        cmd.skip_auth = False
        return
    value: str = req.headers.get("authorization")
    if value is not None:
        code: str
        _, code = value.split(" ")
        decode_data = base64.b64decode(code).decode("utf-8")
        username, password = decode_data.split(":")  # type: str, str
        if userPass.get(username) is not None and userPass[username] == password:
            config.uuid = str(uuid.uuid3(uuid.NAMESPACE_OID, str(decode_data)))
            set_cookie(req, resp, cmd, config)
            cmd.skip_auth = False
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


def check_cookies(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.headers.get("cookie") is None:
        return req, resp, cmd, config
    init_cookie_in_req(req)
    ses_id = req.headers["cookie"].get("session-id")
    print(config.uuid, ses_id, file=sys.stderr)
    if ses_id is None:
        return req, resp, cmd, config
    username, password = ses_id.split(":")
    if userPass.get(username) is not None and userPass[username] == password:
        config.uuid = str(uuid.uuid3(uuid.NAMESPACE_OID, str(ses_id)))
        cmd.skip_auth = True
    return req, resp, cmd, config


def init_cookie_in_req(req: Request):
    tup = req.headers["cookie"].split("; ")
    cookie_dict = {}
    for cookie in tup:
        temp = cookie.split("=", 1)
        cookie_dict[temp[0]] = temp[1]
    req.headers["cookie"] = cookie_dict
    print(cookie_dict)


def set_cookie(req: Request, resp: Response, cmd: Command, config: Configuration):
    hours_interval = 2
    gmt = gmt_str(hours_interval=hours_interval)
    # gmt = gmt_str(second_interval=60)
    temp = "session-id=" + config.uuid + "; "
    temp += "Expires=" + gmt + "; "
    temp += "Path=/; "
    temp += "HttpOnly"
    resp.headers["set-cookie"] = temp


def gmt_str(hours_interval: int = 0, minute_interval: int = 0, second_interval: int = 0):
    # 获取当前 UTC 时间
    now = datetime.utcnow()
    # 增加两小时
    two_hours_later = now + timedelta(hours=hours_interval, minutes=minute_interval, seconds=second_interval)
    # 将时间格式化为 GMT 字符串（符合 RFC 1123 格式）
    gmt_time_str = two_hours_later.strftime('%a, %d %b %Y %H:%M:%S GMT')
    print(gmt_time_str)
    return gmt_time_str
