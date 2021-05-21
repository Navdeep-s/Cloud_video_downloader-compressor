import json
import colorama
from colorama import Fore, Back, Style
colorama.init()
import os,sys
import socket # for socket

BUFFER_SIZE =1024
DISPLAY_TIME = 1024
SEND = 1
GET = 2
import time
FOLDER = 32
FILE = 31
TEXT = 33



config = open("config.json")
config_data = json.load(config)
config.close()


# define Python user-defined exceptions
class Error(Exception):
    """Base class for other exceptions"""
    pass


class reliable_error(Error):
    """Raised when the input value is too small"""
    pass

class my_ft:

	def __init__(self, client):
		self.client = client

	

	def reliable_recv(self,size):
		u = self.client.recv(size)
		while(not len(u)==size):
			recv_bytes = self.client.recv(size-len(u))
			if(len(recv_bytes)==0):
				print("Error in reliable_recv")
				raise reliable_error
			u = u + recv_bytes
		return u
		

	def send_int(self,my_int,size = 4):
		try:
			self.client.sendall(my_int.to_bytes(size, byteorder='big'))
			return 1
		except Exception as e:
			print("error in send_int",e)
			return -1

	def recv_int(self,size = 4):
		try:
			my_int_bytes = self.reliable_recv(size)
			my_int= int.from_bytes(my_int_bytes, byteorder='big')
			return my_int
		except Exception as e:
			print("error in recv_int",e)
			return -1



	def send_text(self,text):
		try:
			
			to_send = bytes(text,"utf-8",errors = 'replace')
			text_size = len(to_send)
			# self.client.sendall(TEXT.to_bytes(1,byteorder='big'))
			self.client.sendall(text_size.to_bytes(4, byteorder='big'))
			self.client.sendall(to_send)
			return 1
		except Exception as e:
			print("error in send_text",e)
			return -1

	
	def recv_text(self):
		try:
			text_size_bytes = self.reliable_recv(4)
			text_size= int.from_bytes(text_size_bytes, byteorder='big')
			text_bytes = self.reliable_recv(text_size)
			text = text_bytes.decode("utf-8",errors = 'replace')
			return text
		except Exception as e:
			print("error in recv_text",e)
			return -1

	#name should be present on pwd
	def send_file(self,name):
		print(f"sending file '{name}'")

		try:
			file_size  = os.path.getsize(name)
			name_size = len(name)

			self.client.sendall(FILE.to_bytes(1,byteorder='big'))
			#int
			self.client.sendall(name_size.to_bytes(4, byteorder='big'))
			#str
			self.client.sendall(bytes(name,"utf-8"))

			#long long
			self.client.sendall(file_size.to_bytes(8, byteorder='big'))

			file = open(name,"rb")

			bytes_sent = 0
			count = 0
			while(bytes_sent!=file_size):
				count=count+1
				if(count%DISPLAY_TIME==0):
					print("\r {} % done".format(int(bytes_sent*100/file_size)),end="")
				sending_size = BUFFER_SIZE
				if(sending_size>file_size-bytes_sent):
					sending_size = file_size-bytes_sent
				read = file.read(sending_size)
				self.client.sendall(read)
				bytes_sent = bytes_sent +len(read)
			print("\r100 % done")
			return 1
		except Exception as e: 
			print("Eror in send_file",e)
			return -1

	#saving folder shloud be present in pwd 
	def recieve_file(self,saving_folder):
		previous_folder = os.getcwd()
		os.chdir(saving_folder)
		try:
			name_size_bytes = self.reliable_recv(4)
			name_size= int.from_bytes(name_size_bytes, byteorder='big')
			name_bytes = self.reliable_recv(name_size)
			name = name_bytes.decode("utf-8")
			print(f"recieving file '{name}'")


			file_size_bytes = self.reliable_recv(8)
			file_size= int.from_bytes(file_size_bytes, byteorder='big')
			
			file = open(name,"wb");
			bytes_recived = 0
			count = 0
			while(bytes_recived<file_size):
				count=count+1
				if(count%DISPLAY_TIME==0):
					print("\r {} % done".format(int(bytes_recived*100/file_size)),end="")
				size_to_recieve = BUFFER_SIZE
				remaining_bytes = file_size - bytes_recived
				if(size_to_recieve > remaining_bytes):
					size_to_recieve = remaining_bytes

				data_bytes = self.client.recv(size_to_recieve)
				if(len(data_bytes)==0):
					os.chdir(previous_folder)
					return -1
				
				bytes_recived = bytes_recived +len(data_bytes)
				file.write(data_bytes)

			print("\r100 % done")
			file.close()

			os.chdir(previous_folder)
			return 1
		except Exception as e :
			print("Eror in recieve_file",e)
			os.chdir(previous_folder)
			return -1

	#chdir should be looked once again
	#folder name should be present on pwd
	def send_folder(self,folder_name):
		try:
			print(f"sending folder '{folder_name}'")
			previous_folder = os.getcwd()
			y = os.listdir(folder_name)
			folder_name = os.path.split(folder_name)[1]
			name_size = len(folder_name)
			# to tell that folder is being sent
			self.client.sendall(FOLDER.to_bytes(1,byteorder='big'))
			# to tell the size of name of folder
			self.client.sendall(name_size.to_bytes(4, byteorder='big'))
			#sending name of the folder
			self.client.sendall(bytes(folder_name,"utf-8"))


			# self.client.sendall(name_size.to_bytes(4, byteorder='big'))
			# name_size= int.from_bytes(name_size_bytes, byteorder='big')
			number_of_files  = len(y)
			
			#sending number of files
			self.client.sendall(number_of_files.to_bytes(4,byteorder='big'))

			#go inside that folder
			os.chdir(folder_name)
			for k in y:
				if(os.path.isdir(k)):
					if(self.send_folder(k)==-1):
						os.chdir(previous_folder)
						return -1
				else:
					if(self.send_file(k)==-1):
						os.chdir(previous_folder)
						return -1

			#get out of the folder
			os.chdir(previous_folder)
			return 1
		except Exception as e:
			print("Error in sending folder",e)
			os.chdir(previous_folder)
			return -1


	#chdir should be looked once again
	#saving_folder should be presented in pwd
	def recieve_something(self,saving_folder):

		try:

			previous_folder = os.getcwd()
			os.chdir(saving_folder)

			item_type_bytes = self.reliable_recv(1)
			item_type= int.from_bytes(item_type_bytes, byteorder='big')

			if(item_type==FOLDER):
				folder_name_size_bytes = self.reliable_recv(4)
				folder_name_size= int.from_bytes(folder_name_size_bytes, byteorder='big')
				folder_name_bytes = self.reliable_recv(folder_name_size)
				folder_name = folder_name_bytes.decode("utf-8")

				number_of_files_bytes = self.reliable_recv(4)
				number_of_files= int.from_bytes(number_of_files_bytes, byteorder='big')
				
				
				if(not os.path.exists(folder_name)):
					os.mkdir(folder_name)
				print(f"recieving folder '{folder_name}'")
				for k in range(number_of_files):
					if(self.recieve_something(folder_name)==-1):
						os.chdir(previous_folder)
						return -1


			elif(item_type==FILE):
				# print("geting a file")
				if(self.recieve_file(".")==-1):
					os.chdir(previous_folder)
					return -1
			
			os.chdir(previous_folder)
			return 1
		except Exception as e:
			os.chdir(previous_folder)
			print("Error in reciving folder",e)
			return -1






