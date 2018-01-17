"""
dirhash: Produce a checksum, similar to a hash, for directories.
"""

__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.0.1"


import sys
import argparse
from os import scandir
from hashlib import new


def checksum(fp, chunksize=1000000, algo='md5'):
    """
    Produce a hashlib.hash object which contains the checksum of a file

    :param str fp: The filepath to the file to be hashed
    :param int chunksize: The maximum amount of the file to read into RAM at once
    :param str algo: The hashing algorithm to use, fed to :func:`hashlib.new`
    :returns: A :class:`_hashlib.HASH` object containing the hash of the file
    :rtype: :class:`_hashlib.HASH`
    """
    h = new(algo)
    with open(fp, 'rb') as f:
        chunk = f.read(chunksize)
        while chunk:
            h.update(chunk)
            chunk = f.read(chunksize)
    return h


def get_parser():
    """
    Create the parser for the CLI

    :returns: The parser
    :rtype: :class:`argparse.ArgumentParser`
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "directory", type=str,
        help="The path to the directory to hash"
    )
    parser.add_argument(
        "-c", "--chunksize", type=int, default=1000000,
        help="How many bytes (maximum) of a file to read into RAM at once"
    )
    parser.add_argument(
        "-a", "--algo", type=str, default='md5',
        help="The algorithm to employ internally ingenerating the hash"
    )
    parser.add_argument(
        "--no-symlinks", action='store_true',
        help="If present, treat symlinks as if they don't exist"
    )
    return parser


def hash_dir(d, chunksize=1000000, algo='md5', resolve_symlinks=True):
    """
    Produce the 'hash' of a directory recursively.

    Directory 'hashes', much like file hashes, when compared, can confirm
    that each contains an identical series of bytes. In the case of
    the directory 'hash' these bytes must be an identical set of files,
    but all attributes of the files except their contents is ignored.

    :param str d: The path to the directory to hash
    :param int chunksize: The maximum amount of any file to read into RAM at once
    :param str algo: The hashing algorithm to use, fed to :func:`hashlib.new`
    :param bool resolve_symlinks: Whether or not to resolve symlinks. If False symlinks
        will be ignored completely, and not factor into the hash.
    :returns: A :class:`_hashlib.HASH` object containing the hash of the directory
    :rtype: :class:`_hashlib.HASH`
    """
    h = new(algo)
    files = []
    symlinks = []
    others = []
    subdirs = []
    for x in scandir(d):
        if x.is_file():
            files.append(x)
        elif x.is_dir():
            subdirs.append(x)
        elif x.is_symlink():
            symlinks.append(x)
        else:
            others.append(x)

    if symlinks and resolve_symlinks:
        # resolve symlinks, add to the proper arrays here
        pass

    if len(others) > 0:
        raise NotImplementedError()

    file_hashes = [
        checksum(x.path, chunksize=chunksize, algo=algo)
        for x in files
    ]
    sorted_file_hashes = sorted(file_hashes, key=lambda x: x.hexdigest())

    # Recurse
    subdir_hashes = [
        hash_dir(x.path, chunksize=chunksize, algo=algo, resolve_symlinks=resolve_symlinks)
        for x in subdirs
    ]
    sorted_subdir_hashes = sorted(subdir_hashes, key=lambda x: x.hexdigest())

    for x in sorted_file_hashes + sorted_subdir_hashes:
        h.update(x.digest())

    return h


def main(args):
    """
    Ingest the arguments, perform the operation

    :param argparse.Namespace args: The parsed arguments
    :returns: A :class:`_hashlib.HASH` object containing the hash of the directory
    :rtype: :class:`_hashlib.HASH`
    """
    h = hash_dir(
        args.directory,
        chunksize=args.chunksize,
        algo=args.algo,
        resolve_symlinks=not args.no_symlinks
    )
    return h


def cli():
    """
    Retrieve a parser, parse the args, feed them into :func:`main`, write out the hexdigest.
    """
    parser = get_parser()
    args = parser.parse_args()
    result = main(args)
    sys.stdout.write("{}\n".format(result.hexdigest()))
    exit(0)


if __name__ == '__main__':
    cli()
