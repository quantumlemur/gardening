from esp32 import Partition
from math import ceil, floor
from os import remove
from ubinascii import hexlify
from uhashlib import sha256
import ujson
from machine import reset
import urequests
from ure import compile

from core.config import config
from currentVersionInfo import currentVersionHash, currentVersionTag


class OTAUpdater:
    def __init__(self):
        self.nextPartition = Partition(Partition.RUNNING).get_next_update()
        self.numBlocks = self.nextPartition.ioctl(4, None)
        self.blockSize = self.nextPartition.ioctl(5, None)
        self.hash = sha256()
        self.firmwareSize = 0

    # def checkAndUpdate(self):
    #     versions = self.get_available_versions()
    #     version = versions[0]
    #     currentVersionTag = "0"
    #     try:
    #         from currentVersionInfo import currentVersionTag
    #     except ImportError:
    #         pass

    #     newCommitTag = version["filename"][:-4]
    #     if newCommitTag > currentVersionTag:
    #         print(
    #             "New firmware found!  {} => {}".format(currentVersionTag, newCommitTag)
    #         )
    #         self.updateFirmware(version)
    #         self.setNextBoot()
    #         print("Download successful.  Restarting...")
    #         reset()

    # def eraseNextPartition(self):
    #     print("Erasing partition...")
    #     for i in range(self.numBlocks):
    #         print("erasing block {} of {}".format(i, self.numBlocks), end="\r")
    #         self.nextPartition.ioctl(6, i)
    #     print("Partition erased!")

    # def parseHeaders(self, headerString):
    #     """Parse header string and return dictionary of headers"""
    #     headerStrings = headerString.split(b"\r\n")
    #     headers = {
    #         row.split(b":")[0]
    #         .decode("utf-8")
    #         .strip(): row.split(b":")[1]
    #         .decode("utf-8")
    #         .strip()
    #         for row in headerStrings
    #         if row.find(b":") != -1
    #     }
    #     return headers

    def getAvailableVersions(self):
        url = "{}/list_versions".format(config.get("server_url"))
        headers = {"mac": str(config.get("mac"))}
        request = urequests.get(url=url, headers=headers)
        versions = request.json()
        request.close()
        return versions

    def getDesiredVersion(self):
        firmwareVersions = self.getAvailableVersions()
        firmwareRequest = config.get("requested_version_tag")
        chosenVersion = None
        if len(firmwareRequest) > 0:
            # if there's an existing request
            for v in firmwareVersions:
                tag = v["filename"][:-4]
                if firmwareRequest == tag:
                    chosenVersion = v
        else:
            # no existing request, get the latest.  List from server is pre-sorted
            chosenVersion = firmwareVersions[0]
            #  = sorted(
            #     firmwareVersions, key=lambda x: x["parsed_version"], reverse=True
            # )[0]
            stripRe = compile("((\d+[\.\-]?)+)")
            splitRe = compile("[\.\-]")
            strippedVersion = stripRe.search(currentVersionTag).group(0).strip("-.")
            # print(strippedVersion)
            splitVersion = splitRe.split(strippedVersion)
            # print(splitVersion)
            parsedVersion = [int(s) for s in splitVersion]
            # print("split version:")
            # print(parsedVersion, chosenVersion["parsed_version"])
            if chosenVersion["parsed_version"] < parsedVersion:
                chosenVersion = None
        if chosenVersion and chosenVersion["filename"][:-4] == currentVersionTag:
            # don't try to update if we're already on the right version
            chosenVersion = None
        return chosenVersion

    def updateFirmware(self, version=None):
        if not version:
            version = self.getAvailableVersions()[0]

        filename = version["filename"]
        bytesExpected = version["size"]
        self.firmwareSize = bytesExpected

        print("Downloading new firmware {}".format(filename))

        url = "{}/get_firmware/{}".format(config.get("server_url"), filename)
        headers = {"mac": str(config.get("mac"))}

        request = urequests.get(url=url, headers=headers)

        if request.status_code == 200:

            # expectedBlocks = ceil(self.firmwareSize / self.blockSize)

            # discard the contents before the magic start byte
            # chunk = chunk[chunk.find(b"\xe9") :]

            ##### Continuous writing
            # offset = 0
            # while len(chunk) > 0:
            #     print("Writing byte {} of {}".format(offset, bytesToDownload), end="\n")
            #     self.nextPartition.writeblocks(0, chunk, offset)
            #     self.hash.update(chunk)
            #     offset += len(chunk)
            #     chunk = s.recv(4096)

            # bytesWritten = offset

            ##### Chunk writing
            self.nextPartition.ioctl(6, 0)  # Erase first block

            blockNum = 0
            bytesRead = 0
            while bytesRead < bytesExpected:
                chunk = request.raw.read(4096)
                if len(chunk) == 0:
                    # connection closed
                    if bytesRead == bytesExpected:
                        break
                    else:
                        print("Download error!")
                        request.close()
                        return False

                print(
                    "Writing block {} of {}.  {} of {} bytes written".format(
                        blockNum, self.numBlocks, bytesRead, bytesExpected
                    ),
                    end="\r",
                )
                self.nextPartition.ioctl(6, blockNum)  # Erase block
                self.nextPartition.writeblocks(blockNum, chunk, 0)
                self.hash.update(chunk)

                blockNum += 1
                bytesRead += len(chunk)

            # Erase the remainder of the blocks
            for i in range(blockNum + 1, self.numBlocks):
                print(
                    "Writing block {} of {}.  {} of {} bytes written".format(
                        i, self.numBlocks, bytesRead, bytesExpected
                    ),
                    end="\r",
                )
                self.nextPartition.ioctl(6, i)

            print(
                "Firmware download+write finished.  Written {} of {} bytes.".format(
                    bytesRead, self.firmwareSize
                )
            )

        else:
            print("Error from server")
            request.close()
            return False

        request.close()
        return True

    def verifyHash(self):
        # firstHash = sha256()
        # buf = bytearray(self.blockSize)
        # self.nextPartition.readblocks(0, buf, 0)
        # firstHash.update(buf)
        # print(buf)
        # self.nextPartition.readblocks(1, buf, 0)
        # print("=================================")
        # print(buf)

        # for h in (firstHash, self.hashStart):
        #     hashstring = hexlify(h.digest()).decode("utf-8")
        #     print(hashstring)

        diskHash = sha256()
        buf = bytearray(self.blockSize)
        blocksToRead = floor(self.firmwareSize / self.blockSize)
        numBytes = 0
        for i in range(blocksToRead):
            self.nextPartition.readblocks(i, buf, 0)
            print(
                "Checking hash.  Block {} of {}.".format(i, blocksToRead),
                end="\r",
            )
            diskHash.update(buf)
            numBytes += self.blockSize
        # print(buf)
        # Read the last partial block
        self.nextPartition.readblocks(blocksToRead, buf, 0)
        remainder = self.firmwareSize % self.blockSize
        print(self.blockSize * blocksToRead + remainder)
        # print("firmware tail", buf)
        tail = buf[:remainder]
        # print(remainder, len(tail))
        # print("firmware tail", buf)
        # print(tail)
        diskHash.update(tail)
        numBytes += remainder
        print("Checked {} bytes of {}".format(numBytes, self.firmwareSize))

        downloadedHashString = hexlify(self.hash.digest()).decode("utf-8")
        diskHashString = hexlify(diskHash.digest()).decode("utf-8")
        print("Downloaded sha256: {}".format(downloadedHashString))
        print("Written sha256: {}".format(diskHashString))
        success = downloadedHashString == diskHashString
        if success:
            print("Hashes match!")
        else:
            print("Hashes don't match.")
        return success

    def setNextBoot(self):
        self.nextPartition.set_boot()

        # success = self.verifyHash()
        # if success:
        #     try:
        #         remove("__canary.py")
        #     except OSError:
        #         pass

    # print("reading firmware file")
    # with open("firmware.bin", "r") as f:
    #     while True:
    #         block = f.read(4WDT096)
    #         if len(block) == 0:
    #             break
    #         print(len(block))


if __name__ == "__main__":
    from config import Config

    config = Config()
    ota = OTAUpdater(config)
    # print(ota.get_available_versions())
    # ota.eraseNextPartition()
    ota.checkAndUpdate()
    # ota.updateFirmware()
    # ota.setNextBoot()
