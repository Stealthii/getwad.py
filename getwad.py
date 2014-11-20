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
  --getlink (prints a link to the wad rather than downloading it)
"""

from __future__ import print_function

import argparse
import os
import sys
import textwrap
import urllib2


def main():
    parser = argparse.ArgumentParser(description="Member Checker Tool")
    parser.add_argument('name', help='The name of the wad')
    parser.add_argument('--waddir', help='Location for wads', type=str,
                        default=os.getenv('DOOMWADDIR'))
    parser.add_argument('--getlink', help='Return a link to the wad instead', type=bool)
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

    response = get_response(name=args["name"],
                            repos=get_wad_repos())

    get_wad(response, waddir=args["waddir"],
            links=args["getlink"])


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


def get_response(name, repos):
    """Returns first response on a valid wad link"""
    # TODO: Be a generator so can return other links to the wad if any fail
    for filename in (name + ".zip", name + ".pk3", name + ".wad"):
        for repo in repos:
            try:
                if "%s" in repo:
                    response = urllib2.urlopen(repo % filename)
                else:
                    response = urllib2.urlopen(repo + filename)

                if response.getcode() == 200:
                    return response

            except urllib2.URLError as e:
                if hasattr(e, 'reason'):
                    log_warning('We failed to reach a server.')
                    log_warning('Reason: ', e.reason)
                elif hasattr(e, 'code'):
                    log_warning('The server couldn\'t fulfill the request.')
                    log_warning('Error code: ', e.code)

    return None


def get_wad(response):
    """Attempts to get wad from response."""
    # TODO: .pk3 and .wad should be left in place, zips should be checked for
    # .wad file of same name, and should extract $name.wad and $name.txt if
    # applicable. For now, just 'if zip, extract'


def log_error(*objs):
    print("ERROR:", *objs, file=sys.stderr)


def log_warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)


def log(*objs):
    print(*objs, file=sys.stdout)


if __name__ == '__main__':
    main()
