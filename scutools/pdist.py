"""
Parallel file distribution

@author Somsak Sriprayoonsakul <ssy@sce.cpe.ku.ac.th>
"""
from scutools.pexec import PExec
from scutools.rdup import RcpBg
from scutools.rdup import Rdup
from scutools.error import InvalArg

class PDist(PExec) :
	def __init__(self, prog_args) :
		self.args = []
		self.source = []
		self.dest = None
		self.copy_flag = 0x0
		PExec.__init__(self, None, prog_args)

	def parseArg(self, prog_args) :
		"Parse additional argument for pdist command"
		PExec.parseArg(self, prog_args)

		i = 0

		import getopt
		optlist, args = getopt.getopt(self.cmd_args, 'rp')
		# getopt.getopt will raise proper exception when
		# unknown exception occur
		for opt in optlist :
			if opt[0] == '-r' :
				self.copy_flag = self.copy_flag | Rdup.RECURSIVE
			elif opt[0] == '-p' :
				self.copy_flag = self.copy_flag | Rdup.PRESERVE_PERM
				
		# Only real command left
		if len(args) < 2 :
			raise InvalArg, 'missing destination'
		self.dest = args.pop(len(args) - 1)
		self.source = args

	def launch(self, out = None, err = None) :
		# Always create rcp rdup
		launcher = RcpBg(self.specarg)
		#print self.dest, self.source
		return launcher.copy(self.hostlist, self.source, self.dest, self.copy_flag) 

if __name__ == '__main__' :
	pdist = PDist(['-r', '/etc/hosts', '/etc/services', '/tmp'])

	pdist.launch()
