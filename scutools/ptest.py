"""
Generic interface for PTest and co.

@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""

from scutools.pexec import PExec
from stat import *

class Ptest(PExec) :
	def __init__(self, prog_args) :
		PExec.__init__(self, None, prog_args)

	def parseArg(self, prog_args) :
		"""Add command to the tail of test command"""
		PExec.parseArg(self, prog_args)
		self.cmd_args = ['if', 'test'] + self.cmd_args + [';', 'then', 'echo 1;', 'else', 'echo 0;', 'fi']


	def launch(self, out = None, err = None) :
		import tempfile, os

		out = tempfile.mktemp()
		err = tempfile.mktemp()
		outf = open(out, 'w')
		errf = open(err, 'w')
		retval = PExec.launch(self, outf, errf)
		outf.close()
		errf.close()
		if not retval == 0 : return retval

		if os.stat(err)[ST_SIZE] > 0 :
			import sys
			f = open(err, 'r')
			lines = f.readlines()
			for line in lines :
				sys.stderr.write(line)
			f.close()
			return -1
		else :
			f = open(out, 'r')
			lines = f.readlines()
			import string
			retval = 0
			for line in lines :
				line = string.strip(line)
				host, exit_stat = string.split(line, ':', 1)
				if not int(exit_stat) :
					retval = 1
					break
			f.close()
			return retval

if __name__ == '__main__' :
	cmd = Ptest(['-a', '-f', '/etc/passwd'])
	print cmd.launch()
	cmd = Ptest(['-a', '-f', '/etc/pass'])
	print cmd.launch()
