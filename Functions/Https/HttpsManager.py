from Entities.Request import Request
from Entities.Response import Response
from Entities.Command import Command
from Entities.Configuration import Configuration
from Functions.Https.KeysManager import KeyManager


def getPublicKey(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.headers.get("request-public-key") is not None and config.is_first_time and config.keysMan is None:
        cmd.resp_imm = True
        resp.statusCode = "200"
        resp.statusMessage = resp.code_massage[resp.statusCode]
        config.keysMan = KeyManager()
        cmd.return_pub_key = True
        resp.body = config.keysMan.generate_keys().decode()


def setSymKey(req: Request, resp: Response, cmd: Command, config: Configuration):
    if req.headers.get("give-symmetric-key") is not None and config.keysMan is not None:
        config.keysMan.load_sym_key(req.headers["give-symmetric-key"])
        cmd.resp_imm = True
        resp.statusCode = "200"
        resp.statusMessage = resp.code_massage[resp.statusCode]
        resp.body = 'Start transmitting data now!'

