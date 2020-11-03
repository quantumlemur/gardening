from esp32 import Partition
from machine import reset
from os import listdir, mount, remove, rename, umount, urandom
from time import time
from ubinascii import hexlify
from uhashlib import sha256


criticalFiles = [
    "main.py",
    "wifi.py",
    "config.py",
    "updater.py",
    "credentials.py",
]
upgradeSuccessFile = "__UPGRADE_SUCCESSFUL"
upgradeFile = "__UPGRADE_IN_PROGRESS"
canaryFile = "__canary.py"

print("==============================")
print("Time: {}".format(time()))
part = Partition(Partition.RUNNING)
print(part.info())
print("==============================")

# umount("/")
# mount(bdev, "/")


def hashFile(fname):
    hash_sha256 = sha256()
    with open(fname, "rb") as f:
        chunk = f.read(4096)
        while chunk != b"":
            hash_sha256.update(chunk)
            chunk = f.read(4096)
    hashString = hexlify(hash_sha256.digest()).decode("utf-8")
    if fname == canaryFile:
        with open(fname, "r") as f:
            print(f.read(4096))
        print("Hash {}: {}".format(fname, hashString))
    return hashString


def alterCanary():
    print("Altering canary")

    # no cheating!  make sure it's actually gone and force the updater to re-fetch
    if "{}.new".format(canaryFile) in listdir():
        remove("{}.new".format(canaryFile))

    # write random data to the existing canary file
    with open(canaryFile, "w") as f:
        f.write(hexlify(urandom(10)).decode("utf-8"))


def copyFile(oldFile, newFile):
    print("Copying {} to {}".format(oldFile, newFile))
    with open(oldFile, "rb") as old:
        with open(newFile, "wb") as new:
            chunk = old.read(4096)
            while chunk != b"":
                new.write(chunk)
                chunk = old.read(4096)
    oldHash = hashFile(oldFile)
    newHash = hashFile(newFile)
    return oldHash == newHash


def upgradeSuccessful():
    print("upgrade sucessful")
    if upgradeFile in listdir():
        remove(upgradeFile)
    if upgradeSuccessFile in listdir():
        remove(upgradeSuccessFile)


def upgradeFailed():
    print("upgrade failed")
    for fname in criticalFiles:
        copyFile("{}.bak".format(fname), fname)
    remove(upgradeFile)
    # sync()
    reset()

    # now we'll go on to boot, sync with the server, and run everything to test
    # Hopefully the reverted files can resync and download new copies and we'll try again next time


# State actions


def startUpgrade():
    print("start upgrade")
    alterCanary()

    copiesSuccessful = True
    for fname in criticalFiles:
        copiesSuccessful = copiesSuccessful and copyFile(
            fname, "{}.baktmp".format(fname)
        )
    if copiesSuccessful:
        print("All file copies successful")
        with open(upgradeFile, "w") as f:
            f.write("zzz")
        for fname in criticalFiles:
            print("Moving .baktmp to .bak and .new to .py: {}".format(fname))
            # print("Renaming .baktmp files to .bak")
            rename("{}.baktmp".format(fname), "{}.bak".format(fname))
            # print("Renaming .new files to .py")
            if "{}.new".format(fname) in listdir():
                rename("{}.new".format(fname), fname)
        print("All files configured for test run")
    else:
        # try again...
        print("File copies failed.  Restarting and trying again.")
        reset()

        # sync()
        # now we'll go on to boot, sync with the server, and run everything to test


def continueOldUpgrade():
    print("continue old upgrade")
    alterCanary()
    for fname in criticalFiles:
        if "{}.new".format(fname) in listdir():
            rename("{}.new".format(fname), fname)
    # sync()
    # now we'll go on to boot, sync with the server, and run everything to test


