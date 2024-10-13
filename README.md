# tinySched

A playground for a decentralized conference scheduling application,
hopefully running over frugal tinySSB.

In a first step we model the Conference Scheduling application using a
traditional and central relational data model. This permits to
understand the required functionality in an early stage, before
attempting to map the requirements to tinySSB's append-only logs.

## Exploration 2 with sqlite: overall data volume

The current DB model has the following stats:
- 10 tables
- 46 fields

We accumulated fake names, emails, talk titles and abstract, session
titles etc.  With these data (in the ```./data``` directory) we
populate the sqlite using some volume assumptions:

- 600 registration requests (name, email, bio)
- 450 accepted attendees
- 320 talk proposals (title and abstract)
- 2 days with 4 blocks having 8 parallel sessions each having 4 talks -> 256 accepted talks
- 0.75 day for unconference (3 blocks having 4 parallel sessions each having 4 talks -> 48 unconference discussions)


The script ```init_db_from_rnd_data.py``` dumps a fake conference program,
as e.g. in
```
CONFERENCE 'dWeb 1234'

  DAY 1

    08-10 Block 1

      Session on 'Electric Lemonade v2' in Cricket Field, steward=Bob

        08:00-08:30 'Which Disney princess do you find to be the most attractive?' by Morgan Watkins
        08:30-09:00 'Why the NASA shuttle program was stopped' by Kason Ochoa
        09:00-09:30 'Conspiracy theories' by Liberty Pittman
        09:30-10:00 'How I Became a Personal Care Aide' by Caitlin Clarke

      Session on 'Mimosa v2' in Bakery, steward=Bob

        08:00-08:30 'How I Became a Paramedic' by Demarcus Sexton
        08:30-09:00 'How the CIA can track terrorists' by Christina Marquez
        09:00-09:30 'Do you like music? if so what kind?' by Rashad Chapman
        09:30-10:00 'What are your major goals in life?' by Stephanie Holland
...
```

The total volume of the sqlite database is slightly below 400KB.

Adding 25% editing churn to the data, this becomes 0.5MB.

Taking into account the encoding overhead of tinySSB (signatures), we
double this to 1MB.

Adding 450*30 personal talk selections (personalized schedule), each
needing 240B: this is another 3MB.

Adding an engineering safety margin of 30% to the 4MB and 15'000 records
we get an **overall data volume of 6MB for 20'000 records,
carried in 52'500 tinySSB packets (120B).**


## Exploration 1 with sqlite

Note: This section is about an outdated trace of the Python script at

https://github.com/tschudin/tinySched/blob/3377740f94ccf269ffbaf99eeab2d17aa62cbf02/py/tinySched-over-sqlite.py

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
