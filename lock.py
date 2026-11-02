"""Lock a home code for homes.txt with the public key in docs/lock.js.
Usage: python lock.py '{"k": "HOME", "n": "Chalet", "p": [46.81, -71.21], "c": "..."}'
k: MAIN (your own home's location), HOME (Echo) or PHONE (ntfy). Same keys as the setup pages."""
import base64
import json
import os
import re
import sys
from pathlib import Path


def public_key():
    from cryptography.hazmat.primitives.serialization import load_der_public_key
    js = (Path(__file__).parent / "docs" / "lock.js").read_text()
    return load_der_public_key(base64.b64decode(re.search(r'OLF_PUBKEY = "([^"]+)"', js).group(1)))


def lock(obj, pub=None) -> str:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    key, iv = AESGCM.generate_key(bit_length=256), os.urandom(12)
    oaep = padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
    blob = (pub or public_key()).encrypt(key, oaep) + iv + AESGCM(key).encrypt(iv, json.dumps(obj).encode(), None)
    return "olf1:" + base64.urlsafe_b64encode(blob).decode().rstrip("=")


if __name__ == "__main__":
    print(lock(json.loads(sys.argv[1])))
