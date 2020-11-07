from esp32 import Partition
from math import ceil, floor
from os import remove
import socket
from ubinascii import hexlify
from uhashlib import sha256



class OTAUpdater:
    def __init__(self):
        self.nextPartition = Partition(Partition.RUNNING).get_next_update()
        self.numBlocks = self.nextPartition.ioctl(4, None)
        self.blockSize = self.nextPartition.ioctl(5, None)
        self.hash = sha256()
        self.hashStart = sha256()
        self.firmwareSize = 1427840

    def eraseNextPartition(self):
        print("Erasing partition...")
        for i in range(self.numBlocks):
            print("erasing block {} of {}".format(i, self.numBlocks), end="\r")
            self.nextPartition.ioctl(6, i)
        print("Partition erased!")

    def parseHeaders(self, headerString):
        """Parse header string and return dictionary of headers"""
        headerStrings = headerString.split(b"\r\n")
        headers = {
            row.split(b":")[0]
            .decode("utf-8")
            .strip(): row.split(b":")[1]
            .decode("utf-8")
            .strip()
            for row in headerStrings
            if row.find(b":") != -1
        }
        return headers

    def updateFirmware(self):
        print("Downloading new firmware")
        addr = (b"192.168.86.20", 5000)
        s = socket.socket()
        s.settimeout(10)
        s.connect(addr)
        request = b"GET /static/application.bin HTTP/1.0\r\nHost: 192.168.86.20\r\n\r\n"
        s.send(request)

        response = s.recv(4096)
        if response == b"HTTP/1.0 200 OK\r\n":
            headerBuf = b""

            chunk = s.recv(4096)
            while chunk.find(b"\xe9") == -1:
                headerBuf += chunk

                # loop and discard data until we get a chunk that includes the magic start byte
                # to indicate the start of the firmware image
                chunk = s.recv(4096)
            headerBuf += chunk

            # Parse headers
            headerBuf = headerBuf[: headerBuf.find(b"\xe9")]
            headers = self.parseHeaders(headerBuf)
            bytesToDownload = int(headers["Content-Length"])
            self.firmwareSize = bytesToDownload
            expectedBlocks = ceil(bytesToDownload / self.blockSize)

            # discard the contents before the magic start byte
            chunk = chunk[chunk.find(b"\xe9") :]

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
            buf = b""
            while len(chunk) > 0:
                buf += chunk

                while len(buf) >= self.blockSize:

                    # Write out a block once we have enough data
                    print(
                        "Writing block {} of {}.  Buffer length: {}".format(
                            blockNum, expectedBlocks, len(buf)
                        ),
                        end="\r",
                    )
                    self.nextPartition.ioctl(6, blockNum)  # Erase block
                    blockToWrite = buf[: self.blockSize]
                    self.nextPartition.writeblocks(blockNum, blockToWrite, 0)
                    self.hash.update(blockToWrite)
                    if blockNum == 0:
                        self.hashStart.update(blockToWrite)
                    blockNum += 1
                    buf = buf[self.blockSize :]

                chunk = s.recv(4096)

            print("")

            # Write out the last bit of the buffer to a full block
            # print(buf)
            print("=======================================")
            blockToWrite = bytearray(self.blockSize)
            blockToWrite[: len(buf)] = buf
            self.nextPartition.ioctl(6, blockNum)  # erase
            self.nextPartition.writeblocks(blockNum, buf, 0)  # write
            self.hash.update(buf)
            bytesWritten = blockNum * self.blockSize + len(buf)

            # Erase the remainder of the blocks
            # zeros = bytearray(self.blockSize)
            for i in range(blockNum + 1, self.numBlocks):
                print(
                    "Erasing remainder of flash... block {} of {}".format(
                        i, self.numBlocks
                    ),
                    end="\r",
                )
                self.nextPartition.ioctl(6, i)
                # self.nextPartition.writeblocks(i, zeros, 0)

            print(
                "Firmware download+write finished.  Written {} of {} bytes.".format(
                    bytesWritten, bytesToDownload
                )
            )

        else:
            print("Error from server")

        s.close()

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
        success = self.verifyHash()
        if success:
            self.nextPartition.set_boot()
            remove("__canary.py")

    # print("reading firmware file")
    # with open("firmware.bin", "r") as f:
    #     while True:
    #         block = f.read(4WDT096)
    #         if len(block) == 0:
    #             break
    #         print(len(block))


if __name__ == "__main__":
    ota = OTAUpdater()
    # ota.eraseNextPartition()
    ota.updateFirmware()
    ota.setNextBoot()
