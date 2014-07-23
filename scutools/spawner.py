"""
Generic interface for SUT spawner

@author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""

import sys,os,tempfile,string,select,tempfile
from select import POLLIN, POLLOUT
#import subprocess

import config, util
from util import ping_check

try :
    #import paramiko
    has_paramiko = False
except ImportError :
    has_paramiko = False

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
        @return 0 if no task fail, otherwise -1
        """
        pass

# if has_paramiko :
#     class SshSpawner(Spawner) :
#         def __init__(self, special_arg) :
#             """
#             Initialized generic spawner
#             
#             @param special_arg special argument of SUT
#             """
#             Spawner.__init__(self, special_arg)
#             try :
#                 config.max_rshbg = special_arg['max-rshbg']
#                 if config.max_rshbg < 1 :
#                     config.max_rshbg = 1
#             except KeyError:
#                 pass
# 
#             # Mutex for output printing and host_list
#             self.show_out_mutex = threading.Lock()
#             self.host_list_mutex = threading.Lock()
#             self.host_list = []
# 
#             # create pool of SshClient equal to number of rshbg
# 
# 
#         def spawn(self, hostlist, cmd, args, out = None, err = None) :
#             """
#             Spawn the command
# 
#             @param hostlist list of host to spawn task
#             @param cmd command name
#             @param args command argument
#             @param out output file object
#             @param err error file object
#             @return 0 if no task fail, otherwise -1
#             """
#             pass
# 
#     class SshClient(threading.Thread) :
#         def __init__(self, **kwargs) :
#             threading.Thread.__init__(self)
#             self.spawner = kwargs['spawner'] = spawner
#             self.rt_output = kwargs.get('rt_output', False)
#             self.connect_timeout = kwargs.get('connect_timeout', 15)
#             self.port = kwargs.get('port', 22)
#             self.password = kwargs.get('password', None)
#             self.ssh = paramiko.SSHClient()
#             self.transport = None
#             self.host = ''
#             self.poller = select.poll()
# 
#         def show_out(self, outputs) :
#             '''
#             Display output from execution to stdout/stderr
# 
#             @param outputs list of output file
#             '''
#             for file,out in outputs :
#                 f = open(file, 'r')
#                 out.write(f.read())
#                 f.close()
# 
#         def run(self) :
#             exit = False
#             while True :
#                 self.spawner.host_list_mutex.acquire()
#                 if self.spawner.host_list :
#                     self.host = self.spawner.host_list[0]
#                     del self.spawner.host_list[0]
#                 else :
#                     exit = True
#                 self.spawner.host_list_mutex.release()
#                 try :
#                     if not exit :
#                         finish = False
#                         if self.transport :
#                             self.transport.close()
#                         self.ssh.connect(host, port=self.port, password=self.password, timeout = self.connect_timeout)
#                         self.transport = self.ssh.get_transport()
#                         session = self.transport.open_session()
#                         session.shutdown_write()
#                         self.poller.register(session, POLLIN)
#                         output_file, output_path = tempfile.mkstemp()
#                         error_file, error_path = tempfile.mkstemp()
# 
#                         # main loop to process input/output
#                         while not finish :
#                             events = self.poller.poll()
#                             for event in events :
#                                 data = ''
#                                 if session.recv_stderr_ready() :
#                                     data = session.recv_stderr(1024)
#                                     storage = output_file
#                                 else :
#                                     data = session.recv(1024)
#                                     storage = error_file
#                                 if data :
#                                     os.write(storage)
#                                 else :
#                                     os.close(output_file)
#                                     os.close(error_file)
#                                     session.shutdown()
#                                     session.close()
#                                     finish = True
#                         # showing output
#                         self.spawner.show_out_mutex.acquire()
#                         self.show_out([(output_path, sys.stdout), (error_path, sys.stderr)])
#                         self.spawner.show_out_mutex.release()
#                         os.remove(output_path)
#                         os.remove(error_path)
#                     else :
#                         break
#                 except :
#                     import traceback
#                     traceback.print_exc()
# 
#         def __del__(self) :
#             if self.transport :
#                 self.transport.close()
#             threading.Thread.__del__(self)
# 
#             
# else :
#     class SshSpawner(Spawner) :
#         def __init__(self, special_arg) :
#             raise InvalLauncher('python-paramiko ssh API is not available')

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
                outfd, tmpout = tempfile.mkstemp()
                errfd, tmperr = tempfile.mkstemp()
                pid = os.fork()
                if pid == 0 :
                    # child
                    sys.stdin.close()
                    os.dup2(outfd, sys.stdout.fileno())
                    os.dup2(errfd, sys.stderr.fileno())
                    spawn_arg = self.buildArg(hostlist[0], cmd, args)
                    os.execvp(spawn_arg[0], spawn_arg)
                else :
                    os.close(outfd)
                    os.close(errfd)
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

        if os.path.basename(config.rsh_cmd) == 'ssh' :
            spawn_arg = [config.rsh_cmd, '-o', 'StrictHostKeyChecking no', '-T', '-n', host]
        else :
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

