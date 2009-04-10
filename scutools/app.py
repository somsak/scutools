'''
    Main command for all parallel command
    
    @author Somsak Sriprayoonsakul <somsaks@gmail.com>
'''
import sys,os
global progname
progname = os.path.basename(sys.argv[0])

def print_error(errstr) :
    sys.stderr.write('%s:%s\n' % (progname, errstr))

def main() :
    from scutools.pexec import PExec
    from scutools.error import InvalArg,NodeStatus,InvalHost

    execer = None

    try :

        if progname == 'pexec' :
            if len(sys.argv) == 1 : raise InvalArg, 'missing argument'
            execer = PExec(None, sys.argv[1:])
        elif progname == 'pls' :
            execer = PExec('ls', sys.argv[1:])
        elif progname == 'pps' :
            execer = PExec('ps', sys.argv[1:])
        elif progname == 'pcp' :
            if len(sys.argv) == 1 : raise InvalArg, 'missing argument'
            execer = PExec('cp', sys.argv[1:])
        elif progname == 'pmv' :
            if len(sys.argv) == 1 : raise InvalArg, 'missing argument'
            execer = PExec('mv', sys.argv[1:])
        elif progname == 'prm' :
            if len(sys.argv) == 1 : raise InvalArg, 'missing argument'
            execer = PExec('rm', sys.argv[1:])
        elif progname == 'pcat' :
            if len(sys.argv) == 1 : raise InvalArg, 'missing argument'
            execer = PExec('cat', sys.argv[1:])
        elif progname == 'pfind' :
            execer = PExec('find', sys.argv[1:])
        elif progname == 'pdist' :
            from scutools.pdist import PDist
            execer = PDist(sys.argv[1:])
        elif progname == 'pfps' :
            from scutools.pfps import Pfps
            execer = Pfps(sys.argv[1:])
        elif progname == 'pkillps' :
            from scutools.pkill import Pkillps
            execer = Pkillps(sys.argv[1:])
        elif progname == 'pkillu' :
            from scutools.pkill import Pkillu
            execer = Pkillu(sys.argv[1:])
        elif progname == 'ppred' :
            from scutools.ptest import Ptest
            execer = Ptest(sys.argv[1:])
        elif progname == 'ptest' :
            from scutools.ptest import Ptest
            execer = Ptest(sys.argv[1:])
        else :
            print_error('invalid command name %s' % (progname))
            sys.exit(1)
        retval = execer.launch()
        sys.exit(retval)
    except (NodeStatus, InvalHost, InvalArg), e :
        print_error(e)
    except KeyboardInterrupt, e :
        print_error('interrupted by user')
    except SystemExit :
        raise
    except Exception, e :
        print_error(e)
        raise
    sys.exit(1)
