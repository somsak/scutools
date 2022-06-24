"""
Generic configuration for all SUT command
Could be initialized from config file

@author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""
import os,tempfile
from configparser import ConfigParser

conf_name = 'scutools.conf'
conf_part = 'part'
conf_dir_list = [\
    os.path.join(os.path.expanduser('~'), '.scutools'),
    '/etc/scutools',
    '/usr/etc/scutools',
    '/usr/local/etc/scutools',
]
partfile_dir = ''

for dir in conf_dir_list :
    full_path = os.path.join(dir, conf_name)
    if os.access(full_path, os.R_OK) :
        config_file = full_path
    full_path = os.path.join(dir, conf_part)
    if os.path.exists(full_path) and os.path.isdir(full_path) :
        partfile_dir = full_path

rsh_cmd = 'ssh'
rcp_cmd = 'scp'
rsync_cmd = 'rsync'
max_rshbg = 10
def_spawner = 'rsh'
def_rdup = 'rsync'
tmpdir = tempfile.gettempdir()
sut_hostlen = 14
hostlist_src = 'file'
hostlist = []
gstat = 'gstat'
sce_host = 'sce_host'
ping = '/bin/ping'
ping_args = '-c 1 -W 1'
ping_check = False
default_host_arg = None

ansible_hosts = '/etc/ansible/hosts'

try :
    _config = ConfigParser()
    _config.read(config_file)
    if _config.has_section('main') :
        if _config.has_option('main', 'max_rshbg') :
            max_rshbg = int(_config.get('main', 'max_rshbg'))
        if _config.has_option('main', 'hostname_len') :
            sut_hostlen = int(_config.get('main', 'hostname_len'))
        if _config.has_option('main', 'hostlist_src') :
            hostlist_src = _config.get('main', 'hostlist_src')
        if _config.has_option('main', 'sce_host') :
            sce_host = _config.get('main', 'sce_host')
        if _config.has_option('main', 'gstat') :
            gstat = _config.get('main', 'gstat')
        if _config.has_option('main', 'rsh') :
            rsh_cmd = _config.get('main', 'rsh')
        if _config.has_option('main', 'rcp') :
            rcp_cmd = _config.get('main', 'rcp')
        if _config.has_option('main', 'rsync') :
            rsync_cmd = _config.get('main', 'rsync')
        if _config.has_option('main', 'use_rsync') :
            val = _config.get('main', 'use_rsync').lower()
            if val == 'yes' or val == 'true' :
                def_rdup = 'rsync'
            else :
                def_rdup = 'rcp'
        if _config.has_option('main', 'ping') :
            ping = _config.get('main', 'ping')
        if _config.has_option('main', 'ping_args') :
            ping_args = _config.get('main', 'ping_args')
        if _config.has_option('main', 'ping_check') :
            ping_check = _config.get('main', 'ping_check')
            if ping_check == '1' or ping_check == 'true' or ping_check == 'yes' :
                ping_check = True
        if _config.has_option('main', 'default_host_arg') :
            default_host_arg = _config.get('main', 'default_host_arg')
        if _config.has_option('main', 'ansible_hosts') :
            ansible_hosts = _config.get('main', 'ansible_hosts')
    if _config.has_section('hostlist') :
        for option, value in _config.items('hostlist') :
            hostlist.append(value)
except :
    pass
