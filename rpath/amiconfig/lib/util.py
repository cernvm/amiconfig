#
# Copyright (c) 2008 rPath, Inc.
#

import os
import stat
import zlib
import base64
import shutil
import urllib2
import urlparse
import tempfile
import subprocess

def encode(s):
    return base64.encodestring(s).replace('\n', '')

def decode(s):
    return base64.decodestring(s)

def compress(s, level=9):
    return zlib.compress(s, level)

def decompress(s):
    return zlib.decompress(s)

def call(cmd, stdout=None, stderr=None, stdin=None):
    null = open(os.devnull, 'w')
    if not stdout:
        stdout = null
    if not stderr:
        stderr = null
    if not stdin:
        stdin = null
    return subprocess.call(cmd, stdout=stdout, stderr=stderr, stdin=stdin)

def _splitPath(path):
    dirs = []
    current = os.sep
    for level in path.split(os.sep):
        current = os.path.join(current, level)
        dirs.append(current)
    return dirs

def mkdirChain(path):
    for dir in _splitPath(path):
        if not os.path.exists(dir):
            os.mkdir(dir)
            continue
        if not os.path.isdir(dir):
            raise OSError, 'File exists'

def _copystat(src, dst):
    shutil.copystat(src, dst)
    s = os.stat(src)
    uid = s[stat.ST_UID]
    gid = s[stat.ST_GID]
    os.chown(dst, uid, gid)

def copytree(src, dst, symlink=False):
    mkdirChain(os.path.dirname(dst))

    if not os.path.isdir(src):
        shutil.copy2(src, dst)
        return

    shutil.copytree(src, dst, symlink)
    _copystat(src, dst)

    for srcdir, dirs, files in os.walk(src):
        dstdir = dst + os.sep + srcdir[len(src):]
        for element in dirs + files:
            srcE = os.path.join(srcdir, element)
            dstE = os.path.join(dstdir, element)
            _copystat(srcE, dstE)

def movetree(src, dst, symlink=False):
    copytree(src, dst, symlink=symlink)
    shutil.rmtree(src)

def createUnlinkedTmpFile(path=None):
    if path:
        fd, name = tempfile.mkstemp(dir=path)
    else:
        fd, name = tempfile.mkstemp()
    os.unlink(name)
    fh = os.fdopen(fd, 'w')
    return fh

def growFile(fh, size):
    """ Fill a file with zeros up to a specified size. """
    # Convert to mBytes -> kBytes
    size = size * 1024
    kByte = '\x00' * 1024
    for i in range(size):
        fh.write(kByte)
    fh.flush()

def urlgrab(url, filename=None):
    if not filename:
        file = os.path.basename(urlparse.urlsplit(url)[2])
    else:
        file = filename
    fh = open(file, 'w')
    fh.write(urllib2.urlopen(url).read())
    fh.close()
    return file
