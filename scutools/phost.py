"""
Generic interface for Phost

@author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""

from scutools.pexec import PExec
from stat import *
import optparse

class Phost(PExec) :
    def __init__(self, prog_args) :
        PExec.__init__(self, None, prog_args)

    def parseArg(self, prog_args) :
        """Add command to the tail of test command"""
        PExec.parseArg(self, prog_args)
        parser = optparse.OptionParser(usage='Usage: %prog [options]')
        parser.add_option('-n', '--number', dest='number', action='store_true', default=False, help='print number of host')
        self.options, self.args = parser.parse_args(prog_args)

    def launch(self, out = None, err = None) :
        if self.options.number :
            print(len(self.hostlist))
        else :
            for host in self.hostlist :
                print(host)

# if __name__ == '__main__' :
#     cmd = Ptest(['-a', '-f', '/etc/passwd'])
#     print cmd.launch()
#     cmd = Ptest(['-a', '-f', '/etc/pass'])
#     print cmd.launch()
