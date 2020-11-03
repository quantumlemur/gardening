print("boot/__init__.py loaded")


def now():
    return time() + 946684800


def printBootInfo():
    print("==============================")
    print("Booting at time: {}".format(time()))
    part = Partition(Partition.RUNNING).info()
    print(part.info())

    print(
        "Current version: {}.  Commit hash: {}".format(
            currentCommitTag, currentCommitHash
        )
    )
    print("==============================")