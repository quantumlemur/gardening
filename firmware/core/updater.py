from ubinascii import hexlify
from uhashlib import sha256
from uos import listdir

from core.config import config
from core.utilities import get


# def md5_file(fname):
#     hash_md5 = md5()
#     with open(fname, "rb") as f:
#         for chunk in iter(lambda: f.read(4096), b""):
#             hash_md5.update(chunk)
#     return hash_md5.hexdigest()


@micropython.native
def sha256_file(fname):
    hash_sha256 = sha256()
    with open(fname, "rb") as f:
        chunk = f.read(4096)
        while chunk != b"":
            hash_sha256.update(chunk)
            chunk = f.read(4096)
    return hexlify(hash_sha256.digest()).decode("utf-8")


@micropython.native
def update_all_files():
    filelist = get_filelist()
    newFilesAvailable = False
    for fname, hash in filelist:
        device_filelist = listdir()
        if fname not in device_filelist or hash != sha256_file(fname):
            newFilesAvailable = True
            get_file(fname)
    return newFilesAvailable


@micropython.native
def get_file(fname):
    print("Updating file {}".format(fname))
    path = "getfile_python_v2/{}".format(fname)
    request = get(path=path)
    if request.status_code == 200:
        with open(fname, "wb") as f:
            f.write(request.content)
        print("Download successful: {}".format(fname))


@micropython.native
def get_filelist():
    path = "listfiles_python_v2"
    request = get(path=path)
    # request.close()
    return request.json()


if __name__ == "__main__":
    from wifi import WifiConnection
    from config import Config

    config = Config()

    wifiConnection = WifiConnection(config)
    wifiConnection.connect_wifi()

    updater = Updater(config)
    updater.update_all_files()
