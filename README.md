# Installation
## Server Side Installation
* Copy the content of "server code" folder on your virtual machine or any machine (Only linux) on which you want to host your service.
* Go to the directory where you saved the content and run
* * #chmod +x install.sh#
* * #sudo ./install.sh#
* Provide your ip(type anything here it won't matter) and port (here be careful what you are typing because you are going to use it on client side)
* Now service will install and to check the status run the command systemctl status my_cloud.service You will the status = running
* To stop this service anything run *sudo sysemctl stop my_cloud.service*
* To start it again run  *sudo sysemctl start my_cloud.service*


## Client Side Installation

* Just copy the content of client code on your client pc
* open the config.json file and type change the ip value to ip of your server machine (make sure that ip is ecnlosed in double quotes) and port (without quotes)

# Playing with it - The fun begins

* To send any file or directory just run <python3 send.py absolute_path_of_file_or_folder_with_quotes> (remember the quoutes otherwise things can be very messy)
* Now the more interesting scripts is get.py. When you will run get.py it will give you list of all the files which are there in your server download_folder
  If there are none it will exit. So use send.py atleast once to make sure that you have atleast one file in your download folder on server.
  
* Now you can select a file or folder by typing its index.
  
  It will give you 4 option
  * * to dowload - Choosing this one will download the file or complete directory (if its a directory) on your pc
  * * to compress - Choosing this will result in compressing the video file. It will only work on video files. If you choose this option on a directory it will recursive compress all the video files present in it
  * * to delete - this will delete any file or folder which you selected
  * * to download torrent - here name is bit confusing but this can be use to download any link like direct link, magnet link, ftp link etc. You can also download torrent from a file if you don't have a magnet by first sending that torrent file to the server using send.py and then choosing this option in get.py and provide the complete name of the torrent file as input.
  
* If you choose a directory it will give you one option to get inside it 
  
* Also if you have knowledge about ffmpeg you can play with the command setting in compress.py to achieve desired results.
  
  
  
  
  
  
  
