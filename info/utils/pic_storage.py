import qiniu

access_key = "KP1RLxS4sxzg9x2MGUeqTYX3jcOeYCQGtxgg7x20"
secret_key = "VfwsLS0-A-9W9iNFNotuef5OmPyW1dhnxr6PwKf4"
# 上传图片的空间名称
bucket_name = "shiwanlinzt"


def pic_storage(data):
    """
    上传文件到qiniu平台
    key：图片名称，为None时名称由平台给定，且唯一
    data：图片二进制内容
    :return:
    """
    if not data:
        return AttributeError("图片数据为空")
    q = qiniu.Auth(access_key, secret_key)
    token = q.upload_token(bucket_name)
    # 上传图片到平台,ret：平台返回的图片名称
    ret, info = qiniu.put_data(token, None, data)
    if ret is not None:
        print('All is OK')
        # print(ret)
        # print("------")
        # print(info)
    else:
        print(info)  # error message in info

    if info.status_code == 200:
        print("上传成功")
    else:
        # 抛出异常，让调用着可获取异常
        raise AttributeError("上传图片到平台失败")

    return ret


if __name__ == '__main__':
    file_name = input("输入上传的文件")
    with open(file_name, "rb") as f:
        pic_storage(f.read())
