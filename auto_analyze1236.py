import subprocess
import pytsk3
import sys
import os
import pathlib
from Registry import Registry

# contains path to the index of browser artefacts in different operating systems
browser_artefact_map = {"Windows XP":
["/Local Settings/Temporary Internet Files/Content.IE5/",
"/Cookies/", "/Local Settings/History/history.IE5/",
"/Application Data/Mozilla/Firefox/Profiles/",
"/Application Data/Apple Computer/Safari/History.plist",
"/Local Settings/Application Data/Apple Computer/Safari/History.plist",
"/Application Data/Opera/Opera/",
"/Local Settings/Application Data/Google/Chrome/User Data/Default/Preferences"],

"Linux":
["/.mozilla/firefox/",
"/.opera/",
"/.config/google-chrome/Default/Preferences"],

"Windows":
["/AppData/Local/Microsoft/Windows/Temporary Internet Files/",
"/AppData/Roaming/Mozilla/Firefox/Profiles/",
"/AppData/Roaming/Apple Computer/Safari/History.plist",
"/AppData/Local/Apple Computer/Safari/History.plist",
"/AppData/Roaming/Opera/Opera/",
"/AppData/Local/Google/Chrome/User Data/Default/Preferences"]

}

# takes mount which is path to the mounted disk and path is the
# destination where the "software" and "system" registry files
# have to be copied. This function copies the registry files to the
# directory of the disk image
def getRegistry(mount, path):

	# mount point + default path of registry files on windows
	registry_path = mount + "/WINDOWS/system32/config"
	reg = ["/system", "/software"]

	# loops over the reg list and copies the registry files to "path"
	for i in reg:
		command = "cp " + registry_path + i + " " + path
		os.system(command)

# takes the path from "browser_artefact_map" and copies the browser artefact
# containing history, cache etc. to the disk image directory
def check_file(path, image_path):

	# removes spaces within file path with \\
	path = format_strings(path)
	suppress_output = ">/dev/null 2>&1"

	# check if path contains .IE5 in its path belonging to IE explorer
	if((path.find(".IE5")) != -1):

		# this command gets the list of folders in the path
		command = "ls " + path
		try:
			op = subprocess.check_output(command, shell = True)
		except:
			return

		op_list = op.split("\n")

		# loop through each of the folders in the path and check for .dat file
		for i in op_list:

			#if found copy the .dat file to disk directory
			if(i.find(".dat") != -1):

				# append the folder to the path
				new_path = path + i
				command = "cp " + new_path + " " + image_path
				os.system(command + suppress_output)

	# check if path belongs to firefox directory
	if((path.lower()).find("firefox") != -1):

		# get list of folders in the path
		command = "ls " + path
		try:
			op = subprocess.check_output(command,shell = True)
		except:
			return

		op_list = op.split("\n")

		# loop through the folders from "ls" command
		for i in oplist:

			# if the folder ends with .default copy the .sqlite file
			if(i.find(".default") != -1):

				new_path = path + i + "/places.sqlite"
				command = "cp " + new_path + " " + image_path
				os.system(command + suppress_output)

	# if the path does not belong to IE explorer or firefox copy file
	# specified in the path to the disk directory
	command = "cp " + path + " " + image_path
	os.system(command + suppress_output)

# takes the "path" appends the path from the map based on the "os_ver" and calls
# "check_file"
def append_uri(path, os_ver, image_path):

	# call the list from map based on the os_ver
	for i in browser_artefact_map[os_ver]:

		# "path" + path from the map
		path_uri = path + i
		formatted_path = path_uri
		check_file(formatted_path, image_path)

# check for the os version of the disk image mounted at "temp_mount" and
# creates a path based on the os_ver and call another function for
# further processing
def available_paths(temp_mount, image_path):

	# initial path based on os versions
	init_path = {"Windows XP": "/Documents and Settings/",
	"Windows": "C:/Users/", "Linux": "/home/"}

	# get os_ver through registry parsing
	os_ver = get_OS_version(temp_mount)

	#gets the first part of the path from init_path based on the os version
	# and appends it to the temp_mount
	path = temp_mount + init_path[os_ver]
	path_perma = path
	path = format_strings(path)

	# gets list of folders in the init_path
	command2 = "ls " + path
	op = subprocess.check_output(command2, shell = True)

	op_list = op.split("\n")

	# loops through each folder and call append_uri for further
	# processing
	for i in op_list:
		new_path = path_perma + i
		append_uri(new_path, os_ver, image_path)

