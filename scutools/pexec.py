"""
Generic SUT interface
    
@author Somsak Sriprayoonsakul
"""

import sys, string, os

import config, node
from error import *

import spawner

class PExec :
    "Generic interface to parallel command"
    HARG_ALL = 1
    HARG_EXCEPT = 2
    HARG_HOST = 3
    HARG_PART = 4
    HARG_DOWN = 5

    def __init__(self, cmd, prog_args) :
        " Initialized internal variable "
        self.cmd = cmd
        self.cmd_args = None
        self.hostarg = (None, None)
        self.hostlist = []
        self.specarg = {}
        self.parseArg(prog_args)
        self.parseHostArg()

    def parseArg(self, prog_args) :
        "Parse generic sut argument"
        
        try :
            # parse special option first
            i = 0
            while i < len(prog_args) :
                if prog_args[i][0:5] == '--scu' :
                    arg = prog_args[i][6:]
                    if arg :
                        arg = string.split(arg, '=', 1)
                        if len(arg) == 1 :
                            self.specarg[arg[0]] = 1
                        else :
                            self.specarg[arg[0]] = arg[1]
                    del prog_args[i]
                else :
                    i = i + 1
            # now host option
            try :
                self.hostarg = (self.HARG_ALL, None)
                if prog_args[0] == '--help' :
                    # this is special case, since --help is the first command which is not very likely to happen
                    if len(prog_args) < 2 :
                        raise InvalArg, 'try man pexec'
                if prog_args[0] == '-a' or\
                    prog_args[0] == '--all' :
                    self.hostarg = (self.HARG_ALL, None)
                    del prog_args[0]
                elif prog_args[0] == '-aa' or \
                    prog_args[0] == '--really-all' :
                    self.hostarg = (self.HARG_ALL, None)
                    self.specarg['forceall'] = 1
                    del prog_args[0]
                elif prog_args[0] == '-d' or \
                    prog_args[0] == '--down' :
                    self.hostarg = (self.HARG_DOWN, None)
                    self.specarg['forceall'] = 1
                    del prog_args[0]
                elif prog_args[0] == '-e' or\
                    prog_args[0] == '--except' :
                    self.hostarg = (self.HARG_EXCEPT, None)
                    del prog_args[0]
                elif prog_args[0] == '-ea' or\
                    prog_args[0] == '--except-all' :
                    self.hostarg = (self.HARG_EXCEPT, None)
                    self.specarg['forceall'] = 1
                    del prog_args[0]
                elif prog_args[0] == '-p' or\
                    prog_args[0] == '--part' :
                    if len(prog_args) < 2 :
                        self.listPart()
                        raise NoError
                    self.hostarg = (self.HARG_PART, prog_args[1])
                    del prog_args[0:2]
                elif prog_args[0] == '-pa' or\
                    prog_args[0] == '--part-all' :
                    if len(prog_args) < 2 :
                        self.listPart()
                        raise NoError
                    self.hostarg = (self.HARG_PART, prog_args[1])
                    self.specarg['forceall'] = 1
                    del prog_args[0:2]
                elif prog_args[0] == '-h' or\
                    prog_args[0] == '--host' :
                    if len(prog_args) < 2 :
                        raise InvalArg, 'need at least one host pattern, such as \'compute.*\''
                    self.hostarg = (self.HARG_HOST, prog_args[1])
                    del prog_args[0:2]
                elif prog_args[0] == '-ha' or\
                    prog_args[0] == '--host-all' :
                    if len(prog_args) < 2 :
                        raise InvalArg, 'need at least one host pattern, such as \'compute<0-9>\''
                    self.hostarg = (self.HARG_HOST, prog_args[1])
                    self.specarg['forceall'] = 1
                    del prog_args[0:2]
            except IndexError :
                pass
                #if not config.compat_scms_2 :
                #    # We can't let the command without host option!
                #    raise InvalArg, 'need host specification'
            # The rest is command option
            self.cmd_args = prog_args

        except IndexError:
            if i < len(prog_args) :
                raise InvalArg, prog_args[0]
            else :
                raise InvalArg, 'none'

    def parseHostArg(self) :
        "Create hostlist from host specification argument"
        # Get node first
        flag = 0x0
        if self.hostarg[0] == self.HARG_EXCEPT :
            flag = flag | node.ALL_EXC

        if self.hostarg[0] == self.HARG_DOWN or self.specarg.has_key('forceall') :
            self.hostlist = node.get_alive(node.ALL | flag)
        else :
            self.hostlist = node.get_alive(node.ALIVE | flag)

        if self.hostarg[0] == self.HARG_DOWN :
            on_hostlist = node.get_alive(node.ALIVE | flag)
            # exclude host that's in on-line hosts
            real_hostlist = []
            for host in self.hostlist :
                if not host in on_hostlist :
                    real_hostlist.append(host)
            self.hostlist = real_hostlist
                    
        # Parse host argument, if needed
        if self.hostarg[0] == self.HARG_HOST or self.hostarg[0] == self.HARG_PART :
            tmp_hostlist = []
            if self.hostarg[0] == self.HARG_PART :
                import partfile
                tmp_hostlist = partfile.part_read(self.hostarg[1])
            elif self.hostarg[0] == self.HARG_HOST :
                tmp_hostlist = string.split(self.hostarg[1], ',')
            # Treat each line as REGEX
            real_hostlist = []
            import xre
            while tmp_hostlist :
                h = tmp_hostlist[0]
                try :
                    ro = xre.compile('^' + h + '$')
                except :
                    if len(tmp_hostlist) != 1 :
                        tmp_hostlist[0] = string.join([h,tmp_hostlist[1]], ',')
                        del tmp_hostlist[1]
                        continue
                    else :
                        raise InvalHost, h
                i = 0
                while i < len(self.hostlist) :
                    # match the whole hostname
                    m1 = ro.match(self.hostlist[i])
                    # additionally match just short hostname
                    m2 = ro.match(self.hostlist[i].split('.')[0])
                    if m1 or m2 :
                        real_hostlist.append(self.hostlist[i])
                        del self.hostlist[i]
                    else :
                        i = i + 1
                del tmp_hostlist[0]
            self.hostlist = real_hostlist
        
        # Move our name to the last of the list, if any
        self.moveLast()
    
    def moveLast(self) :
        "Move hostname to the last entry of list"
        import socket

        myaddr = socket.gethostbyname(socket.gethostname())
        for i in range(len(self.hostlist)) :
            try :
                if socket.gethostbyname(self.hostlist[i]) is myaddr :
                    del self.hostlist[i]
                    self.hostlist.append(h)
                    break
            except socket.gaierror, e :
                raise NodeStatus(self.hostlist[i])

    def launch(self, out = None, err = None) :
        """Execute the command, return the exit status"""
        # Get spawner first
        spawner_arg = config.def_spawner
        if self.specarg.has_key('spawner') :
            spawner_arg = self.specarg['spawner'][1]
        
        launcher = None
        if spawner_arg == 'rsh' :
            launcher = spawner.RshBg(self.specarg)
        else :
            raise InvalLauncher(spawner_arg)

        if not self.cmd and not self.cmd_args :
            raise InvalArg('')

        retval = launcher.spawn(self.hostlist, self.cmd, self.cmd_args, out, err)
        return retval

    def listPart(self) :
        """List partition file available on the system"""
        if config.partfile_dir :
            print 'Part available in this host are:'
            for file in os.listdir(config.partfile_dir) :
                path = os.path.join(config.partfile_dir, file)
                if os.path.isfile(path) :
                    print file
        
if __name__ == '__main__' :
    cmd = PExec(sys.argv[1], sys.argv[2:])
    print 'command = ', cmd.cmd
    print 'command args = ', cmd.cmd_args
    print 'host arg = ', cmd.hostarg
    print 'special args = ', cmd.specarg
    print 'hostlist = ', cmd.hostlist
    cmd.launch()
