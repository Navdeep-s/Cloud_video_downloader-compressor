import sys,os

print(os.getcwd())


def download_torrent(file):

    os.system(f"aria2c \"{file}\" --seed-time=0 2> /dev/null > /dev/null ")
    # os.system(f"aria2c \"{file}\" --seed-time=0 ")
    print("done downloading")


print(sys.argv[1])
if(len(sys.argv)>1):
    download_torrent(sys.argv[1])

