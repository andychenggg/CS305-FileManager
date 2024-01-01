from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration
from Functions.Authentication.Authentication import get_cookie_str, cookie_dict
import json

with open("Functions/Authentication/userPass.json", "r") as f:
    userPass = dict(json.load(f))


def login(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.path.lower() == '/login':
        with open('html_package/login.html', 'r', encoding='utf-8') as f:
            html_content = f.read()
        resp.body = html_content
        cmd.resp_imm = True


def submit_login(json_str: str) -> str:
    failed: str = '{\"status\": 401}'
    form: dict = dict(json.loads(json_str))
    if form.get('username') is None or form.get('password') is None:
        return failed
    elif userPass.get(form['username']) == form.get('password'):
        up = form['username'] + ':' + form['password']
        ck_str = get_cookie_str(2, up)
        cookie_dict[up] = ck_str
        return f'{{\"status\": 200, \"cookie\": \"{ck_str}\"}}'
    return failed
