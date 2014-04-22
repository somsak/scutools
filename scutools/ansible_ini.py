# This file was inspired by Ansible inventory/ini.py. License is as follow

# (c) 2012-2014, Michael DeHaan <michael.dehaan@gmail.com>
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

#############################################

#############################################
# For detect_range and expand_hostname_range
#
# (c) 2012, Zettar Inc.
# Written by Chin Fang <fangchin@zettar.com>
#
# This file is part of Ansible
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#

import os, sys, commands, string, socket
from scutools import config
from scutools.error import NodeStatus, InvalArg

import shlex
import re
import ast

DEFAULT_REMOTE_PORT = 22

def detect_range(line = None):
    '''
    A helper function that checks a given host line to see if it contains
    a range pattern descibed in the docstring above.

    Returnes True if the given line contains a pattern, else False.
    '''
    if (line.find("[") != -1 and
        line.find(":") != -1 and
        line.find("]") != -1 and
        line.index("[") < line.index(":") < line.index("]")):
        return True
    else:
        return False

def expand_hostname_range(line = None):
    '''
    A helper function that expands a given line that contains a pattern
    specified in top docstring, and returns a list that consists of the
    expanded version.

    The '[' and ']' characters are used to maintain the pseudo-code
    appearance. They are replaced in this function with '|' to ease
    string splitting.

    References: http://ansible.github.com/patterns.html#hosts-and-groups
    '''
    all_hosts = []
    if line:
        # A hostname such as db[1:6]-node is considered to consists
        # three parts:
        # head: 'db'
        # nrange: [1:6]; range() is a built-in. Can't use the name
        # tail: '-node'

        # Add support for multiple ranges in a host so:
        # db[01:10:3]node-[01:10]
        # - to do this we split off at the first [...] set, getting the list
        #   of hosts and then repeat until none left.
        # - also add an optional third parameter which contains the step. (Default: 1)
        #   so range can be [01:10:2] -> 01 03 05 07 09
        # FIXME: make this work for alphabetic sequences too.

        (head, nrange, tail) = line.replace('[','|',1).replace(']','|',1).split('|')
        bounds = nrange.split(":")
        if len(bounds) != 2 and len(bounds) != 3:
            raise InvalArg("host range incorrectly specified")
        beg = bounds[0]
        end = bounds[1]
        if len(bounds) == 2:
            step = 1
        else:
            step = bounds[2]
        if not beg:
            beg = "0"
        if not end:
            raise InvalArg("host range end value missing")
        if beg[0] == '0' and len(beg) > 1:
            rlen = len(beg) # range length formatting hint
            if rlen != len(end):
                raise InvalArg("host range format incorrectly specified!")
            fill = lambda _: str(_).zfill(rlen)  # range sequence
        else:
            fill = str

        try:
            i_beg = string.ascii_letters.index(beg)
            i_end = string.ascii_letters.index(end)
            if i_beg > i_end:
                raise InvalArg("host range format incorrectly specified!")
            seq = string.ascii_letters[i_beg:i_end+1]
        except ValueError:  # not a alpha range
            seq = range(int(beg), int(end)+1, int(step))

        for rseq in seq:
            hname = ''.join((head, fill(rseq), tail))

            if detect_range(hname):
                all_hosts.extend( expand_hostname_range( hname ) )
            else:
                all_hosts.append(hname)

        return all_hosts

class Group(object):
    def __init__(self, name = None) :
        self.name = name
        self._groups = {}
        self._hosts = {}

    def add_child_group(self, group) :
        if self._groups.has_key(group) :
            return
        self._groups[group.name] = group
    
    def add_host(self, host):
        self._hosts[host] = 1
    
    def get_hosts(self):
        for name, group in self._groups.iteritems() :
            for host in group.get_hosts() :
                self._hosts[host] = 1
        return self._hosts.keys()
    
    def get_groups(self):
        return self._groups.keys()
    
    def __repr__(self):
        return 'Groups=' + str(self.get_groups()) + ', Hosts=' + str(self.get_hosts())

