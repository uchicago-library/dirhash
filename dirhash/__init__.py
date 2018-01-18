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
from json import dump, load, dumps


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
        help="The algorithm to employ internally for generating the checksum"
    )
    parser.add_argument(
        "--no-symlinks", action='store_true',
        help="If present, treat symlinks as if they don't exist"
    )
    parser.add_argument(
        "--write-cache", type=str, default=None,
        help="A filepath to write the cache to. Cache is not written if not provided"
    )
    return parser


def hash_dir(d, chunksize=1000000, algo='md5', resolve_symlinks=True, cache={}):
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
    :param dict cache: A dictionary where the keys are filepaths and the values are
        :class:`_hashlib.HASH` objects which are in the necessary state to produce
        digests and hexdigests when called. If a path exists in the cache it
        will not be rehashed when encountered.
    :returns: A :class:`tuple`, the first element of which is a :class:`_hashlib.HASH` object
        containing the hash of the directory. The second element of which is the cache
        :class:`dict` - keys are filepaths and values are :class:`_hashlib.HASH` objects for all
        subdirectories and files.
    :rtype: :class:`tuple`
    """
    h = new(algo)
    files = []
    others = []
    subdirs = []
    for x in scandir(d):
        # scandir will return True to both
        # DirEntry.is_symlink() and DirEntry.is_dir() if something
        # is a symlink to a dir, same for files and .is_file().
        #
        # Note the division of the if here and the
        # following if/elif/else block for this reason
        if x.is_symlink() and resolve_symlinks is False:
            continue

        if x.is_file():
            files.append(x.path)
        elif x.is_dir():
            subdirs.append(x.path)
        else:
            others.append(x.path)

    if len(others) > 0:
        raise NotImplementedError()

    # Hash the files
    file_hashes = []
    for x in files:
        if x in cache:
            file_hashes.append(cache[x])
        else:
            fh = checksum(x, chunksize=chunksize, algo=algo)
            file_hashes.append(fh)
            cache[x] = fh
    # Sort them by hexdigest so we reliably get the same order by content
    sorted_file_hashes = sorted(file_hashes, key=lambda x: x.hexdigest())

    # Hash the subdirs (recursive)
    subdir_hashes = []
    for x in subdirs:
        if x in cache:
            subdir_hashes.append(cache[x])
        else:
            # Recurse
            dh, cache = hash_dir(
                x, chunksize=chunksize,
                algo=algo, resolve_symlinks=resolve_symlinks,
                cache=cache
            )
            subdir_hashes.append(dh)
            cache[x] = dh
    # Sort them by hexdigest so we reliably get the same order by content
    sorted_subdir_hashes = sorted(subdir_hashes, key=lambda x: x.hexdigest())

    # Hash together all the subhashes
    for x in sorted_file_hashes + sorted_subdir_hashes:
        h.update(x.digest())

    # Final cache update
    cache[d] = h

    return h, cache


def main(args):
    """
    Ingest the arguments, perform the operation

    :param argparse.Namespace args: The parsed arguments
    :returns: A :class:`_hashlib.HASH` object containing the hash of the directory
    :rtype: :class:`_hashlib.HASH`
    """
    h, cache = hash_dir(
        args.directory,
        chunksize=args.chunksize,
        algo=args.algo,
        resolve_symlinks=not args.no_symlinks
    )
    return h, cache


def cli():
    """
    Retrieve a parser, parse the args, feed them into :func:`main`, write out the hexdigest.
    """
    parser = get_parser()
    args = parser.parse_args()
    r, cache = main(args)
    if args.write_cache:
        with open(args.write_cache, 'w') as f:
            dump({x: cache[x].hexdigest() for x in cache}, f, indent=2)

    sys.stdout.write("{}\n".format(r.hexdigest()))
    exit(0)


def getdupes():
    """
    Little utility for processing cache outputs in order
    to pull out duplicates
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("cachefile", type=str, help='The path to the cache file')
    parser.add_argument("-o", "--outfile", type=str, help="Path to output the "
                        "duplicate JSON file to, defaults to stdout", default="-")
    args = parser.parse_args()

    with open(args.cachefile) as f:
        cache = load(f)

    by_hash = {}
    for x in cache:
        if by_hash.get(cache[x]) is None:
            by_hash[cache[x]] = []
        by_hash[cache[x]].append(x)
    dupes = {x: by_hash[x] for x in by_hash if len(by_hash[x]) > 1}
    if args.outfile == "-":
        sys.stdout.write(dumps(dupes, indent=2))
    else:
        with open(args.outfile, 'w') as f:
            dump(dupes, f)


if __name__ == '__main__':
    cli()
