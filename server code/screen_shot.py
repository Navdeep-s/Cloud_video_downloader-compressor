import cv2
import os,sys
import datetime
def give_commands(filename,n):
    
    
  
    # create video capture object
    data = cv2.VideoCapture(filename)
      
    # count the number of frames
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = int(data.get(cv2.CAP_PROP_FPS))
      
    # calculate dusration of the video
    video_time = int(frames / fps)

    time_gap = (video_time//n)+1

    time_list =[]
    count =0

    stri = '''-vf  "drawtext=fontsize=100:fontcolor=white:box=1:boxcolor=black:x=(W-tw)/2:y=H-th-10:text='''
    for k in range(time_gap,video_time,time_gap):
        timing =str(datetime.timedelta(seconds=k))
        printed_value = "\\:".join(timing.split(":"))
        time_list.append(f"ffmpeg -ss {timing} -i \"{filename}\" {stri}'{printed_value}'\" -frames:v 1  temp{count}.jpg 2> /dev/null > /dev/null")
        count = count + 1
    
    return time_list

# define a function for vertically
# concatenating images of the
# same size and horizontally
def concat_vh(list_2d):
    
    # return final image
    return cv2.vconcat([cv2.hconcat(list_h)
                        for list_h in list_2d])
# image resizing

if(len(sys.argv)<3):
    print(f"Usage screen_shot file_name number_of_screen_shots")
    sys.exit()


y = give_commands(sys.argv[1],int(sys.argv[2]))

print(len(y))


count = 0
Image_list = []
Temp_list=[]
for k in y:
    os.system(k)
    file_name= f'temp{count}.jpg'
    img = cv2.imread(file_name)
    print(file_name)
    try:
        print(img.shape)
    except Exception:
        continue
    img1 = cv2.resize(img, dsize = (0,0),fx = 0.5, fy = 0.5)

    Temp_list.append(img1)
    if(len(Temp_list)>=3):
        Image_list.append(Temp_list)
        Temp_list = []
    count = count +1

    os.remove(file_name)
    # print(k)

if(len(Temp_list)!=0):
    while(len(Temp_list)<3):
        Temp_list.append(Temp_list[0])
    Image_list.append(Temp_list)



img_tile = concat_vh(Image_list)

cv2.imwrite(sys.argv[1]+"_screen_shot.jpg", img_tile)