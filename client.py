import os
import json
import base64
import string
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES

PRIME = 2**128 + 51

def split_secret(secret_bytes):
    secret = int.from_bytes(secret_bytes, "big")
    a = int.from_bytes(get_random_bytes(16), "big") % PRIME

    shares = []
    for x in [1, 2, 3]:
        y = (a * x + secret) % PRIME
        shares.append({
            "x": x,
            "y": hex(y)
        })

    return shares

def reconstruct_secret(s1, s2):
    x1, y1 = s1["x"], int(s1["y"], 16)
    x2, y2 = s2["x"], int(s2["y"], 16)

    denom = (x2 - x1) % PRIME
    inv = pow(denom, PRIME - 2, PRIME)

    secret = (y1 * x2 * inv - y2 * x1 * inv) % PRIME
    return secret.to_bytes(16, "big")

def derive_key(password, salt):
    return PBKDF2(password, salt, dkLen=16, count=100000)

def encrypt(plaintext, key):
    cipher = AES.new(key, AES.MODE_GCM)
    ct, tag = cipher.encrypt_and_digest(plaintext)
    return ct + tag, cipher.nonce

def decrypt(blob, key, nonce):
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ct, tag = blob[:-16], blob[-16:]
    return cipher.decrypt_and_verify(ct, tag)

def save_local(username, enc_share, nonce, salt, backup_vault, backup_nonce):
    filename = f"client_local_{username}.json"

    data = {
        "enc_share": base64.b64encode(enc_share).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "salt": base64.b64encode(salt).decode(),
        "backup_vault": base64.b64encode(backup_vault).decode(),
        "backup_nonce": base64.b64encode(backup_nonce).decode()
    }

    with open(filename, "w") as f:
        json.dump(data, f)


def load_local(username):
    filename = f"client_local_{username}.json"

    if not os.path.exists(filename):
        return None

    with open(filename, "r") as f:
        data = json.load(f)

    return {
        "enc_share": base64.b64decode(data["enc_share"]),
        "nonce": base64.b64decode(data["nonce"]),
        "salt": base64.b64decode(data["salt"]),
        "backup_vault": base64.b64decode(data["backup_vault"]),
        "backup_nonce": base64.b64decode(data["backup_nonce"])
    }

def generate_password(length):
    chars = string.ascii_letters + string.digits + "!@#$%^&*()"
    return "".join(
        chars[b % len(chars)]
        for b in get_random_bytes(length)
    )