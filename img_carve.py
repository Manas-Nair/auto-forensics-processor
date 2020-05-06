import subprocess
import os
import random
import sys

def extract_partition_no(alloc_string):
	partition_number = alloc_string.split(':')[0]
	x =  int(partition_number)
	return x


def alloc_nos(allocated_partitions):
	partition_no = list()
	allocated_array = allocated_partitions.split('\n')[5:-1]
	for i in allocated_array:
		print i
		y = extract_partition_no(i)
		partition_no.append(y)
	return partition_no

def carve_partitions(partitions, path):
	names = list()
	for i in partitions:
		file_name = 'img_partition'+str(i)+'.dd'
		command = 'mmcat '+path+' '+str(i)+ ' > '+file_name
		print command
		os.system(command)
		names.append(file_name)
	return names

def carve_images(partition_names, img_folder):

	for i in partition_names:
		folder = img_folder+'_'+i
		command = 'scalpel -c img.conf '+i+' -o '+folder
		os.system(command)

def generate_stringlists(partition_names):

	for i in partition_names:
		file_name = 'stringlist_partition'+i
		command = 'strings -eS -td '+i+' > '+file_name
		print command
		os.system(command)

def images_and_strings(path):
	#Configure conf file for scalpel

	conf_cmd = 'egrep "(gif|jpg)" /etc/scalpel/scalpel.conf | sed s/#//g > img.conf'
	img_folder = raw_input('Enter folder name for extracted images:\t')
	clear_direcotries = 'rm -rf '+img_folder+'*'
	remove_existing = 'rm img_partition*'

	os.system(conf_cmd)
	os.system(clear_direcotries)
	os.system(remove_existing)

	command = "mmls -a "+ path
	print command
	allocated_partitions = subprocess.check_output(command, shell = True)

	partitions = alloc_nos(allocated_partitions)

	partition_names = carve_partitions(partitions, path)
	print partition_names

	print "Running Scalpel to Carve Images"
	carve_images(partition_names, img_folder)

	print "Generating String Lists"
	generate_stringlists(partition_names)


if len(sys.argv) != 2:
	print 'Usage: python img_carve.py <Disk Image>'
else:
	image_name = sys.argv[1]
	pwd = os.getcwd()
	path = pwd+'/'+image_name
	images_and_strings(path)
