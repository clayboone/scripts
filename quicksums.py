#!/usr/bin/env python3

import os
import sys
import subprocess

if len(sys.argv) < 2:
    print('specify a file')
    sys.exit()

fn = sys.argv[1]
if not os.path.isfile(fn):
    print('no file {} could be found'.format(fn))
    sys.exit()

progs = ('md5sum', 'sha1sum', 'sha256sum')

for prog in progs:
    hs = subprocess.check_output([prog, fn])
    print(str(hs.split()[0], encoding='utf-8'), ' -- ', prog)
