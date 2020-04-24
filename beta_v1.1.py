import subprocess
import pytsk3
import sys
import os
import pathlib
from Registry import Registry

browser_artefact_map = {"Windows XP": 
["/Local Settings/Temporary Internet Files/Content.IE5/", 
"/Cookies/", "/Local Settings/History/history.IE5/", 
"/Application Data/Mozilla/Firefox/Profiles/", #%PROFILE%.default/places.sqlite",
"/Application Data/Apple Computer/Safari/History.plist", 
"/Local Settings/Application Data/Apple Computer/Safari/History.plist",
"/Application Data/Opera/Opera/",
"/Local Settings/Application Data/Google/Chrome/User Data/Default/Preferences"],

"Linux": 
["/.mozilla/firefox/",#$PROFILE.default/places.sqlite",
"/.opera/",
"/.config/google-chrome/Default/Preferences"],

"Windows":
["/AppData/Local/Microsoft/Windows/Temporary Internet Files/",#NOT!! windows xp no IE5 check if only index.dat works on reverse vm
"/AppData/Roaming/Mozilla/Firefox/Profiles/",
"/AppData/Roaming/Apple Computer/Safari/History.plist",
"/AppData/Local/Apple Computer/Safari/History.plist",
"/AppData/Roaming/Opera/Opera/",
"/AppData/Local/Google/Chrome/User Data/Default/Preferences"]

}

def getRegistry(mount, path):

	registry_path = mount + "/WINDOWS/system32/config"
	reg = ["/system", "/software"]

	for i in reg:
		command = "cp " + registry_path + i + " " + path #requires tools/script to be in the directory of the image, accomodate user path
		os.system(command)


def check_file(path, image_path):

	path = format_strings(path)
	suppress_output = ">/dev/null 2>&1"

	if((path.find(".IE5")) != -1):
		#print("Here!!")

		command = "ls " + path
		try:
			op = subprocess.check_output(command, stderr=subprocess.DEVNULL)
		except:	
			return

		op_list = op.split("\n")
		#print(op_list)

		for i in op_list:
			if(i.find(".dat") != -1):
				new_path = path + i
				#pwd = os.getcwd()
				command = "cp " + new_path + " " + image_path	
				os.system(command + suppress_output)

	if((path.lower()).find("firefox") != -1):
		command = "ls " + path
		try:
			op = subprocess.check_output(command, stderr=subprocess.DEVNULL)
		except:
			return

		op_list = op.split("\n")
		#print(op_list)

		for i in oplist:
			if(path.find(".default") in oplist):
				new_path = path + i + "/places.sqlite"
				#pwd = os.getcwd()
				command = "cp " + new_path + " " + image_path
				os.system(command + suppress_output)		
			
	#pwd = os.getcwd()
	command = "cp " + path + " " + image_path	
	os.system(command + suppress_output)

def append_uri(path, os_ver, image_path):
	for i in browser_artefact_map[os_ver]:
		path_uri = path + i
		#formatted_path = format_strings(path_uri)
		formatted_path = path_uri
		check_file(formatted_path, image_path)
		

def available_paths(temp_mount, image_path):
	
	init_path = {"Windows XP": "/Documents and Settings/", "Windows": "C:/Users/", "Linux": "/home/"}

	os_ver = get_OS_version(temp_mount) #get it through the registry

	path = temp_mount + init_path[os_ver]
	path_perma = path
	path = format_strings(path)

	command2 = "ls " + path
	op = subprocess.check_output(command2, shell = True)

	#print("Here: "+ op)
	op_list = op.split("\n")
	#print(op_list)

	for i in op_list:
		new_path = path_perma + i
		append_uri(new_path, os_ver, image_path)

def format_strings(path):
	return path.replace(" ", "\\ ")

def parse_win(path):

	xp = "Windows XP"
	other_ver = "Windows"

	registry_file_path = path + "/software"

	reg_software = Registry.Registry(registry_file_path)
	reg_software_key = "Microsoft\\Windows NT\\CurrentVersion"

	try:
	    software_key = reg_software.open(reg_software_key)

	except Registry.RegistryKeyNotFoundException:
	    print("Couldn't find Run key. Exiting...")
	    sys.exit(-1)

	version = software_key.value("ProductName")
	image_os = str(version.value())
	#print ("OS Version: " + str(version.value()))
	if(xp in image_os):
		return xp
	else:
		return other_ver
	
def get_OS_version(temp_mount):

	not_found = "No such file or directory"
	default_mount = "/mnt/temp/"

	linux_command = "strings " + str(temp_mount) + "/etc/os-release"
	try:
		print("In get_OS_version:")
		cmd_output = subprocess.check_output(linux_command, shell = True)
	except:
		#if(not_found in cmd_output):#replace this with exception block
		return parse_win(image_path) #check this if the variable is accessible 

	return "Linux"

