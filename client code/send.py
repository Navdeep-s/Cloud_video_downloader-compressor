import json
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
			
			to_send = bytes(text,"utf-16",errors = 'replace')
			text_size = len(to_send)
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
			text = text_bytes.decode("utf-16",errors = 'replace')
			return text
		except Exception as e:
			print("error in recv_text",e)
			return -1

	#name should be present on pwd
	def send_file(self,name):
		print(f"sending file '{name}'")

		try:

			file_size  = os.path.getsize(name)
			self.send_int(FILE,1)
			#sending name
			self.send_text(name)
			#sending size
			self.send_int(file_size,8)

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
			
			name = self.recv_text()
			print(f"recieving file '{name}'")
			file_size= self.recv_int(8)
			
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
					print("something wierd")
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
			self.send_int(FOLDER,1)
			# to tell the size of name of folder
			self.send_text(folder_name)
			
			


			# self.client.sendall(name_size.to_bytes(4, byteorder='big'))
			# name_size= int.from_bytes(name_size_bytes, byteorder='big')
			number_of_files  = len(y)
			
			#sending number of files
			self.send_int(number_of_files,4)
			

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

			item_type = self.recv_int(1)

			if(item_type==FOLDER):

				folder_name = self.recv_text()
				number_of_files= self.recv_int(4)
				
				
				
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
SEND = 1
GET = 2
import time
FOLDER = 32
FILE = 31




if(len(sys.argv)<2):
	print("Usage for window : python <folder/file_name>")
	print("Usage for others : python3 <folder/file_name>")
	sys.exit()


if(not os.path.exists(sys.argv[1])):
	print(f"'{sys.argv[1]}' named file or folder doesn't exist")
	sys.exit()

os.chdir(os.path.dirname(sys.argv[1]))

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

print("waiting to connect please wait .....")
client.connect((host_ip, port))
client.sendall(SEND.to_bytes(1, byteorder='big'))

cli = my_ft(client)

# client.sendall(GET.to_bytes(1, byteorder='big'))
print("Connected to the server")
print("but if only this line is showing meaning somebody else request is processing so try again or wait")


send_name = os.path.basename(sys.argv[1])


if(os.path.isdir(send_name)):
	cli.send_folder(send_name)
else:
	cli.send_file(send_name)
try:
	client.close()
except Exception :
	pass






