#!/usr/bin/env python3

import requests
import json
import sys

seen = dict()

def fetch(url):
    sys.stderr.write(".")
    sys.stderr.flush()
    r = requests.get(url)
    return json.loads(r.text)

def walk(repo):
    for r in fetch('https://api.github.com/repos/' + repo + '/git/refs'):
        process_ref(r)
    return seen.keys()

def see(hash,type):
    t = seen.get(hash)
    if t is None:
        seen[hash] = type
        return False
    if t == type:
        return True
    print("Weird-ass hash collision: {0}".format(hash))
    return False
    

def process_ref(r):
    type = r['object']['type']
    if type == 'commit':
        process_commit(r['object'])

def process_commit(c):
    if see(c['sha'], 'commit'):
        return
    data = fetch(c['url'])
    process_tree(data['tree'])
    for p in data['parents']:
        process_commit(p)

def process_tree(t):
    if see(t['sha'], 'tree'):
        return
    data = fetch(t['url'])
    for o in data['tree']:
        if o['type'] == 'tree':
           process_tree(o)
        if o['type'] == 'blob':
           process_blob(o)

def process_blob(b):
    see(b['sha'], 'blob')


if __name__ == '__main__':
    walk(sys.argv[1])
    for p in seen.items():
        print("{0} {1}".format(*p))
