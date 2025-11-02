import pytest
from FernetCrypto import FernetCrypto
import random
import string

def random_string(length, seed):
    random.seed = seed
    letters = string.printable
    return ''.join(random.choice(letters) for i in range(length))

@pytest.fixture
def random_input():
    return [ random_string(20, 67) for _ in range(5) ]

def test_crypto(random_input):
    for input in random_input:
        (crypto, _) = FernetCrypto.from_pwd(input)
        enc = crypto.encrypt(input)
        dec = crypto.decrypt_to_str(enc)
        assert dec == input
    