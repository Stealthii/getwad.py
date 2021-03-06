#!/usr/bin/env python

"""
  Doom WAD retrieval tool
  Original Author: Daniel Porter
  Original Date: Nov 19, 2014
  Description:

  A tool for querying WAD repositories, and downloading. Or shit.

  cmdLine args are:
  name (name of wad)

  optionally:
  --waddir=dir (overrides $DOOMWADDIR)
"""

from __future__ import print_function

import argparse
import os
import sys
import textwrap
import urllib2
import zipfile
import StringIO


def main():
    parser = argparse.ArgumentParser(description="Member Checker Tool")
    parser.add_argument('name', help='The name of the wad')
    parser.add_argument('--waddir', help='Location for wads', type=str,
                        default=os.getenv('DOOMWADDIR'))
    args = vars(parser.parse_args())

    if not args['waddir']:
        log_error(textwrap.dedent("""\
            You need to set $DOOMWADDIR in your environment to a
            directory where you wish to store PWADs. This also lets
            Zandronum and other software know where to look.

            Hint: $HOME/.zandromum is bad. Try:
              $HOME/.zandronum/wads, or
              $HOME/doom/wads."""))
        sys.exit(1)

    wad = get_wad(name=args["name"], repos=get_wad_repos())
    if not wad:
        log_error("We couldn't find the WAD file!")
        sys.exit(1)
    log('Writing...')
    filepath = os.path.join(args["waddir"], args["name"] + ".wad")
    f = open(filepath, 'wb')
    f.write(wad)
    f.close()
    log('WAD file written to %s' % filepath)


def get_wad_repos():
    """Returns a list of places to get wads"""
    master_list = ("http://getwad.keystone.gr/master/",
                   "http://zdaemon.org/getwad/")
    for url in master_list:
        try:
            repo_list = urllib2.urlopen(url).read()
            if repo_list:
                return repo_list.split()
        except urllib2.URLError as e:
            if hasattr(e, 'reason'):
                log_warning('We failed to reach a server.')
                log_warning('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                log_warning('The server couldn\'t fulfill the request.')
                log_warning('Error code: ', e.code)
    return None


def get_wad(name, repos):
    """Returns first response on a valid wad link"""
    # TODO: Be a generator so can return other links to the wad if any fail
    for filename in (name + ".zip", name + ".pk3", name + ".wad"):
        for repo in repos:
            log('Trying %s' % repo)
            try:
                if "%s" in repo:
                    response = urllib2.urlopen(repo % filename)
                else:
                    response = urllib2.urlopen(repo + filename)

                if response.getcode() == 200:
                    log('Retrieving file...')
                    wad = get_wad_content(response, name)
                    if wad:
                        return wad

            except urllib2.URLError as e:
                if hasattr(e, 'reason'):
                    log_warning('We failed to reach a server.')
                    log_warning('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    log_warning('The server couldn\'t fulfill the request.')
                    log_warning('Error code: ', e.code)

    return None


def get_link(response):
    """Gets a link from the response"""
    return response.geturl()


def get_wad_content(response, name):
    """Attempts to get wad content from response"""
    # TODO: .pk3 and .wad should be left in place, zips should be checked for
    # .wad file of same name, and should extract $name.wad and $name.txt if
    # applicable. For now, just 'if zip, extract'
    filehandle = StringIO.StringIO(response.read())

    if zipfile.is_zipfile(filehandle):
        log('Extracting WAD from zip file...')
        archive = zipfile.ZipFile(filehandle, 'r')
        filenames = [fname for fname in archive.namelist()
                     if name + '.wad' == fname.lower()]
        if filenames:
            wad = archive.read(filenames[0])
    else:
        wad = filehandle.read()

    log('Validating...')
    if wad[1:4] == 'WAD':
        return wad
    else:
        log_warning('Not a WAD file!')


def log_error(*objs):
    print("ERROR:", *objs, file=sys.stderr)


def log_warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)


def log(*objs):
    print(*objs, file=sys.stdout)


if __name__ == '__main__':
    main()