def get_win_ipos(image_path):

	system_registry_path = image_path + "/system"
	software_registry_path = image_path + "/software"

	reg_system = Registry.Registry(system_registry_path)
	reg_software = Registry.Registry(software_registry_path)

	reg_system_key = "ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces"
	reg_software_key = "Microsoft\\Windows NT\\CurrentVersion"

	try:
	    software_key = reg_software.open(reg_software_key)
	    system_key = reg_system.open(reg_system_key)

	except Registry.RegistryKeyNotFoundException:
	    print("Couldn't find Run key. Exiting...")
	    sys.exit(-1)

	version = software_key.value("ProductName")
	print ("OS Version: " + str(version.value()))

	for subkeys in system_key.subkeys():
		for value in [v for v in subkeys.values()]:
			if(value.name() == "DhcpIPAddress"):
				print("IP Address: " + str(value.value()))

def get_lin_ipos(image_path):

	command = "strings " + image_path + "/etc/os-release"
	os_cat = subprocess.check_output(command, shell = True)
	os_cat_list = os_cat.split("\n")

	print(str(os_cat_list[0]))
	print(str(os_cat_list[1]))

	command1 = "ls " + image_path + "/sys/class/net"
	interfaces_list = subprocess.check_output(command1, shell = True)
	interfaces = interfaces_list.split("\n")

	for i in interfaces:
		command2 = image_path + "/sbin/ip -o -4 addr list " + i + " | cut -d/ -f1"
		IP = subprocess.check_output(command2, shell = True)
		print(IP)

def ip_OS_hostname(image_path, temp_mount):

	os = get_OS_version(temp_mount)

	if(os.find("Windows") != -1):
		get_win_ipos(image_path)
	else:
		get_lin_ipos(temp_mount)

def alloc_extract(alloc_mmls, image_name, volume, fstype_list):
	
	fs_list = alloc_mmls.split("\n")
	#print(fs_list)
	first_alloc_fs = True
	offset = 0
	for i in fs_list[5:]:

		try:
			slot = int(i.split(":")[0])

		except ValueError:
			continue

		#print(type(slot), slot)

		fs_name = "slot" + str(slot)
		dd_format = fs_name + ".dd"
		fstype_list.append(fs_name)
		#print(fs_list)

		command = "mmcat " + image_name + " " + str(slot) + " > " + dd_format
		#print(command)
		#os.system(command)

		for part in volume:
			if(part.addr == slot):
				if(first_alloc_fs == True):
					offset = part.start
					first_alloc_fs = False

    				fs_command = "fsstat -o " + str(part.start) + " " + image_name + " > " + "slot" + str(slot) + "_fsstat.txt"
				os.system(fs_command)

	return offset

def tsk_recover_files(fs_list, path):

	print(fs_list, path)
	
	for i in fs_list:

		dir_make = "/recovered_" + i + "_files"
		dir_cmd = "sudo mkdir " + path + dir_make
		#print(dir_cmd)
		os.system(dir_cmd + ">/dev/null 2>&1")

		rec_cmd = "sudo tsk_recover -e " + i + ".dd " + path + dir_make
		#print(rec_cmd)
		#os.system(rec_cmd)
		
		

print('Please make sure this script is in the same directory as the disk image!')

temp_path = subprocess.check_output("pwd", shell = True)
image_path = temp_path.rstrip()
print(image_path)

image_name = str(raw_input('Please enter the name of the disk image: '))
#"Pswift01.dd"

image_name = image_name.rstrip()

fs_list = []
#str(input('Please enter the name of the disk image: \n'))

image_directory = pathlib.Path(image_path) 
#must be changed to accomodate user path
#pwd = os.getcwd()

url = image_path + "/" + image_name
#print(url)

img = pytsk3.Img_Info(url)
volume = pytsk3.Volume_Info(img)

command3 = "mmls " + image_path + "/" + image_name + " > " + image_name + "_mmls.txt"
os.system(command3)

command1 = "mmls -a " + image_path + "/" + image_name	
alloc_mmls = subprocess.check_output(command1, shell = True)
#print(alloc_mmls)
offset = alloc_extract(alloc_mmls, image_name, volume, fs_list)

tsk_recover_files(fs_list, image_path)

temp_mount = "/mnt/temp"
#suppress_output = ">/dev/null 2>&1"

#might have to make a temp directory in /mnt folder
create_temp_mount = "sudo mkdir " + temp_mount
os.system(create_temp_mount)

command1 = "sudo mount -o loop,offset=$((" + str(offset * 512) + ")) " + str(image_name) + " " + temp_mount #offset to be gotten by mmls regex
#print("mount command is: " + command1)
os.system(command1)

getRegistry(temp_mount, image_path)
available_paths(temp_mount, image_path)
ip_OS_hostname(image_path, temp_mount)