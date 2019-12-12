# dirhash [![v0.0.1](https://img.shields.io/badge/version-0.0.1-blue.svg)](https://github.com/uchicago-library/dirhash/releases)

[![Build Status](https://travis-ci.org/uchicago-library/dirhash.svg?branch=master)](https://travis-ci.org/uchicago-library/dirhash) [![Coverage Status](https://coveralls.io/repos/github/uchicago-library/dirhash/badge.svg?branch=master)](https://coveralls.io/github/uchicago-library/dirhash?branch=master) [![Documentation Status](https://readthedocs.org/projects/dirhash/badge/?version=latest)](http://dirhash.readthedocs.io/en/latest/?badge=latest)

Produce a checksum, similar to a hash, for directories.


See the full documentation at https://dirhash.readthedocs.io

## Quickstart

```
$ git clone https://github.com/uchicago-library/dirhash.git
$ cd dirhash
$ python3 -m venv venv
$ source venv/bin/activate
$ python setup.py install
$ dirhash --help
`
```

## CLI Syntax

```
$ dirhash --help
usage: dirhash [-h] [-c CHUNKSIZE] [-a ALGO] [--no-symlinks]
               [--write-cache WRITE_CACHE]
               directory

positional arguments:
  directory             The path to the directory to hash

optional arguments:
  -h, --help            show this help message and exit
  -c CHUNKSIZE, --chunksize CHUNKSIZE
                        How many bytes (maximum) of a file to read into RAM at
                        once
  -a ALGO, --algo ALGO  The algorithm to employ internally for generating the
                        checksum
  --no-symlinks         If present, treat symlinks as if they don't exist
  --write-cache WRITE_CACHE
                        A filepath to write the cache to. Cache is not written
                        if not provided
```

# See Also
[md5deep and hashdeep](http://md5deep.sourceforge.net)

# Author
Brian Balsamo <brian@brianbalsamo.com>
