import json
from Crypto.Cipher import AES

from common.constants import ENCODING, MAX_PACKAGE_LENGTH


SECRET_KEY = b'super_secret_key'


def padding_text(text):
    ''' Выравнивание сообщения до длины, кратной 16 байтам.
        В данном случае исходное сообщение дополняется пробелами.
    '''
    pad_len = (16 - len(text) % 16) % 16
    return text + b' ' * pad_len


def _encrypt(plaintext, key=SECRET_KEY):
    """ Шифрование сообщения plaintext ключом key.
        Атрибут iv - вектор инициализации для алгоритма шифрования.
        Если не задается явно при создании объекта-шифра, генерируется случайно.
        Его следует добавить в качестве префикса к финальному шифру,
        чтобы была возможность правильно расшифровать сообщение.
    """
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.iv + cipher.encrypt(plaintext)
    return ciphertext


def _decrypt(ciphertext, key):
    """ Расшифровка шифра ciphertext ключом key.
        Вектор инициализации берется из исходного шифра.
        Его длина для большинства режимов шифрования всегда 16 байт.
        Расшифровываться будет оставшаяся часть шифра.
    """
    cipher = AES.new(key, AES.MODE_CBC, iv=ciphertext[:16])
    msg = cipher.decrypt(ciphertext[16:])
    return msg


def send_encrypted_message(sock, msg):
    """Отправка зашифрованного сообщения"""
    print(f'send {msg}')
    msg = json.dumps(msg).encode(ENCODING)
    msg = padding_text(msg)
    sock.send(_encrypt(msg, SECRET_KEY))
    print('Sent')


def get_encrypted_message(sock):
    """Получение зашифрованного сообщения"""
    msg = sock.recv(MAX_PACKAGE_LENGTH)
    msg = _decrypt(msg, SECRET_KEY)
    msg = json.loads(msg.decode(ENCODING))

    print(f'get {msg}')

    if isinstance(msg, dict):
        return msg
    raise ValueError
