RH_RELEASE=`cat /etc/redhat-release 2> /dev/null | sed 's/.* release \([0-9.]*\) .*/\1/g'`
case "$RH_RELEASE" in
    5.*)
        python2.6 setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
        ;;
    *)
        python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
        ;;
esac
# 'brp-compress' gzips the man pages without distutils knowing... fix this
sed -i -e 's@man/man\([[:digit:]]\)/\(.\+\.[[:digit:]]\)$@man/man\1/\2.gz@g' INSTALLED_FILES

case "$RH_RELEASE" in
    7*)
        cat INSTALLED_FILES | grep "\.pyc$" | sed 's/\.pyc/.pyo/g' > /tmp/setup_py_scutools.tmp
        cat /tmp/setup_py_scutools.tmp >> INSTALLED_FILES
        rm -f /tmp/setup_py_scutools.tmp
        ;;
esac
