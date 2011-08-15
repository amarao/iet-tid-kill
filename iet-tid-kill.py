#!/usr/bin/python
"""
automatic TID (target) removal from IET
Usage: iet-tid-kill N
,where N - tid number form /proc/net/iet/volume

(C) Selectel, 2011
"""

VOLUME = "/proc/net/iet/volume"
SESSION = "/proc/net/iet/session"
import re,sys
from pprint import pprint
from os import system

def find_with_tail(prefix):
    regexp = re.compile(r"%(pref)s:(\d+)(.+?)(?:(?=%(pref)s:)|$)" %
                        {"pref": prefix}, re.I | re.S)
    return lambda s: regexp.findall(s)

def parse(terms, s):
    f = dict if len(terms) > 1 else lambda x: x
    return f([(int(val), parse(terms[1:], tail)) if len(terms) > 1 else int(val)
              for val, tail in find_with_tail(terms[0])(s)])

def get_volume():
    return parse(["tid", "lun"], file(VOLUME).read())
def get_session():
    return parse(["tid", "sid", "cid"], file(SESSION).read())

def del_cid(tid, sid, cid):
    return system("ietadm --tid %s --sid %s --cid %s --op delete" %
                  (tid, sid, cid))
def del_lun(tid, lun):
    return system("ietadm --tid %s --lun %s --op delete" % (tid, lun))
def del_tid(tid):
    return system("ietadm --tid %s --op delete" % (tid))

if len(sys.argv) == 2:
    tid = int(sys.argv[1])

    session = get_session()
    while True:
        if not session[tid]: break # if no sids in tid
        for sid in session[tid]:
            if not session[tid][sid]: break #if no cids in sid
            for cid in session[tid][sid]:
                del_cid(tid, sid, cid)
        session = get_session()
    volume = get_volume()
    for lun in volume[tid]:
        del_lun(tid, lun)
    del_tid(tid)
else:
    print "usage: %s NUMBER_OF_TID" % (sys.argv[0])