# this function replaces spaces in the path with "\\"" since spaces in os.system
# command considers spaces as seperate commands
def format_strings(path):
	return path.replace(" ", "\\ ")

# if os version of the disk image is windows this function parses through the
# windows registry and gets windows os version that the disk image is running
def parse_win(path):

	xp = "Windows XP"
	other_ver = "Windows"

	# path to the software registry in the disk image
	registry_file_path = path + "/software"

	# call registry module that creates a registry object
	reg_software = Registry.Registry(registry_file_path)
	reg_software_key = "Microsoft\\Windows NT\\CurrentVersion"

	# opens the reg_software_key and returns an object to the key
	try:
	    software_key = reg_software.open(reg_software_key)

	# if the key does not exist exit
	except Registry.RegistryKeyNotFoundException:
	    print("Couldn't find Run key. Exiting...")
	    sys.exit(-1)

	# in the registry key object check for the value associated with
	# "ProductName"
	version = software_key.value("ProductName")

	# convert the value to string
	image_os = str(version.value())

	# if the image_os is windows xp return the same else windows
	if(xp in image_os):
		return xp
	else:
		return other_ver

# check the version of the os of the disk image mounted at "temp_mount"
def get_OS_version(temp_mount):

	not_found = "No such file or directory"
	default_mount = "/mnt/temp/"

	# creates a path that holds os version in linux image
	linux_command = "strings " + str(temp_mount) + "/etc/os-release"

	# tries to open the above linux path
	try:
		print("In get_OS_version:")
		cmd_output = subprocess.check_output(linux_command, shell = True)

	# if image is windows the above command raises exception which means it is
	# a windows image
	except:
		return parse_win(image_path)

	return "Linux"

# gets the path of the mount and processes it to obtain the ip address for win
def get_win_ipos(image_path):

	# holds path to system and software registry
	system_registry_path = image_path + "/system"
	software_registry_path = image_path + "/software"

	# open registry object for both the registry path
	reg_system = Registry.Registry(system_registry_path)
	reg_software = Registry.Registry(software_registry_path)

	# registry keys that contain IP address and OS version
	reg_system_key = "ControlSet001\\Services\\Tcpip\\Parameters\\Interfaces"
	reg_software_key = "Microsoft\\Windows NT\\CurrentVersion"

	# open the registry key
	try:
	    software_key = reg_software.open(reg_software_key)
	    system_key = reg_system.open(reg_system_key)

	# if unable to open exit
	except Registry.RegistryKeyNotFoundException:
	    print("Couldn't find Run key. Exiting...")
	    sys.exit(-1)

	# get the value associated with the "ProductName"
	version = software_key.value("ProductName")
	print '*****************************************************\n'
	print ("OS Version: " + str(version.value()))

	# for each of the subkeys within the "Interfaces" key
	# check for "DhcpIPAddress" name and print its value which is the IP address
	for subkeys in system_key.subkeys():
		for value in [v for v in subkeys.values()]:

			if(value.name() == "DhcpIPAddress"):
				print("IP Address: " + str(value.value()))
	print '\n*****************************************************'

# get the os version and IP address of a linux image
def get_lin_ipos(image_path):

	# command to extract os version in the os-release file
	command = "strings " + image_path + "/etc/os-release"
	os_cat = subprocess.check_output(command, shell = True)
	os_cat_list = os_cat.split("\n")

	print '*****************************************************\n'
	print(str(os_cat_list[0]))
	print(str(os_cat_list[1]))


	# /sys/class/net contains the interface files which contain ip addresses
	# of each interface. Get the list of interface using "ls"
	command1 = "ls " + image_path + "/sys/class/net"
	interfaces_list = subprocess.check_output(command1, shell = True)
	interfaces = interfaces_list.split("\n")

	# loop through each interface file and grab the IP address of each
	# interface and print it
	for i in interfaces:
		command2 = image_path + "/sbin/ip -o -4 addr list " + i + " | cut -d/ -f1"
		IP = subprocess.check_output(command2, shell = True)
		print(IP)
	print '\n*****************************************************'

