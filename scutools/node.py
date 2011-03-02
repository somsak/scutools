"""
  Wrapper for node information fetching
          
  @author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""

import os, sys, commands, string, socket
from scutools import config
from scutools.error import NodeStatus

ALIVE = 0x1
ALL = 0x2
ALL_EXC = 0x4

class HostSrc(object) :
    def get_alive(self, flag = None) :
        host_list = config.hostlist
        if flag and (flag & ALL_EXC) :
            my_hostname = socket.gethostname()
            short_hostname = my_hostname.split('.', 1)[0]
            for i in range(len(host_list)) :
                if (host_list[i] == my_hostname) or (host_list[i].split('.', 1)[0] == short_hostname) :
                    del host_list[i]
                    break

        return host_list

class ScmsHostSrc(HostSrc) :
    def get_alive(self, flag) :
        cmd = None
        opt = ''
        if flag and (flag & ALL) :
            # get only alive node
            opt = opt + ' -a'
        if flag and (flag & ALL_EXC) :
            opt = opt + ' -e'
        cmd = config.sce_host + opt
        status, output = commands.getstatusoutput(cmd)
        if status == 0 :
            host_list = string.split(output)
            if (flag & ALL) or (flag & ALL_EXC) :
                for host in HostSrc.get_alive(self) :
                    if not host in host_list :
                        host_list.append(host)
        else :
            raise NodeStatus, 'sce_host ' + opt

class GstatHostSrc(HostSrc) :
    def get_alive(self, flag) :
        host_list = []
        gstat_cmd = os.popen(config.gstat + ' -a -m -l', 'r')
        while True :
            line = gstat_cmd.readline()
            if not line: break
            host, ncpu = line.strip().split(':')
            host_list.append(host)
        exit_stat = gstat_cmd.close()
        if not exit_stat is None :
            raise NodeStatus, 'gstat -a -m -l'

        if flag and (flag & ALL) :
            gstat_cmd = os.popen(config.gstat + ' -d -1 -l', 'r')
            while True :
                line = gstat_cmd.readline()
                if not line: break
                if line.find('There are no hosts down') >= 0 :
                    break
                else :
                    host, time = line.strip().split(' ', 1)
                    # ganglia report short-hostname instead of full name
                    hostent = socket.gethostbyname_ex(host)
                    host_list.append(hostent[0])
            exit_stat = gstat_cmd.close()
            if not exit_stat is None :
                raise NodeStatus, 'gstat -a -m -l'

            # also use hostlist defined in configuration file
            for host in HostSrc.get_alive(self) :
                if not host in host_list :
                    host_list.append(host)

        if flag and (flag & ALL_EXC) :
            my_hostname = socket.gethostname()
            short_hostname = my_hostname.split('.', 1)[0]
            for i in range(len(host_list)) :
                if (host_list[i] == my_hostname) or (host_list[i].split('.', 1)[0] == short_hostname) :
                    del host_list[i]
                    break
        return host_list

def get_alive(flag = ALIVE) :
    if config.hostlist_src == 'gstat' :
        host_src = GstatHostSrc()
    elif config.hostlist_src == 'sce_host' :
        host_src = ScmsHostSrc()
    elif config.hostlist_src == 'file' :
        host_src = HostSrc()

    return host_src.get_alive(flag = flag)

if __name__ == '__main__' :
    print '*** alive nodes ***'
    print get_alive(ALIVE)
    print '*** all nodes ***'
    print get_alive(ALL)
    print '*** all nodes except self ***'
    print get_alive(ALIVE | ALL_EXC)
