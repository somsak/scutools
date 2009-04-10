"""
Parallel Find process command

@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""

from scutools.pexec import PExec

class Pfps(PExec) :
	""" This class is just a wrapper of pps """
	def __init__(self, prog_args) :
		PExec.__init__(self, 'ps', prog_args)

	def parseArg(self, prog_args) :
		PExec.parseArg(self, prog_args)
		for i in range(len(self.cmd_args)) :
			self.cmd_args[i] = '-C ' + self.cmd_args[i]
		self.cmd_args.append('--no-header')
		self.cmd_args.append('ux')

	def launch(self, out = None, err = None) :
		print "HOST\t\tUSER       PID %CPU %MEM   VSZ  RSS TTY      STAT START   TIME COMMAND"
		return PExec.launch(self)
		
