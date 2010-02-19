"""
Generic interface for SUT spawner

@author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""

import subprocess

from util import ping_check

class Spawner :
    def __init__(self, special_arg) :
        """
        Initialized generic spawner
        
        @param special_arg special argument of SUT
        """
        pass

    def __del__(self) :
        pass
    
    def spawn(self, hostlist, cmd, args, out = None, err = None) :
        """
        Spawn the command

        @param hostlist list of host to spawn task
        @param cmd command name
        @param args command argument
        @param out output file object
        @param err error file object
        @return 0 if none task fail, otherwise -1
        """
        pass

import sys,os,tempfile,string
from  scutools import config, util

class BgfSpawner(Spawner) :
    """
    Spawner with background-file style.
    All output and error of the command will be redirected to file.
    All command will be spawned in background mode
    @note output and error will not be in order
    """
    def __init__(self, special_arg) :
        Spawner.__init__(self, special_arg)
        try :
            config.max_rshbg = special_arg['max-rshbg']
            if config.max_rshbg < 1 :
                config.max_rshbg = 1
        except KeyError:
            pass

    def _showout(self, file, fd, host) :
        f = open(file, 'r')
        line = f.readline()
        #XXX: Assume hostname format, not IP
        host = string.split(host, '.', 1)[0]
        while line :
            line = util.trim_host(host) + ':\t' + line
            fd.write(line)
            line = f.readline()
        f.close()

    def buildArg(self, host, cmd, args) :
        """Build command line"""
        pass

    def spawn(self, hostlist, cmd, args, out = None, err = None) :
        """Spawn task via rsh (or ssh) command"""
        count = 0
        pid_list = {}
        retval = 0

        if not out :
            out = sys.stdout
        if not err :
            err = sys.stderr
        while hostlist :
            if count < config.max_rshbg :
                # Fork and exec command
                tmpout = tempfile.mkstemp()
                tmperr = tempfile.mkstemp()
                pid = os.fork()
                if pid == 0 :
                    # child
                    sys.stdin.close()
                    outfd = os.open(tmpout, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0700)
                    errfd = os.open(tmperr, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0700)
                    os.dup2(outfd, sys.stdout.fileno())
                    os.dup2(errfd, sys.stderr.fileno())
                    spawn_arg = self.buildArg(hostlist[0], cmd, args)
                    os.execvp(spawn_arg[0], spawn_arg)
                else :
                    pid_list[pid] = (tmpout, tmperr, hostlist[0])
                    
                count = count + 1
                del hostlist[0]
            else :
                while pid_list and len(pid_list) >= config.max_rshbg :
                    pid, exit_stat = os.wait()
                    if exit_stat != 0 : retval = -1
                    p = pid_list[pid]
                    self._showout(p[0], out, p[2])
                    self._showout(p[1], err, p[2])
                    os.remove(p[0])
                    os.remove(p[1])
                    del pid_list[pid]
                    count = count - 1
                    
        while pid_list :
            pid, exit_stat = os.wait()
            if exit_stat != 0 : retval = -1
            p = pid_list[pid]
            self._showout(p[0], out, p[2])
            self._showout(p[1], err, p[2])
            os.remove(p[0])
            os.remove(p[1])
            del pid_list[pid]
        return retval

class RshBg(BgfSpawner) :
    """Spawn command using rsh"""
    def __init__(self, special_arg) :
        BgfSpawner.__init__(self, special_arg)

    def buildArg(self, host, cmd, args) :
        if config.ping_check and ping_check(host) != 0 :
            return ['echo', 'down']

        spawn_arg = [config.rsh_cmd, host]
            
        if cmd :
            spawn_arg.append(cmd)
        spawn_arg = spawn_arg + args
        return spawn_arg


if __name__ == '__main__' :
    rsh = RshBg({'max_rshbg':3})

    import socket
    
    rsh.spawn(['localhost',socket.gethostname(), 'localhost'], \
        '/bin/hostname', ['-i'])

