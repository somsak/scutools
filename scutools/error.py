''' 
	Error handler for SUT

	@author Somsak Sriprayoonsakul <somsaks@gmail.com>
'''

class InvalArg(Exception) :
	"Invalid argument input from user"
		
	def __init__(self, argname, argarg = None) :
		if argarg :
			self.value = 'invalid argument, %s %s' % (argname, argarg)
		else :
			self.value = 'invalid argument, %s' % (argname)
	def __str__(self) :
		return self.value

class NodeStatus(Exception) :
	"Error while getting node status"
	def __init__(self, cmdname) :
		self.value = 'error while getting node status, %s' % cmdname
	
	def __str__(self) :
		return self.value

class InvalHost(Exception) :
	"Invalid host format"
	def __init__(self, inval_host) :
		self.value = 'invalid host specification format %s' % inval_host

	def __str__(self) :
		return self.value

class InvalLauncher(Exception) :
    "Invalid launcher specify"
    def __init__(self, inval_launcher) :
        self.value = 'invalid launcher specify: %s' % inval_launcher

    def __str__(self) :
        return self.value