# get the os version of the image in temp_mount and call respective functions
def ip_OS_hostname(image_path, temp_mount):

	os = get_OS_version(temp_mount)

	if(os.find("Windows") != -1):
		get_win_ipos(image_path)
	else:
		get_lin_ipos(temp_mount)

# extract allocated partitions from the disk image and output file system
# information on each fs. "alloc_mmls" contains the mmls information of
# allocated slots. "image_name" disk image name provided by the user.
def alloc_extract(alloc_mmls, image_name, volume, fstype_list):

	# get a list of allocated partitions
	fs_list = alloc_mmls.split("\n")

	# variable to check first allocated fs
	first_alloc_fs = True
	offset = 0

	# create .dd images of each allocated partition using mmcat
	for i in fs_list[5:]:

		try:
			slot = int(i.split(":")[0])


		except ValueError:
			continue


		# create .dd with the slot name
		fs_name = "slot" + str(slot)
		dd_format = fs_name + ".dd"

		# append the slot name to fstype_list to recover files on each fs
		fstype_list.append(fs_name)

		# mmcat on partition
		command = "mmcat " + image_name + " " + str(slot) + " > " + dd_format
		os.system(command)

		# loop through each parition and extract fs information
		for part in volume:

			# check if its an allocated fs
			if(part.addr == slot):
				# if first slot store the offset for mounting
				if(first_alloc_fs == True):
					offset = part.start
					first_alloc_fs = False
				# extract fsstat and store it in fsstat.txt file
				fs_command = "fsstat -o " + str(part.start) + " " + image_name + " > " + "slot" + str(slot) + "_fsstat.txt"

				os.system(fs_command)

	return offset

# recover deleted files on the fs on the disk at "fs_list" into the a new
# directory within the disk image directory
def tsk_recover_files(fs_list, path):

	# loop through each fs and recover files into the /recovered_fs_files dir
	for i in fs_list:

		dir_make = "/recovered_" + i + "_files"
		# make a directory at the disk image dir
		dir_cmd = "sudo mkdir " + path + dir_make

		# use ">/dev/..." to suppress output
		os.system(dir_cmd + ">/dev/null 2>&1")

		rec_cmd = "sudo tsk_recover -e " + i + ".dd " + path + dir_make
		os.system(rec_cmd)



print('Please make sure this script is in the same directory as the disk image!')

# get the current working directory
temp_path = subprocess.check_output("pwd", shell = True)
image_path = temp_path.rstrip()
print(image_path)

# get user provided disk image name
image_name = str(raw_input('Please enter the name of the disk image: '))

# remove space at the end of the input string
image_name = image_name.rstrip()

# get the list of fs in the disk image
fs_list = []

# Pathlib object for the path to the image
image_directory = pathlib.Path(image_path)

url = image_path + "/" + image_name

# pytsk3 for getting the volume object to extract fs
img = pytsk3.Img_Info(url)
volume = pytsk3.Volume_Info(img)

# get the mmls of the disk image
command3 = "mmls " + image_path + "/" + image_name + " > " + image_name + "_mmls.txt"
os.system(command3)

# mmls -a provides the allocated filesystems in the disk image
command1 = "mmls -a " + image_path + "/" + image_name
alloc_mmls = subprocess.check_output(command1, shell = True)


# extract the fs info of the disk image and get the offset to the first fs
offset = alloc_extract(alloc_mmls, image_name, volume, fs_list)

# recover files from all the fs in the disk image
tsk_recover_files(fs_list, image_path)

# mount point of the disk image
temp_mount = "/mnt/temp"
#suppress_output = ">/dev/null 2>&1"

# if not present create the temporary mount and mount disk image
create_temp_mount = "sudo mkdir " + temp_mount
os.system(create_temp_mount)

command1 = "sudo mount -o loop,offset=$((" + str(offset * 512) + ")) " + str(image_name) + " " + temp_mount
os.system(command1)

# get the registry file to the current dir if the user wants to extract more info
getRegistry(temp_mount, image_path)

# gets the browser artefact
available_paths(temp_mount, image_path)

# prints the IP address and OS of the disk image
ip_OS_hostname(image_path, temp_mount)