BUFFER_SIZE =1024
DISPLAY_TIME = 1024
ROOT_FOLDER = os.getcwd()
INPUT_FOLDER = os.path.join(ROOT_FOLDER,"input")
OUTPUT_FOLDER = os.path.join(ROOT_FOLDER,"output")
SEND = 1
GET = 2
import time



GET_INSIDE =34
DELETE =45
DOWNLOAD =67
COMPRESS = 57
TORRENT = 36
SCREENSHOT = 91



choices_option = [GET_INSIDE,DOWNLOAD,COMPRESS,DELETE,TORRENT,SCREENSHOT]




def display_folder_contect(u):
	
	u = " ----- folder".join(u.split("\n1"))
	u = " ----- file".join(u.split("\n0"))
	count = 0
	lis = []
	for k in u.splitlines():
		print(f"{count}.) ",end="")
		temp_lis =[]
		if(k.endswith("----- folder")):
			temp_lis.append(1)
			temp_lis.append(0)
			print(Fore.BLUE+k.split("----- folder")[0]+Style.RESET_ALL)
		else:
			temp_lis.append(0)
			print(Fore.GREEN+k.split("----- file")[0]+Style.RESET_ALL)

			
			if(((k.split(" ----- file")[0]).split(".")[-1].lower()) in ["mkv","mpeg","mp4","avi","mov"]):
				temp_lis.append(1)
			else:
				temp_lis.append(0)

		lis.append(temp_lis)
		count = count+1
	return lis


