"""
Parallel kill command

@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""

from scutools.pexec import PExec

class Pkill(PExec) :
	def __init__(self, prog_args) :
		"""Init pkill"""
		self.sig_opt = ''
		self.search_spec = []
		self.ps_opt = None
		PExec.__init__(self, None, prog_args)

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
						self.sig_opt = self.sig_opt + '-s ' + self.cmd_args[i + 1] + ' '
						i = i + 2
					elif int(arg[1:]) > 0 :
						self.sig_opt = self.sig_opt + arg + ' '
						i = i + 1
					else :
						raise InvalArg, ('invalid option', arg)
				else :
					self.search_spec.append(arg)
					i = i + 1
		except IndexError :
			raise InvalArg, ('missing argument', self.cmd_args[i])
		if not self.search_spec :
			raise InvalArg, 'missing search spec'

	def launch(self, out = None, err = None) :
		import os
		return PExec.launch(self)

from scutools import config

class Pkillu(Pkill) :
	def __init__(self, prog_args) :
		Pkill.__init__(self, prog_args)

	def parseArg(self, prog_args) :
		Pkill.parseArg(self, prog_args)
		self.ps_opt = ''
		for spec in self.search_spec :
			self.ps_opt = self.ps_opt + '-u ' + spec + ' '
		self.cmd_args = ['(ps x --no-header -o pid %s 2> %s/pkill.$$ || head -1 %s/pkill.$$ ; rm -f %s/pkill.$$) | (while read ans; do pid_list="$pid_list $ans"; done; kill %s -- $pid_list)' \
				% (self.ps_opt, config.tmpdir, config.tmpdir, config.tmpdir, self.sig_opt)]

class Pkillps(Pkill) :
	def __init__(self, prog_args) :
		Pkill.__init__(self, prog_args)

	def parseArg(self, prog_args) :
		Pkill.parseArg(self, prog_args)
		self.cmd = 'killall'
		self.cmd_args = [self.sig_opt] + self.search_spec

if __name__ == '__main__' :
	pkill = Pkillu(['-a', '-s', 'SIGUSR1', '-1', 'ssy', 'b40sup'])

	print 'retval = ', pkill.launch()

	print '***********************'

	pkill = Pkillps(['-a', '-s', 'SIGUSR1', '-1', 'ssy', 'b40sup'])

	print 'retval = ', pkill.launch()
