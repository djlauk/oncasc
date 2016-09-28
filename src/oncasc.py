#!/usr/bin/env python
# ----------------------------------------------------------------------
# oncasc - On Call Scheduler
#
# See LICENSE.md for details.
# ----------------------------------------------------------------------

import getopt
import json
import os
import random
import sys
import time


__PROG = os.path.basename(sys.argv[0])
__DEBUG_ENABLED = os.environ.get('DEBUG', '0').lower() in ('1', 'yes', 'y', 'on', 'true')
if __DEBUG_ENABLED:
    import traceback
    def debug(msg):
        sys.stdout.write("DEBUG: %s %s\n" % (time.strftime('%Y-%m-%d %H:%M:%S'), msg))
else:
    def debug(msg):
        pass


class TeamMember(object):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name')
        self.unavailable = kwargs.get('unavailable', [])
        debug("Created team member %s, not available for: %s" % (self.name, str(self.unavailable)))
    
    def __str__(self):
        return self.name


def main():
    debug("Starting")
    opts, args = getopt.getopt(sys.argv[1:], 'ht:s:')
    team = None
    time_slots = None
    for o, v in opts:
        if o == '-h':
            help()
            sys.exit(0)
        elif o == '-t':
            team = read_team(v)
        elif o == '-s':
            time_slots = read_time_slots(v)
    if not team:
        raise RuntimeError("No team file provided")
    if not time_slots:
        raise RuntimeError("No time slots provided")
    schedule = generate_schedule(team, time_slots)
    print_schedule(schedule)
    debug("Done")


def help():
    sys.stdout.write("""
Usage: %(prog)s OPTIONS

OPTIONS
  -h          Display instructions and exit
  -t FILE     Read on call team info from FILE
  -s FILE     Read schedule from FILE
""" % {
    'prog': os.path.basename(sys.argv[0])
})


def read_team(fname):
    debug("Reading team from %s" % fname)
    team = []
    for li in read_file(fname):
        parts = [x.strip() for x in li.split(':', 1)]
        if len(parts) == 1:
            team.append(TeamMember(name=parts[0]))
        else:
            team.append(TeamMember(name=parts[0], unavailable=[x.strip() for x in parts[1].split(',')]))
    debug("Team: %s" % str([str(x) for x in team]))
    return team


def read_file(fname):
    f = file(fname, 'r')
    lines = [x.strip() for x in f.readlines() if len(x.strip()) > 0 and not x.strip().startswith('#')]
    f.close()
    return lines


def read_time_slots(fname):
    debug("Reading time slots from %s" % fname)
    return read_file(fname)


def generate_schedule(team, time_slots):
    schedule = {}
    random.shuffle(team)
    debug("Shuffled team: %s" % str([str(x) for x in team]))
    skipped = []
    next_team_member = 0
    for slot in time_slots:
        debug("Processing time slot '%s'" % str(slot))
        if len(skipped) > 0:
            debug("Checking skipped people...")
            found = False
            for i in range(len(skipped)):
                debug("Checking skipped person %d: %s" % (i, skipped[i]))
                if slot not in skipped[i].unavailable:
                    debug("Person is available")
                    schedule[slot] = skipped[i].name
                    del skipped[i]
                    found = True
                    break
                else:
                    debug("Person is not available")
            if found:
                continue   # proceed to next slot, if this one could be assigned

        debug("Checking team, starting at index %d" % next_team_member)
        found = False
        for offset in range(len(team)):
            i = (next_team_member + offset) % len(team)
            debug("Check %d: %s" % (i, team[i]))
            if slot in team[i].unavailable:
                debug("Person is not available... postponing")
                skipped.append(team[i])
            else:
                debug("Person is available")
                schedule[slot] = team[i].name
                next_team_member = (i + 1) % len(team)
                found = True
                break
        if found:
            continue   # proceed to next slot, if this one could be assigned
        sys.stdout.write("WARNING: No team member available for slot '%s'" % slot)
        
    return schedule


def print_schedule(schedule):
    keys = schedule.keys()
    keys.sort()
    for k in keys:
        sys.stdout.write("%s: %s\n" % (k, schedule[k]))


if __name__ == '__main__':
    try:
        main()
    except Exception, e:
        sys.stderr.write("%s: %s\n" % (__PROG, str(e)))
        if __DEBUG_ENABLED:
            traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