class InventoryParser(object):
    """
    Host inventory for ansible.
    """

    def __init__(self, filename = config.ansible_hosts):
        if not os.access(filename, os.R_OK) :
            raise InvalArg('can not access ansible host list at ' + filename)
        fh = open(filename, "r")
        self.lines = fh.readlines()
        fh.close()
        self.groups = {}
        self.hosts = {}
        self._parse()

    def _parse(self):

        self._parse_base_groups()
        self._parse_group_children()
        return self.groups


    # [webservers]
    # alpha
    # beta:2345
    # gamma sudo=True user=root
    # delta asdf=jkl favcolor=red

    def _parse_base_groups(self):
        # FIXME: refactor

        ungrouped = Group(name='ungrouped')
        allgroup = Group(name='all')
        allgroup.add_child_group(ungrouped)
        
        self.groups = dict(all = allgroup, ungrouped = ungrouped)
        active_group_name = 'ungrouped'

        for line in self.lines:
            line = line.split("#")[0].strip()
            if line.startswith("[") and line.endswith("]"):
                active_group_name = line.replace("[","").replace("]","")
                if line.find(":vars") != -1 or line.find(":children") != -1:
                    active_group_name = active_group_name.rsplit(":", 1)[0]
                    if active_group_name not in self.groups:
                        new_group = self.groups[active_group_name] = Group(name=active_group_name)
                        allgroup.add_child_group(new_group)
                    active_group_name = None
                elif active_group_name not in self.groups:
                    new_group = self.groups[active_group_name] = Group(name=active_group_name)
                    allgroup.add_child_group(new_group)
            elif line.startswith(";") or line == '':
                pass
            elif active_group_name:
                tokens = shlex.split(line)
                if len(tokens) == 0:
                    continue
                hostname = tokens[0]
                port = DEFAULT_REMOTE_PORT
                # Three cases to check:
                # 0. A hostname that contains a range pesudo-code and a port
                # 1. A hostname that contains just a port
                if hostname.count(":") > 1:
                    # Possible an IPv6 address, or maybe a host line with multiple ranges
                    # IPv6 with Port  XXX:XXX::XXX.port
                    # FQDN            foo.example.com
                    if hostname.count(".") == 1:
                        (hostname, port) = hostname.rsplit(".", 1)
                elif (hostname.find("[") != -1 and
                    hostname.find("]") != -1 and
                    hostname.find(":") != -1 and
                    (hostname.rindex("]") < hostname.rindex(":")) or
                    (hostname.find("]") == -1 and hostname.find(":") != -1)):
                        (hostname, port) = hostname.rsplit(":", 1)

                hostnames = []
                if detect_range(hostname):
                    hostnames = expand_hostname_range(hostname)
                else:
                    hostnames = [hostname]

                for hn in hostnames:
                    host = None
                    if hn in self.hosts:
                        host = self.hosts[hn]
                    else:
                        # we didn't support port in scutools!
                        host = hn
                        self.hosts[hn] = host
#                     if len(tokens) > 1:
#                         for t in tokens[1:]:
#                             if t.startswith('#'):
#                                 break
#                             try:
#                                 (k,v) = t.split("=", 1)
#                             except ValueError, e:
#                                 raise InvalArg("Invalid ini entry: %s - %s" % (t, str(e)))
#                             try:
#                                 host.set_variable(k,ast.literal_eval(v))
#                             except:
#                                 # most likely a string that literal_eval
#                                 # doesn't like, so just set it
#                                 host.set_variable(k,v)
                    self.groups[active_group_name].add_host(host)

    # [southeast:children]
    # atlanta
    # raleigh

    def _parse_group_children(self):
        group = None

        for line in self.lines:
            line = line.strip()
            if line is None or line == '':
                continue
            if line.startswith("[") and line.find(":children]") != -1:
                line = line.replace("[","").replace(":children]","")
                group = self.groups.get(line, None)
                if group is None:
                    group = self.groups[line] = []
            elif line.startswith("#") or line.startswith(";"):
                pass
            elif line.startswith("["):
                group = None
            elif group:
                kid_group = self.groups.get(line, None)
                if kid_group is None:
                    raise InvalArg("child group is not defined: (%s)" % line)
                else:
                    group.add_child_group(kid_group)
    
    def get_hosts(self):
        return self.hosts.keys()
                    
if __name__ == '__main__' :
    ip = InventoryParser(filename=sys.argv[1])
    
    print '--- Group ---'
    print ip.groups['httpserver']
#     print '--- All Group ---'
#     print ip.groups['all']
#     print '--- Ungrouped Group ---'
#     print ip.groups['ungrouped']
#     print '--- Host ---'
#     print ip.get_hosts()