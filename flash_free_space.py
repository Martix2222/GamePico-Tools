import os
stats = os.statvfs('/')
freeSpace = stats[0] * stats[3]
totalSpace = stats[0] * stats[2]
print('Free flash memory space:', freeSpace, 'bytes')
print('Total flash memory space:', totalSpace, 'bytes')