def evaluateCompletedUpgrade():
    print("evaluate completed upgrade")

    canaryHash = hashFile("{}.new".format(canaryFile))
    canaryGood = (
        canaryHash == "52b5ba36d63e92afe01175a4c43a8fc1c577db7937d5447702bb0817032ae074"
    )
    runGood = upgradeSuccessFile in listdir()
    succeeded = canaryGood and runGood
    print("===========================================")
    print("Canary passed check: {}".format(canaryGood))
    print("Upgrade success file present: {}".format(runGood))
    print("All upgrade checks passed: {}".format(succeeded))
    print("===========================================")

    if succeeded:
        upgradeSuccessful()
    else:
        upgradeFailed()


# Find state
currentFiles = listdir()
upgradeInProgress = upgradeFile in currentFiles

foundNewFiles = False
for fname in criticalFiles:
    if "{}.new".format(fname) in currentFiles:
        foundNewFiles = True

# Dispatch state
if foundNewFiles and not upgradeInProgress:
    startUpgrade()
elif foundNewFiles and upgradeInProgress:
    continueOldUpgrade()
elif (not foundNewFiles) and upgradeInProgress:
    evaluateCompletedUpgrade()
elif (not foundNewFiles) and (not upgradeInProgress):
    pass


if upgradeSuccessFile in listdir():
    remove(upgradeSuccessFile)


print(listdir())

# CG    canary good
# UIP   upgradeinprogress exists
# US    upgradesuccessful exists
# .new  .new critical file exists

# .new  UIP CG  US  actions
#   N   N   N   N   -          normal operation, no upgrade available
#   Y   N   N   N   BCUT       start of normal upgrade cycle.
#   N   Y   N   N   RHD        upgrade cycle failed.  revert critical files.  hard restart so we connect to wifi next boot
#   Y   Y   N   N   TC         upgrade in progress, got more files to try to update.  don't overwrite the backups.
#   N   N   Y   N   -
#   Y   N   Y   N   BCUT       start of normal upgrade cycle
#   N   Y   Y   N   RHD        upgrade failed after canary rewrite but still failed.  revert
#   Y   Y   Y   N   TC         upgrade in progress, got more files. don't overwrite backups
#   N   N?  N   Y   RHD        upgrade "succeeded" but canary failed.  revert
#   Y   N   N   Y   TC         upgrade in progress, got more files
#   N   Y   N   Y   RHD        upgrade failed.  revert
#   Y   Y   N   Y   TC         upgrade in progress, got more files
#   N   N?  Y   Y   D          lingering upgradesuccessful
#   Y   N   Y   Y   BCUT       start of normal upgrade cycle
#   N   Y   Y   Y   D          successful upgrade cycle
#   Y   Y   Y   Y   TC         upgrade in progress, got more files.

# - normal operation, no upgrade available.  delete upgradesuccessful and upgradeingprogress if present, for cleanup
# BHUT - start normal upgrade cycle
# TC - upgrade in progress, got more files
# RHD - upgrade cycle failed, revert

#   N   nothing
#   C   modify Canary
#   B   backup criticalFile.py to criticalFile.bak
#   U   create upgradeinprogressfile
#   D   delete upgradesuccessful and upgradeinprogress
#   R   revert .bak files to .py files
#   T   try renaming .new files to .py files
#   H   hard restart

# if criticalFile.new exists
#   create upgradeinprogress file
#   copy criticalFile.py to criticalFile.bak
#   modify canary.py

# if upgradeinprogress file exists, then we're back after an upgrade cycle
#   is canary.py back to what it should be?  (verify sha256 match)
#   does upgradesuccessfile exist?
#   if yes:
#       remove upgradesuccessfile and upgradeinprogress file (leave the upgrade cycle).  remove .bak files?
#   if no: upgrade cycle failed
#       copy .bak files back to .py files

# modifications to other files:
#   should always connect to wifi if upgradeinprogress exists
#   can write upgradesuccessfile at end of main.py (don't need to go all the way to the end)
#   main.py should call masterActions.py
#   Should main.py now put it back to sleep?  why not?
