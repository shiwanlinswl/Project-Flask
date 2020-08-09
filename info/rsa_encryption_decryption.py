# coding=utf-8
import rsa
import os
import sys

private_pem_abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "private.pem")
password_data_abspath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passwd.data")


def create_keys():
    # 生成公钥和私钥
    (pubkey, privkey) = rsa.newkeys(1024)
    pub = pubkey.save_pkcs1()
    with open('public.pem', 'wb+')as f:
        f.write(pub)

    pri = privkey.save_pkcs1()
    with open('private.pem', 'wb+')as f:
        f.write(pri)


def encrypt(password):
    # 用公钥加密
    with open('public.pem', 'rb') as publickfile:
        p = publickfile.read()
    pubkey = rsa.PublicKey.load_pkcs1(p)
    original_text = password.encode('utf8')
    crypt_text = rsa.encrypt(original_text, pubkey)
    print(crypt_text)
    # return crypt_text  # 加密后的密文
    f = open('passwd.data', 'wb')
    f.write(crypt_text)
    f.close()


def decrypt():
    # 用私钥解密
    with open(private_pem_abspath, 'rb') as privatefile:
        p = privatefile.read()
    privkey = rsa.PrivateKey.load_pkcs1(p)
    f = open(password_data_abspath, 'rb')
    crypt_text = f.read()
    # 注意，这里如果结果是bytes类型，就需要进行decode()转化为str
    lase_text = rsa.decrypt(crypt_text, privkey).decode()

    # print(lase_text)
    f.close()
    return lase_text


if __name__ == '__main__':
    # create_keys()
    # password = "shi930718"
    # encrypt(password=password)
    """
    b'\x13-\xc6\xf6\xc0\x8e*\x8f\x9d\x9c\x1em9/\xf3\x1dt\xa1E\xf3e\x16\xa2\xf6\xd4\xad\x8e\x81I\xb1\xf3\x8d\xdc\x8c\xd6\x11g\xe1\x7fg\xe24\x88\xf5kb9\xd5\x8c\x98\x9f\xd6\x03\x00\xfd\xf0\xcb\x8b\xffv\xa8\x9bbUU\xc6\xb0Bg\x14g\x89~m\x1a\xed\xaa\x17\x19\x89\x86\x15\xc3\xbc,\xd9\x84km]\xf9\x90\xb4\xb6\x11\xe5\xce\xbdN\xcd\xde\xa5z\xca?\x1dGlq\xd8\x95\x82\t\x9f@\xfb\x14\xd4G"\xc9\xa75\xb2!\x7f\xefx'
    """
    # decrypt()