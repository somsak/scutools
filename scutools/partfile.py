"""
Partition file module
	
@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""

import os, string
from scutools import config

def part_read(arg) :
	hostlist = []
	f = None
	# Try default partfile first
	try :
		f = open(config.partfile_dir + os.sep + arg, 'r')
	except IOError :
		f = open(arg, 'r')
	lines = f.readlines()
	f.close
	for i in lines :
		line = string.strip(i)
		if line and line[0] != '#' :
			hostlist.append(line)
	return hostlist
	
if __name__ == '__main__' :
	import sys

	print part_read(sys.argv[1])
