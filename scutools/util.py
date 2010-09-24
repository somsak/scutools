"""
Generic Utility

@author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""

try :
    import subprocess
    has_subprocess = 1
except ImportError :
    has_subprocess = 0

import os
import config

sut_hostlen = config.sut_hostlen

def trim_host(host) :
    """Trim down hostname to only host, no domain"""
    out = host.split('.', 1)[0]
    if len(out) > sut_hostlen :
        out = out[:sut_hostlen]
    return out

def ping_check(host) :
    '''
    Check status of a host with ping
    '''
    ping_args = config.ping_args.split()
    retcode = -1
    if has_subprocess :
        null = open('/dev/null', 'w')
        retcode = subprocess.call([config.ping] + ping_args + [host], stdout = null, stderr = subprocess.STDOUT)
        null.close()
    else :
        exit_stat = os.system('%s %s %s > /dev/null 2>&1' % (config.ping, config.ping_args, host))
        retcode = os.WEXITSTATUS(exit_stat)

    return retcode

if __name__ == '__main__' :
    import socket, sys
    print trim_host(socket.gethostname())
    if len(sys.argv) > 1 :
        print trim_host(sys.argv[1])
