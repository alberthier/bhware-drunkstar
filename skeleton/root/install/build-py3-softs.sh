#!/bin/sh

PYTHON3=Python-3.4.2
PYTHON3_ARCHIVE=$PYTHON3.tgz
PYTHON3_VERSIONCODE=\\.cpython-34
PYSERIAL=pyserial-2.7
PYSERIAL_ARCHIVE=$PYSERIAL.tar.gz


move_pyc() {
    echo $1 | grep __pycache__ > /dev/null
    if [ $? -eq 0 ]; then
        SOURCE_FILENAME=`basename $1`
        SOURCE_DIR=`dirname $1`
        DEST_FILENAME=`echo $SOURCE_FILENAME | sed -e "s/$PYTHON3_VERSIONCODE//"`
        DEST_DIR=`dirname $SOURCE_DIR`
        mv "$1" "$DEST_DIR/$DEST_FILENAME"
    fi
}


tar xf $PYTHON3_ARCHIVE
cd $PYTHON3
find . -name "*" -exec touch {} \;
touch Include/Python-ast.h Python/Python-ast.c Objects/typeslots.inc Python/opcode_targets.h
./configure --enable-shared --disable-ipv6
make
make install
ldconfig
cd ..

tar xf $PYSERIAL_ARCHIVE
cd $PYSERIAL
find . -name "*" -exec touch {} \;
python3 setup.py build
python3 setup.py install
cd ..


# Cleaning
strip /usr/local/bin/python3.4
strip /usr/local/bin/python3.4m
find /usr/local/lib -name "*.so" -exec strip {} \;
rm -rf /usr/local/lib/python3.4/test
find /usr/local/lib/python3.4/site-packages -name "*.py" -exec python3 -m py_compile {} \;
for PYC in `find /usr/local/lib/python3.4 -name "*.pyc" -print`; do
    move_pyc $PYC
done
find /usr/local/lib/python3.4 -name "*.py" -exec rm -f {} \;
find /usr/local/lib/python3.4 -name "__pycache__" -exec rm -rf {} \;
rm -f /usr/local/lib/python3.4/config-3.4m/libpython3.4m.a
rm -rf /usr/local/share
ldconfig

