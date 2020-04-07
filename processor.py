import os
import pathlib

image_directory = pathlib.Path('./images')
pwd = os.getcwd()

image_paths = list()

for image in image_directory.iterdir():
	image_paths.append(image)

print("Images found")

for i in image_paths:
	print(i)


for image in image_paths:
	command = 'mmls '+str(image)
	mmls = os.system(command)		
	print(mmls)


