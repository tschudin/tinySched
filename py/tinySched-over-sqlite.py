#!/usr/bin/env python3

# tinySched-over-sqlite.py

# explore the functionality of a decentralized conference scheduling
# app by first prototyping it with a relational database

# Oct 1, 2024 <christian.tschudin@unibas.ch>

import sqlite3

DB_NAME = "tinysched-v1.db"

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

def db_erase():
    tables = [ 'attendintents',
               'bookings',
               'conferences',
               'places',
               'registrations',
               'roles',
               'segments',
               'talks',
               'users',
              ]
    for t in tables:
        c = f'DROP TABLE IF EXISTS {t}'
        print('  cmd', c)
        cur.execute(c)
    c = 'DROP VIEW IF EXISTS roster'
    print('  cmd', c)
    cur.execute(c)
    con.commit()

def db_init():
    cmds = [
        '''CREATE TABLE 'users' (    -- public keys aka feed IDs
             [UserID] integer primary key autoincrement not null,
             [DisplayName] text
           )''',
        '''CREATE TABLE 'conferences' ( -- supports many conferences
             [ConfID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [Description] text,
             FOREIGN KEY(IssuerRef) REFERENCES users(userID)
           )''',
        '''CREATE TABLE 'registrations' ( -- interest to attend
             [RegID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [ConfRef] integer,
             [Cancel] Bool
           )''',
        '''CREATE TABLE 'talks' ( -- suggested talk, to be "adopted"
             [TalkID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [ConfRef] integer,
             [Authors] text,      -- freeform text
             [Description] text,  -- freeform text
             FOREIGN KEY(IssuerRef) REFERENCES users(userID),
             FOREIGN KEY(ConfRef) REFERENCES conferences(ConfID)
           )''',
        '''CREATE TABLE 'places' ( -- conf-specific location
             [PlaceID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [ConfRef] integer,
             [Description] text,
             FOREIGN KEY(IssuerRef) REFERENCES users(userID),
             FOREIGN KEY(ConfRef) REFERENCES conferences(ConfID)
           )''',
        '''CREATE TABLE 'segments' ( -- segment = sequence of several talks
             [SegmentID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [ConfRef] integer,
             [PlaceRef] integer,
             [StewardRef] integer,
             [Title] text,
             [Start_dt] text,
             [End_dt] text,
             FOREIGN KEY(IssuerRef) REFERENCES users(userID),
             FOREIGN KEY(ConfRef) REFERENCES conferences(ConfID),
             FOREIGN KEY(PlaceRef) REFERENCES places(PlaceID),
             FOREIGN KEY(StewardRef) REFERENCES users(userID)
           )''',
        '''CREATE TABLE 'bookings' (
             [BookingID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [ConfRef] integer,
             [SegmentRef] integer,
             [TalkRef] integer,
             [Start_dt] text,
             [End_dt] text,
             FOREIGN KEY(IssuerRef) REFERENCES users(userID),
             FOREIGN KEY(ConfRef) REFERENCES conferences(ConfID),
             FOREIGN KEY(SegmentRef) REFERENCES segments(SegmentID),
             FOREIGN KEY(TalkRef) REFERENCES talks(TalkID)
           )''',
        '''CREATE TABLE 'roles' (
             [RoleID] integer primary key autoincrement not null,
             [ConfRef] integer,
             [IssuerRef] integer,
             [TargetRef] integer, -- to whom the role should be assigned
             [Role] char(4) check (Role in ('ATDE','PRES','STEW','CURA',
                                            'NOTA','NOTP','NOTS','NOTC')),
             FOREIGN KEY(ConfRef) REFERENCES conferences(confID),
             FOREIGN KEY(IssuerRef) REFERENCES users(userID),
             FOREIGN KEY(TargetRef) REFERENCES users(userID)
           )''',
        '''CREATE TABLE 'attendintents' (
             [AttendintentID] integer primary key autoincrement not null,
             [IssuerRef] integer,
             [BookingRef] integer,
             [Action] char(1) check (Action in ('Y','N')),
             FOREIGN KEY(IssuerRef) REFERENCES users(userID),
             FOREIGN KEY(BookingRef) REFERENCES bookings(BookingID)
           )''',

        '''CREATE VIEW 'roster' AS SELECT
             conferences.Description,
             segments.Start_dt, segments.End_dt, segments.Title,
             places.Description,
             users.DisplayName AS steward,
             bookings.Start_dt, bookings.End_dt,
             talks.Description, talks.Authors
           FROM
             conferences
           INNER JOIN segments ON Segments.ConfRef= conferences.ConfID
           INNER JOIN places ON Segments.PlaceRef = places.PlaceID
           INNER JOIN users ON Segments.StewardRef = users.UserID
           INNER JOIN bookings ON Bookings.segmentRef = segments.segmentID
           INNER JOIN talks ON Bookings.TalkRef = talks.talkID
           '''
    ]
    for c in cmds:
        print("cmd", c)
        cur.execute(c)
    con.commit()

