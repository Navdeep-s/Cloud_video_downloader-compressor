import sys,os

print(os.getcwd())

exten = ["mp4","avi","mkv","mpeg"]
def compress(file):

    try:
        if(not os.path.isdir(file)):


           
            name = ".".join(file.split(".")[:-1])
            if(file.split(".")[-1] in exten):
                print(f"doing {file}")
                # os.system(f"ffmpeg -i \"{file}\" -c:v libx264 -crf 23 -preset faster -c:a aac -b:a 128k -movflags +faststart -vf scale=-2:720,format=yuv420p \"{name}_small.mp4\" 2> /dev/null > /dev/null ")
                os.system(f"ffmpeg -n -i \"{file}\" -vcodec libx264 -crf 28 -preset slower \"{name}_small.mp4\" 2> /dev/null > /dev/null ")                
                # os.system(f"ffmpeg -n -i \"{file}\" -vcodec libx265 -crf 28 \"{name}_small.mp4\" 2> /dev/null > /dev/null ")
                #os.system(f"ffmpeg -n -i \"{file}\" -vcodec libx264 -crf 37 -preset faster \"{name}.avi\" ")
                print("done")
                if(f"{name}_small.mp4" in os.listdir()):
                    os.remove(file)
        else:
            previous_folder = os.getcwd()	
            os.chdir(file)
            y = os.listdir()
            print("list of dirs y")
            for k in y:
                compress(k)
            os.chdir(previous_folder)
    except Exception as e:

        print("error in compress",e)


print(sys.argv[1])
if(len(sys.argv)>1):
    compress(sys.argv[1])