def get_input_index(count,message):
	while True:
		try:
			index = int(input(message))
			if(-1<index<count):
				return index
			print(f"please provide an int of size 0 to {count-1}")
			
		except Exception as e:
				print(f"please provide an int of size 0 to {count-1}")
				



def getter(ft):
	try:
		u = ft.recv_text()
		if(u==-1):
			# print("Error while recieving text")
			return 

		lis = display_folder_contect(u)
		count = len(lis)
		if(count==0):
			print("No files is there in cloud first upload then use this script")
			sys.exit()
		index = get_input_index(count,f"select any folder or file you want from 0 to {count-1}\n")
		if(lis[index][0]==1):
			message = "0 to get inside\n1 to download\n2 to compress\n3 to delete\n4 to download torrent\n"
			choice = choices_option[get_input_index(len(choices_option),message)]
			

		elif(lis[index][1]==0):
			message = "0 to download\n1 to compress\n2 to delete\n3 to download torrent\n"
			choice = choices_option[get_input_index(len(choices_option),message)+1]
		else:
			message = "0 to download\n1 to compress\n2 to delete\n3 to download torrent\n4 to download screenshot\n"
			choice = choices_option[get_input_index(len(choices_option),message)+1]

			
		
		ft.send_int(index)
		ft.send_int(choice,1)
		if(choice == GET_INSIDE):
			getter(ft)
		elif(choice ==DOWNLOAD):
			ft.recieve_something(".")
		elif(choice==COMPRESS):
			print("compression of file has been started Don't send any command now")
		elif(choice==DELETE):
			print("Deletion has been started")
		elif(choice==TORRENT):
			magnet_link = input("provide the magnet link")
			ft.send_text(magnet_link)
			print("Download has been started")
		elif(choice==SCREENSHOT):
			number_of_ss = get_input_index(300,"How many screen shot do you want")
			ft.send_int(number_of_ss)
			ft.recieve_something(".")
	except Exception as e:
		print("error in getter",e)






try:
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# print ("Socket successfully created")
except socket.error as err:
	print ("socket creation failed with error %s" %(err))

try:
	port = config_data["port"]
	host_ip = config_data["ip"]
except Exception:
	print("[!!] your configuration file is corrupted \n[!!] copy it from server again from the folder where you install this or edit is by yourself changing ip an port to correct values")
	sys.exit()
# host_ip = "localhost"

print("waiting to connect please wait .....")
client.connect((host_ip, port))
# client.sendall(SEND.to_bytes(1, byteorder='big'))
client.sendall(GET.to_bytes(1, byteorder='big'))
print("Connected to the server")
print("but if only this line is showing meaning somebody else request is processing so try again or wait")

ft = my_ft(client)
# send_all_files(client)
# time.sleep(3)
getter(ft)
client.close()





