# Installation
## Server Side Installation
* Copy the content of "server code" folder on your virtual machine or any machine (Only linux) on which you want to host your service.
* Go to the directory where you saved the content and run
* * **chmod +x install.sh**
* * **sudo ./install.sh**
* Provide your ip(type anything here it won't matter) and port (here be careful what you are typing because you are going to use it on client side)
* Now service will install and to check the status run the command systemctl status my_cloud.service You will the status = running
* To stop this service anything run **sudo systemctl stop my_cloud.service**
* To start it again run  **sudo systemctl start my_cloud.service**


## Client Side Installation

* Just copy the content of client code on your client pc
* open the config.json file and type change the ip value to ip of your server machine (make sure that ip is ecnlosed in double quotes) and port (without quotes)

# Playing with it - The fun begins

* To send any file or directory just run **python3 send.py absolute_path_of_file_or_folder_with_quotes** (remember the quoutes otherwise things can be very messy)
* Now the more interesting scripts is get.py. When you will run get.py it will give you list of all the files which are there in your server download_folder
  If there are none it will exit. So use send.py atleast once to make sure that you have atleast one file in your download folder on server.
  
* Now you can select a file or folder by typing its index.
  
  It will give you 4 option
  * * **dowload** - Choosing this one will download the file or complete directory (if its a directory) on your pc
  * * **compress** - Choosing this will result in compressing the video file. It will only work on video files. If you choose this option on a directory it will recursive compress all the video files present in it. 
  * * **delete** - this will delete any file or folder which you selected
  * * **download torrent** - here name is bit confusing but this can be use to download any link like direct link, magnet link, ftp link etc. You can also download torrent from a file if you don't have a magnet by first sending that torrent file to the server using send.py and then choosing this option in get.py and provide the complete name of the torrent file as input. 
  
  * For files like mp4, mpeg, avi etc one another option **download screenshot** is also provided which you can use to get a tiled screenshot image from the whole video.It will first ask you number of screen shot you want and then after little bit of process will give you the screenshot file.
  
* If you choose a directory it will give you one option to get inside it 
  
* Also if you have knowledge about ffmpeg you can play with the command setting in compress.py to achieve desired results.
### Note
whenever you run get.py it will display the list of pending task which means those downlaodes or compressions are not done yet so don't download or delete those things.
  
# Use Cases

* If you want to watch a movie but you don't have a great data pack. You can download it on vm and compress it and download it to save your data pack
* Torrent download fast on virtual machines because they are connected to high speed. So what I usually do is whenever I want to download a torrent just first downlaod it on your vm because vm can run 24/7 as compare to your pc. When it downloads there, Then download it from there only those files which you really want
* You can also use send.py and get.py on google collab to transafer data from vm to your google drive directly without having to download on your machine.
  
## Notes 
* the ip address in the config file of client side should be the ip on which you server machine is hosted. Suppose your machine is in a private netwok like in your institute or organisation then the ip will be that's mahines local ip not public ip.
* To connect over the internet you should make sure that port forwarding on your server machine is on and there is a port bound rule which bound the port which is there in the config file of server and client side.
* For any queries raise an issue :)
  
  
  
  

