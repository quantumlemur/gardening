from esp32 import Partition
import os


print(Partition.find(subtype=0xFF))

running = Partition(Partition.RUNNING)
print(running.info())

# nextPartition = Partition(Paritition.RUNNING).get_next_update()
# print(nextPartition.info())
# nextPartition.set_boot()

import os

# os.umount("/")
# print("hi")
# os.VfsLfs2.mkfs(bdev)
# print("asd")
# os.mount(bdev, "/")
# print("asda")

print(os.listdir("/"))

# import os, pyb
# os.umount('/flash')
# p1 = pyb.Flash(start=0, len=256*1024)
# p2 = pyb.Flash(start=256*1024)
# os.VfsFat.mkfs(p1)
# os.VfsLfs2.mkfs(p2)
# os.mount(p1, '/flash')
# os.mount(p2, '/data')
# os.chdir('/flash')