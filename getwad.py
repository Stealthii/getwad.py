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
import urllib2


def main():
    parser = argparse.ArgumentParser(description="Member Checker Tool")
    parser.add_argument('name', help='The name of the wad')
    parser.add_argument('--waddir', help='Location for wads', type=str,
                        default=os.getenv('DOOMWADDIR'))
    parser.add_argument('--getlink', help='Return a link to the wad instead', type=bool)
    args = vars(parser.parse_args())

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
                break
        except urllib2.HTTPError:
            pass
    return repo_list.split()


def get_response(name, repos):
    """Returns first response on a valid wad link"""
    for filename in (name + ".zip", name + ".pk3", name + ".wad"):
        for repo in repos:
            if "%s" in repo:
                response = urllib2.urlopen(repo % filename)
            else:
                response = urllib2.urlopen(repo + filename)
            if response.getcode() == 200:
                return response


def log_error(*objs):
    print("ERROR:", *objs, file=sys.stderr)


def log_warning(*objs):
    print("WARNING:", *objs, file=sys.stderr)


def log(*objs):
    print(*objs, file=sys.stdout)


if __name__ == '__main__':
    main()
