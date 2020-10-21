import urequests

from os import listdir
from ubinascii import hexlify
from uhashlib import sha256


# local file imports
from credentials import credentials


class Updater:

    def __init__(self):
        pass

    # def md5_file(fname):
    #     hash_md5 = md5()
    #     with open(fname, "rb") as f:
    #         for chunk in iter(lambda: f.read(4096), b""):
    #             hash_md5.update(chunk)
    #     return hash_md5.hexdigest()

    def sha256_file(self, fname):
        hash_sha256 = sha256()
        with open(fname, "rb") as f:
            chunk = f.read(4096)
            while chunk != b"":
                hash_sha256.update(chunk)
                chunk = f.read(4096)
        return hexlify(hash_sha256.digest()).decode("utf-8")

    def update_all_files(self):
        filelist = self.get_filelist()
        newFilesAvailable = False
        for fname, hash in filelist:
            device_filelist = listdir()
            if fname not in device_filelist or hash != self.sha256_file(fname):
                newFilesAvailable = True
                self.get_file(fname)
        return newFilesAvailable

    def get_file(self, fname):
        print("Updating file " + fname)
        url = credentials['server_url'] + '/getfile_python/' + fname
        request = urequests.get(url=url)
        if request.status_code == 200:
            with open(fname + ".new", 'wb') as f:
                f.write(request.content)
            print('Download successful: ' + fname)

    def get_filelist(self):
        url = credentials['server_url'] + '/listfiles_python'
        request = urequests.get(url=url)
        # request.close()
        return (request.json())

    def put_data(self, data):
        request = urequests.put(json=data)
        # request.close()


if __name__ == "__main__":
    from wifi import WifiConnection

    wifiConnection = WifiConnection()
    wifiConnection.connect_wifi()

    updater = Updater()
    updater.update_all_files()
