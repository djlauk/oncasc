# On Call Scheduler Readme

*oncasc* is the On Call Scheduler; it tries to schedule on call service
duties in a fair fashion.

To achieve that, *oncasc* utilizes a round-robin scheme, but additionally
it takes team members' absences into account as well.


## Usage example

This is the command you need to run to process the examples provided along with *oncasc*:

    $ python src/oncasc.py -t examples/example_team -s examples/example_times

And this will be your output:

    01: # Week 1 needs no scheduling: Christmas / new year break
    02: Bob
    03: Claire
    04: Alice
    05: Bob
    06: Dave
    07: Alice
    08: Claire
    09: Dave
    10: Alice
    11: Bob
    12: Claire
    13: Dave
    14: Alice
    15: Claire
    16: Dave
    17: Bob
    18: Alice
    19: Bob
    20: # Big maintenance break, 3 weeks of restructuring, hence no on call service
    21: # Big maintenance break, 3 weeks of restructuring, hence no on call service
    22: # Big maintenance break, 3 weeks of restructuring, hence no on call service
    23: Claire
    24: Dave
    25: Alice
    26: Bob
    27: Claire
    28: Dave
    29: Alice
    30: Bob
    31: Claire
    32: Dave
    33: Alice
    34: Bob
    35: Claire
    36: Dave
    37: Alice
    38: Bob
    39: Claire
    40: Dave
    41: Alice
    42: Bob
    43: Claire
    44: Dave
    45: Alice
    46: Bob
    47: Claire
    48: Dave
    49: Alice
    50: Bob
    51: Claire
    52: # Week 52 needs no scheduling: Christmas / new year break