# utility functions ---------------------------------------------------

def user2ref(nm):
    x = cur.execute(f"SELECT UserID FROM users WHERE DisplayName = '{nm}'"
        ).fetchone()
    if x != None:
        x = x[0]
    return x

def get_roster():
    return cur.execute(f"SELECT * FROM roster").fetchall()

# actions ------------------------------------------------------------

def action_user_add(name):
    cmd = f"INSERT INTO users (DisplayName) " + \
          f"VALUES ('{name}')"
    userID = cur.execute(cmd).lastrowid
    con.commit()
    return userID

def action_conference_add(iam, descr):
    cmd = f"INSERT INTO conferences (IssuerRef,Description) " + \
          f"VALUES ({user2ref(iam)}, '{descr}')"
    confID = cur.execute(cmd).lastrowid
    con.commit()
    return confID

def action_conference_update(iam, conf, newdescr):
    pass

def action_conference_del(iam, conf):
    pass

def action_role_promote(iam, confID, person, role):
    cmd = f"INSERT INTO roles (ConfRef,IssuerRef,TargetRef,Role) " + \
          f"VALUES ({confID}, {user2ref(iam)}, {user2ref(person)}, '{role}')"
    roleID = cur.execute(cmd).lastrowid
    con.commit()
    return roleID

def action_role_demote(iam, conf, person, role):
    pass

def action_register(iam, conf, cancel=False):
    cmd = f"INSERT INTO registrations (ConfRef,IssuerRef,Cancel) " + \
          f"VALUES ({confID}, {user2ref(iam)}, {1 if cancel else 0})"
    regID = cur.execute(cmd).lastrowid
    con.commit()
    return regID

def action_place_add(iam, conf, descr):
    cmd = f"INSERT INTO places (ConfRef,IssuerRef,Description) " + \
          f"VALUES ({confID}, {user2ref(iam)}, '{descr}')"
    placeID = cur.execute(cmd).lastrowid
    con.commit()
    return placeID

    pass

def action_place_update(iam, place, authors, descr):
    pass

def action_place_del(iam, place):
    pass

def action_segment_add(iam, confID, placeID, steward, title, start, end):
    cmd = f"INSERT INTO segments (IssuerRef,ConfRef,PlaceRef," + \
                                f"StewardRef,Title,Start_dt,End_dt) " + \
          f"VALUES ({user2ref(iam)}, {confID}, {placeID}," + \
                  f"{user2ref(steward)}, '{title}', '{start}', '{end}')"
    segmentID = cur.execute(cmd).lastrowid
    con.commit()
    return segmentID

def action_segment_update(iam, segment, steward, title, start, end):
    pass

def action_segment_del(iam, segment):
    pass

def action_talk_add(iam, confID, authors, descr):
    cmd = f"INSERT INTO talks (IssuerRef,ConfRef,Authors,Description)" + \
          f"VALUES ({user2ref(iam)}, {confID}, '{authors}', '{descr}')"
    talkID = cur.execute(cmd).lastrowid
    con.commit()
    return talkID

def action_talk_update(iam, talk, authors, descr):
    pass

def action_booking_add(iam, confID, segmentID, talkID, start, end):
    cmd = f"INSERT INTO bookings (IssuerRef,ConfRef,SegmentRef," + \
                                f"TalkRef,Start_dt,End_dt) " + \
          f"VALUES ({user2ref(iam)}, {confID}, {segmentID}," + \
                  f"{talkID}, {start}, {end})"
    talkID = cur.execute(cmd).lastrowid
    con.commit()
    return talkID

