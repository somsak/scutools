"""
Interface for remote copy

@author Somsak Sriprayoonsakul
"""

class Rdup :
	PRESERVE_PERM = 0x01
	RECURSIVE = 0x02
	def __init__(self, spec_args) :
		"""Initialized rdup"""
		pass
	def copy(self, hostlist, source, dest, copy_flag, out = None, err = None) :
		"""Copy file from source to allhost's dest"""
		pass

from scutools import config
from scutools.spawner import BgfSpawner

class RcpBg(Rdup, BgfSpawner) :
	def __init__(self, special_args) :
		Rdup.__init__(self, special_args)
		BgfSpawner.__init__(self, special_args)

	def buildArg(self, host, cmd, args) :
		"""
		Build RCP argument from input arg
		Input arg are assume to be in order (by external pdist
		class). Last argument is always destination
		"""
		spawn_arg = [config.rcp_cmd]
		last_idx = len(args) - 1
		args[last_idx] = host + ':' + args[last_idx]
		spawn_arg = spawn_arg + args
		return spawn_arg

	def copy(self, hostlist, source, dest, copy_flag, out = None, err = None) :
		"""
		Copy file to all host, use spawner as its underly
		mechanism.
		"""
		args = []
		if copy_flag & self.PRESERVE_PERM :
			args.append('-p')
		if copy_flag & self.RECURSIVE :
			args.append('-r')
		args = args + source
		args.append(dest)
		return self.spawn(hostlist, None, args, out, err)

if __name__ == '__main__' :
	rcp = RcpBg({'max_rshbg':3})
	import socket
	rcp.copy(['localhost', socket.gethostname(), 'localhost'], \
		['/etc/hosts', '/etc/services'], '/tmp', Rdup.PRESERVE_PERM | Rdup.RECURSIVE)
