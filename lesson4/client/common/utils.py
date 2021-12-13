import json
from server.common.constants import ENCODING, MAX_PACKAGE_LENGTH
# from decorators import log


# @log
def get_message(sock):
    msg = json.loads(sock.recv(MAX_PACKAGE_LENGTH).decode(ENCODING))

    if isinstance(msg, dict):
        return msg
    raise ValueError


# @log
def send_message(sock, msg):
    msg = json.dumps(msg)
    sock.send(msg.encode(ENCODING))
