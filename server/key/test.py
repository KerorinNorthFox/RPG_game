from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
 
data = "ねこちゃん".encode("utf-8")
 
recipient_key = RSA.import_key(open("public.pem").read())
session_key = get_random_bytes(16)
 
# セッションキーをRSA公開鍵で暗号化する
cipher_rsa = PKCS1_OAEP.new(recipient_key)
enc_session_key = cipher_rsa.encrypt(session_key)

cipher_aes = AES.new(session_key, AES.MODE_EAX)
ciphertext, tag = cipher_aes.encrypt_and_digest(data)

for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
    print(x)
    print('\n')
