"""
Generic configuration for all SUT command
Could be initialized from config file

@author Somsak Sriprayoonsakul <somsaks@gmail.com>
"""
import os,tempfile
from ConfigParser import ConfigParser

conf_name = 'scutools.conf'
conf_part = 'part'
conf_dir_list = [\
    os.path.join(os.path.expanduser('~'), '.scutools'),
    '/etc',
    '/usr/etc',
    '/usr/local/etc',
]

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
def_rdup = 'rcp'
tmpdir = tempfile.gettempdir()
sut_hostlen = 14
hostlist_src = 'gstat'
gstat = 'gstat'
sce_host = 'sce_host'

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
except :
    pass
