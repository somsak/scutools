"""
Generic Utility

@author Somsak Sriprayoonsakul
"""

import string
import scutools.config

sut_hostlen = scutools.config.sut_hostlen

def trim_host(host) :
    """Trim down hostname to only host, no domain"""
    out = string.split(host, '.', 1)[0]
    if len(out) > sut_hostlen :
        out = out[:sut_hostlen]
    return out

if __name__ == '__main__' :
    import socket, sys
    print trim_host(socket.gethostname())
    if len(sys.argv) > 1 :
        print trim_host(sys.argv[1])