def action_booking_del(iam, booking):
    pass

def action_attend_intent(iam, booking, YN):
    pass

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    print("\n# erase old content")
    db_erase()

    print("\n# create new tables")
    db_init()

    print("\n# list of tables:")
    res = cur.execute("SELECT name FROM sqlite_master"
          ).fetchall()
    for x in sorted([r[0] for r in res if r[0] != 'sqlite_sequence' ]):
        print(" ", x)

    print("\n# adding users")
    for nm in ['Alice', 'Bob', 'Carol', 'Wendy']:
        userID = action_user_add(nm)
        print(" ", userID, nm)

    print("\n# create conference")
    confID = action_conference_add('Wendy', 'dWeb 1234')

    print("\n# promote a curator")
    action_role_promote('Wendy', confID, 'Carol', 'CURA')

    print("\n# promote a steward")
    action_role_promote('Wendy', confID, 'Bob', 'STEW')

    print("\n# Alice registers")
    action_register('Alice', confID, cancel=False)

    print("\n# accept Alice as an attendee (e.g., she paid the fee)")
    action_role_promote('Carol', confID, 'Alice', 'ATDE')

    print("\n# Alice submits a talk")
    talkID1 = action_talk_add('Alice', confID,
                              "Alice and friends", "Encrypted CRDTs")

    print("\n# Carol submits a talk")
    talkID2 = action_talk_add('Carol', confID,
                              "Lewis Carroll", "The Grinning Cat")

    print("\n# define a placeholder talk")
    talkID3 = action_talk_add('Wendy', confID, 'n.a.', 'tba')

    print("\n# define three locations")
    placeID1 = action_place_add('Carol', confID, "Hacker Hall Booth A")
    placeID2 = action_place_add('Carol', confID, "Redwood Cathedral")
    placeID3 = action_place_add('Carol', confID, "Library")
    
    print("\n# define three program segments")
    segmentID1 = action_segment_add('Carol', confID, placeID1,
                                    'Bob', "Tutorials", 10, 12)
    segmentID2 = action_segment_add('Carol', confID, placeID2,
                                    'Alice', "Unconference slot 1", 12, 14)
    segmentID3 = action_segment_add('Carol', confID, placeID3,
                                    'Carol', "Unconference slot 2", 14, 16)

    print("\n# schedule Alice's talk")
    action_booking_add('Carol', confID, segmentID1, talkID1, 10, 10.5)
    print("\n# schedule Carol's talk")
    action_booking_add('Wendy', confID, segmentID1, talkID2, 10.5, 11)

    print("\n# schedule placeholder talks for the unconference")
    action_booking_add('Carol', confID, segmentID2, talkID3, 14, 14.5)
    action_booking_add('Carol', confID, segmentID2, talkID3, 14.5, 15)
    action_booking_add('Carol', confID, segmentID2, talkID3, 15, 15.5)
    action_booking_add('Carol', confID, segmentID2, talkID3, 15.5, 16)
    action_booking_add('Carol', confID, segmentID3, talkID3, 14, 14.5)
    action_booking_add('Carol', confID, segmentID3, talkID3, 14.5, 15)
    action_booking_add('Carol', confID, segmentID3, talkID3, 15, 15.5)
    action_booking_add('Carol', confID, segmentID3, talkID3, 15.5, 16)

    # reports
    print("\n# print full program:")
    conf, seg = '', ''
    for line in get_roster():
        if line[0] != conf:
            conf = line[0]
            print(f"\nCONFERENCE '{conf}'")
        if line[1]+'-'+line[2] != seg:
            seg = line[1]+'-'+line[2]
            print(f"\n  {seg} '{line[3]}' in {line[4]}, steward={line[5]}\n")
        print(f"        {line[6]}-{line[7]} '{line[8]}' by {line[9]}")
    
    '''
    Missing:
    - delet operations
    - access control
    - sorting
    - personal program

    Other possible reports:
    e) inconsistencies (room double bookings, sessions with holes)
    f) "my confererence program"
    g) the dWeb camp's unconference is just another tinySched conference ?
    '''

# eof
