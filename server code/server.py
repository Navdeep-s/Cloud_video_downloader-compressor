# first of all import the socket library 
import os,sys
import socket # for socket
import json

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





BUFFER_SIZE = 1024
ROOT_FOLDER = os.getcwd()
INPUT_FOLDER = os.path.join(ROOT_FOLDER,"input1")
OUTPUT_FOLDER = os.path.join(ROOT_FOLDER,"output")


SEND = 1
GET = 2
FOLDER = 32
FILE = 31



GET_INSIDE =34
DELETE =45
DOWNLOAD =67
COMPRESS = 57
TORRENT = 36


if(not os.path.exists(INPUT_FOLDER)):
	os.mkdir(INPUT_FOLDER)



os.chdir(INPUT_FOLDER)


# sys.exit(0)



def compress(file):

	try:
		if(not os.path.isdir(file)):
				name = ".".join(file.split(".")[:-1])
				print(f"doing {name}")
				os.system(f"ffmpeg -n -i \"{file}\" -vcodec libx264 -crf 37 -preset faster \"{name}.avi\" 2> /dev/null > /dev/null ")
				if(f"{name}.avi" in os.listdir()):
					os.remove(file)
		else:
			previous_folder = os.getcwd()	
			os.chdir(file)
			y = os.listdir()
			for k in y:
				compress(k)
			os.chdir(previous_folder)
	except Exception as e:
		print("error in compress",e)



def send_content(ft):
	stri = ''
	y = os.listdir()
	for k in y:
		if(os.path.isdir(k)):
			stri = stri+k+"\n"+'1'+"\n"
		else:
			stri = stri+k+"\n"+'0'+"\n"
	# print(f"sending {stri}")
	# print(y)
	ft.send_text(stri)
	return y


def run_child(python_file_path,command):
		

		args = ("python3", python_file_path, command)
		newpid = os.fork()
		
		if(newpid==0):
			os.execvp(args[0],args)
		else:
			print(f"child has spawn with p id {newpid}")

												
def provider(ft):
	try:
		previous_folder = os.getcwd()
		lis = send_content(ft)
		index = ft.recv_int()
		choice = ft.recv_int(1)
		print("choice made is",choice)
		if(choice == GET_INSIDE):
			if(os.path.isdir(lis[index])):
				os.chdir(lis[index])
				provider(ft)
			else:
				provider(ft)
		elif(choice ==DOWNLOAD):
			if(os.path.isdir(lis[index])):
				ft.send_folder(lis[index])
			else:
				ft.send_file(lis[index])
		elif(choice==COMPRESS):

			run_child("/home/nobodyknows/secret/compress.py",f"{lis[index]}")

		elif(choice==DELETE):
			os.system(f"rm -r \"{lis[index]}\"")
		elif(choice==TORRENT):
			magnet_link = ft.recv_text()
			if(magnet_link!=-1):
				run_child("/home/nobodyknows/secret/download_torrent.py",magnet_link)
			
		os.chdir(previous_folder)
	except Exception as e:
		print("error in provider",e)
		




	
def handle_client(ft):
	u = ft.reliable_recv(1)
	conn_type = int.from_bytes(u, byteorder='big')
	if(conn_type==SEND):
		#remove old files
		# for k in os.listdir(INPUT_FOLDER):
		# 	print("removing ",k)
		# 	os.remove(os.path.join(INPUT_FOLDER, k))
		try:
			ft.recieve_something(INPUT_FOLDER)
			ft.client.close()
		except Exception as e:
			print("Error in handle client",e)
		
	elif(conn_type==GET):
		provider(ft)
		




		





s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print ("Socket successfully created")




port = config_data["port"]
ip = config_data["ip"]

if(len(sys.argv)>1):
	port = int(sys.argv[1])
	print("hello")
s.bind((ip, port))
print ("socket binded to %s" %(port)) 
s.listen(0)     
print ("socket is listening")            
while True: 

	try:

		c, addr = s.accept()     
		print ('Got connection from', addr )
		ft = my_ft(c)
		handle_client(ft)

		try:
			c.close() 
		except Exception:
			continue
	except Exception as e:
		print("error in main loop",e)
		continue
