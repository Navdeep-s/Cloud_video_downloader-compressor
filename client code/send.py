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

	def print_spaces(self,spaces):
		if(spaces>0):
			print((spaces-1)*"│  "+"├─",end=" ")

	def __init__(self, client):
		self.client = client
		self.spaces = 0

	

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


	#file_path - absolute path of the file
	def send_file(self,file_path,spaces=0):


		file_name = os.path.basename(file_path)
		self.print_spaces(spaces)
		print(f"sending file '{file_name}'")

		try:

			file_size  = os.path.getsize(file_path)
			self.send_int(FILE,1)
			#sending name
			self.send_text(file_name)
			#sending size
			self.send_int(file_size,8)

			file = open(file_path,"rb")

			bytes_sent = 0
			count = 0
			while(bytes_sent!=file_size):
				count=count+1
				if(count%DISPLAY_TIME==0):
					print("\r",end="")
					self.print_spaces(spaces)
					print(" {} % done".format(int(bytes_sent*100/file_size)),end="")
				sending_size = BUFFER_SIZE
				if(sending_size>file_size-bytes_sent):
					sending_size = file_size-bytes_sent
				read = file.read(sending_size)
				self.client.sendall(read)
				bytes_sent = bytes_sent +len(read)

			print("\r",end="")
			self.print_spaces(spaces)
			print("100 % done")
			return 1
		except Exception as e: 
			print("Eror in send_file",e)
			return -1

	#saving_folder_path - absolute path of folder in which you want to recieve the file
	def recieve_file(self,saving_folder_path,spaces=0):
		try:
			
			file_name = self.recv_text()
			self.print_spaces(spaces)
			print(f"recieving file '{file_name}'")
			file_size= self.recv_int(8)

			saving_file_path = os.path.join(saving_folder_path,file_name)
			file = open(saving_file_path,"wb");
			bytes_recived = 0
			count = 0
			while(bytes_recived<file_size):
				count=count+1
				if(count%DISPLAY_TIME==0):
					print("\r",end="")
					self.print_spaces(spaces)
					print(" {} % done".format(int(bytes_recived*100/file_size)),end="")
				size_to_recieve = BUFFER_SIZE
				remaining_bytes = file_size - bytes_recived
				if(size_to_recieve > remaining_bytes):
					size_to_recieve = remaining_bytes

				data_bytes = self.client.recv(size_to_recieve)
				if(len(data_bytes)==0):
					print("something wierd")
					return -1
				
				bytes_recived = bytes_recived +len(data_bytes)
				file.write(data_bytes)

			print("\r",end="")
			self.print_spaces(spaces)
			print("100 % done")
			file.close()

			return 1
		except Exception as e :
			print("Eror in recieve_file",e)
			return -1

	#folder_path - absolute path of the folder 
	def send_folder(self,folder_path,spaces=0):
		try:
			folder_name = os.path.basename(folder_path)
			self.print_spaces(spaces)
			print(f"sending folder '{folder_name}'")

			folder_content = [os.path.join(folder_path,x) for x in os.listdir(folder_path)]
			
			
			# to tell that folder is being sent
			self.send_int(FOLDER,1)
			# to tell the size of name of folder
			self.send_text(folder_name)
			
			


			# self.client.sendall(name_size.to_bytes(4, byteorder='big'))
			# name_size= int.from_bytes(name_size_bytes, byteorder='big')
			number_of_files  = len(folder_content)
			
			#sending number of files
			self.send_int(number_of_files,4)
			

			#go inside that folder

			
			for k in folder_content:
				if(os.path.isdir(k)):
					if(self.send_folder(k,spaces+1)==-1):
						
						return -1
				else:
					if(self.send_file(k,spaces+1)==-1):
						
						return -1

			#get out of the folder
			
			return 1
		except Exception as e:
			print("Error in sending folder",e)
			
			return -1


	#saving_folder_path - absolute path where you want to save the file
	def recieve_something(self,saving_folder_path,spaces=0):

		try:


			item_type = self.recv_int(1)

			if(item_type==FOLDER):

				folder_name = self.recv_text()
				number_of_files= self.recv_int(4)
				
				new_folder_path = os.path.join(saving_folder_path,folder_name)
				
				if(not os.path.exists(new_folder_path)):
					os.mkdir(new_folder_path)

				self.print_spaces(spaces)
				print(f"recieving folder '{folder_name}'")
				for k in range(number_of_files):
					if(self.recieve_something(new_folder_path,spaces+1)==-1):
						
						return -1


			elif(item_type==FILE):
				# print("geting a file")
				if(self.recieve_file(saving_folder_path,spaces)==-1):
					
					return -1
			
			return 1
		except Exception as e:

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

dirName = os.path.dirname(sys.argv[1])
if(dirName!=""):
	os.chdir(dirName)
# os.chdir(os.path.dirname(sys.argv[1]))

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






