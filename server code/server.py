# first of all import the socket library 
import os,sys
import socket # for socket
import json

from urllib.parse import unquote


BUFFER_SIZE =1024
DISPLAY_TIME = 1024
SEND = 1
GET = 2
import time
FOLDER = 32
FILE = 31
TEXT = 33

root_path = os.getcwd()


running_processes = {}


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




BUFFER_SIZE = 1024
ROOT_FOLDER = os.getcwd()
INPUT_FOLDER = os.path.join(ROOT_FOLDER,"download_folder")
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
SCREENSHOT = 91


if(not os.path.exists(INPUT_FOLDER)):
	os.mkdir(INPUT_FOLDER)



os.chdir(INPUT_FOLDER)


# sys.exit(0)






def give_name(x):
	try:
		y  = unquote(x)
		if("dn=" in y):
			index = y.index("dn=")
			new_str = y[index+3:]
			if("&" in new_str):
				new_str = new_str[:new_str.index("&")]


			return new_str
		return x
	except Exception:
		return x






def send_content(ft,path):

	stri = ''
	y = os.listdir(path)
	for k in y:
		if(os.path.isdir(k)):
			stri = stri+k+"\n"+'1'+"\n"
		else:
			stri = stri+k+"\n"+'0'+"\n"
	# print(f"sending {stri}")
	# print(y)
	ft.send_text(stri)
	return y


def run_child(python_file_path,command,message):
		

		args = ("python3", python_file_path, command)
		newpid = os.fork()
		
		if(newpid==0):
			os.execvp(args[0],args)
		else:
			running_processes[newpid]=message
			print(f"child has spawn with p id {newpid}")

												
def provider(ft,base_path):
	try:
	
		lis = send_content(ft,base_path)
		index = ft.recv_int()
		choice = ft.recv_int(1)
		print("choice made is",choice)

		selected_file_path = os.path.join(base_path,lis[index])
		if(choice == GET_INSIDE):
			if(os.path.isdir(selected_file_path)):
				provider(ft,selected_file_path)
			else:
				provider(ft)
		elif(choice ==DOWNLOAD):
			if(os.path.isdir(selected_file_path)):
				ft.send_folder(selected_file_path)
			else:
				ft.send_file(selected_file_path)
		elif(choice==COMPRESS):

			run_child(os.path.join(root_path,"compress.py"),f"{selected_file_path}",f"compression of {selected_file_path} is pending")

		elif(choice==DELETE):
			os.system(f"rm -r \"{selected_file_path}\"")
		elif(choice==TORRENT):
			magnet_link = ft.recv_text()
			if(magnet_link!=-1):
				run_child(os.path.join(root_path,"download_torrent.py"),magnet_link,f"{give_name(magnet_link)} is still downloading")
		elif(choice==SCREENSHOT):
			number_of_ss = ft.recv_int()
			temp_path =os.path.join(root_path,"screen_shot.py")
			print(f"python3 {temp_path} {selected_file_path} {number_of_ss} 2> /dev/null > /dev/null")
			os.system(f"python3 \"{temp_path}\" \"{selected_file_path}\" \"{number_of_ss}\" 2> /dev/null > /dev/null")
			if(os.path.exists(selected_file_path+"_screen_shot.jpg")):
				ft.send_file(selected_file_path+"_screen_shot.jpg")
			else:
				y = open("something_went_wrong.jpg","w")
				y.close()
				ft.send_file("something_went_wrong.jpg")
			
	except Exception as e:
		print("error in provider",e)
		




	
def handle_client(ft):
	u = ft.reliable_recv(1)

	try:


		keys = list(running_processes.keys())
		for k in keys:
			pid,status = os.waitpid(k,os.WNOHANG)
			if(pid>0):
				running_processes.pop(pid)
	except Exception:
		pass

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

		strin = ""
		for _,message in running_processes.items():
			strin =strin+message+"\n"
		ft.send_text(strin)
		provider(ft,INPUT_FOLDER)
		




		





s= socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print ("Socket successfully created")




port = config_data["port"]
ip = config_data["ip"]

if(len(sys.argv)>1):
	port = int(sys.argv[1])
	print("hello")
s.bind(("", port))
print ("socket binded to %s" %(port)) 
s.listen(0)     
print ("socket is listening")            
while True: 

	try:

		c, addr = s.accept()     
		print ('Got connection from', addr )
		ft = my_ft(c)
		handle_client(ft)
		keys = list(running_processes.keys())
		for k in keys:
			pid,status = os.waitpid(k,os.WNOHANG)
			if(pid>0):
				running_processes.pop(pid)
		print(running_processes)
		try:
			c.close() 
		except Exception:
			continue
	except Exception as e:
		print("error in main loop",e)
		continue
