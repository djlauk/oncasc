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


__PROG = os.path.basename(sys.argv[0])
__DEBUG_ENABLED = os.environ.get('DEBUG', '0').lower() in ('1', 'yes', 'y', 'on', 'true')
if __DEBUG_ENABLED:
    import time
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
    opts, args = getopt.getopt(sys.argv[1:], 'hrs:t:')
    team = None
    time_slots = None
    randomize = None
    for o, v in opts:
        if o == '-h':
            help()
            sys.exit(0)
        elif o == '-r':
            randomize = True
        elif o == '-s':
            time_slots = read_time_slots(v)
        elif o == '-t':
            team = read_team(v)
    if not team:
        raise RuntimeError("No team file provided")
    if not time_slots:
        raise RuntimeError("No time slots provided")
    if randomize:
        random.shuffle(team)
        debug("Team after shuffling:  %s" % [str(x) for x in team])
    schedule = generate_schedule(team, time_slots)
    print_schedule(schedule)
    debug("Done")


def help():
    sys.stdout.write("""
Usage: %(prog)s OPTIONS

OPTIONS
  -h          Display instructions and exit
  -r          Randomize ("shuffle") the team
  -s FILE     Read times for schedule from FILE
  -t FILE     Read on call team info from FILE
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
    time_slots = {}
    for li in read_file(fname):
        parts = [x.strip() for x in li.split(':', 1)]
        if len(parts) == 1:
            time_slots[parts[0]] = None
        else:
            time_slots[parts[0]] = parts[1] or None  # empty string, if somebody puts in a colon, but no reason
    return time_slots


def generate_schedule(team, time_slots):
    schedule = {}
    skipped = []
    next_team_member = 0
    last_assigned = None
    for slot in sorted(time_slots.keys()):
        debug("Processing time slot '%s'" % slot)
        if time_slots[slot]:
            debug("Needs no schedule: %s" % time_slots[slot])
            schedule[slot] = time_slots[slot]
            continue
        if len(skipped) > 0:
            debug("Checking skipped people...")
            found = False
            for i in range(len(skipped)):
                debug("Checking skipped person %d: %s" % (i, skipped[i]))
                if slot in skipped[i].unavailable:
                    debug("Person is not available")
                elif skipped[i] is last_assigned:
                    debug("Person already did time slot before...")
                else:
                    debug("Person is available")
                    schedule[slot] = skipped[i].name
                    last_assigned = skipped[i]
                    del skipped[i]
                    found = True
                    break
            if found:
                continue   # proceed to next slot, if this one could be assigned
            debug("Skipped people exhausted, continue to regular team roster")

        debug("Checking team, starting at index %d" % next_team_member)
        found = False
        for offset in range(len(team)):
            i = (next_team_member + offset) % len(team)
            debug("Check team member %d: %s" % (i, team[i]))
            if slot in team[i].unavailable:
                debug("Person is not available... postponing")
                skipped.append(team[i])
            elif team[i] is last_assigned:
                debug("Person already did time slot before... postponing")
                skipped.append(team[i])
            else:
                debug("Person is available")
                schedule[slot] = team[i].name
                last_assigned = team[i]
                next_team_member = (i + 1) % len(team)
                found = True
                break
        if found:
            continue   # proceed to next slot, if this one could be assigned
        sys.stdout.write("WARNING: No team member available for slot '%s'" % slot)
        
    return schedule


def print_schedule(schedule):
    for k in sorted(schedule.keys()):
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
