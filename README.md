# tinySched

A playground for a decentralized conference scheduling application,
hopefully running over frugal tinySSB

## Exploration 1 with sqlite

See py/tinySSB-over-sqlite.py for exploring the required sched functionality
using a traditional relational database. It has 9 tables (!) and
one view, for the time being ...

The output:

```

% ./tinySched-over-sqlite.py

...

# list of tables:
  attendintents
  bookings
  conferences
  places
  registrations
  roles
  segments
  talks
  users

# adding users
  1 Alice
  2 Bob
  3 Carol
  4 Wendy

# create conference

# promote a curator

# promote a steward

# Alice registers

# accept Alice as an attendee (e.g., she paid the fee)

# Alice submits a talk

# Carol submits a talk

# define a placeholder talk

# define three locations

# define three program segments

# schedule Alice's talk

# schedule Carol's talk

# schedule placeholder talks for the unconference

# print full program:

CONFERENCE 'dWeb 1234'

  10-12 'Tutorials' in Hacker Hall Booth A, steward=Bob

        10-10.5 'Encrypted CRDTs' by Alice and friends
        10.5-11 'The Grinning Cat' by Lewis Carroll

  12-14 'Unconference slot 1' in Redwood Cathedral, steward=Alice

        14-14.5 'tba' by n.a.
        14.5-15 'tba' by n.a.
        15-15.5 'tba' by n.a.
        15.5-16 'tba' by n.a.

  14-16 'Unconference slot 2' in Library, steward=Carol

        14-14.5 'tba' by n.a.
        14.5-15 'tba' by n.a.
        15-15.5 'tba' by n.a.
        15.5-16 'tba' by n.a.
```

---
