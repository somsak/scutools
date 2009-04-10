"""
	Parallel kill all user process

	@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""

from pexec import PExec

class Pkillu(PExec) :
	def __init__(self, prog_args) :
		self.sigarg = []
		self.procname = []
		PExec.__init__(self, 'kill', prog_args)

	def parseArg(self, prog_args) :
		"""Parse signal and co."""
		PExec.parseArg(self, prog_args)
		# Parse signal list
		i = 0
		try :
			while i < len(self.cmd_args) :
				arg = self.cmd_args[i]
				if arg[0] == '-' :
					if arg[1:] == 's' :
						self.sigarg.append(arg)
						self.sigarg.append(self.cmd_args[i + 1])
						del self.cmd_args[i]
						del self.cmd_args[i+1]
					elif int(arg[1:]) > 0 :
						self.sigarg.append(arg)
					else :
						raise InvalArg, ('invalid option', arg)
				else :
					self.procname.append(arg)
		except IndexError :
			raise InvalArg, ('missing argument', self.cmd_args[i])
