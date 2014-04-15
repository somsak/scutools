"""
Partition file module
	
@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""

import os, string
from scutools import config
from scutools.node import ansible_ini
from scutools.error import InvalArg

def part_read(arg) :
	hostlist = []
	
	if config.hostlist_src != 'ansible' :
		f = None
		# Try default partfile first
		try :
			f = open(config.partfile_dir + os.sep + arg, 'r')
		except IOError :
			f = open(arg, 'r')
		finally :
			raise InvalArg('Invalid part specified:' + arg)
		lines = f.readlines()
		f.close
		for i in lines :
			line = string.strip(i)
			if line and line[0] != '#' :
				hostlist.append(line)
	else :
		try :
			hostlist = ansible_ini.groups[arg].get_hosts()
		except KeyError:
			raise InvalArg('Invalid part specified:' + arg)
			
	return hostlist
	
if __name__ == '__main__' :
	import sys

	print part_read(sys.argv[1])
