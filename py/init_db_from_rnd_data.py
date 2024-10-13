#!/usr/bin/env python3

# init_db_from_rnd_data.py

# import the random data items for populating a tinySched database

# Oct 1 to Oct 13, 2024 <christian.tschudin@unibas.ch>

import random
import sqlite3
import sys

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
             [DisplayName] text,
             [Email] text,
             [Bio] text
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
             [Authors] text,   -- freeform text
             [Title] text,     -- freeform text
             [Abstract] text,  -- freeform text
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
             [Day] integer,
             [Start_dt] text,
             [End_dt] text,
             [PlaceRef] integer,
             [StewardRef] integer,
             [Title] text,
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
             conferences.Description, segments.Day,
             segments.Start_dt, segments.End_dt, segments.Title,
             places.Description,
             users.DisplayName AS steward,
             bookings.Start_dt, bookings.End_dt,
             talks.Title, talks.Authors
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

def get_users():
    return cur.execute(f"SELECT * FROM users").fetchall()

def tim(t):
    t = float(t)
    return '%02d:%02d' % (int(t), 0 if t == int(t) else 30)

# actions ------------------------------------------------------------

def action_user_add(name, email, bio):
    cmd = f"INSERT INTO users (DisplayName,Email,Bio) " + \
          f"VALUES ('{name}','{email}','{bio}')"
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

def action_segment_add(iam, confID, placeID, steward, title, day, start, end):
    cmd = f"INSERT INTO segments (IssuerRef,ConfRef,PlaceRef," + \
                                f"StewardRef,Title,Day,Start_dt,End_dt) " + \
          f"VALUES ({user2ref(iam)}, {confID}, {placeID}," + \
                  f"{user2ref(steward)},'{title}','{day}','{start}','{end}')"
    segmentID = cur.execute(cmd).lastrowid
    con.commit()
    return segmentID

def action_segment_update(iam, segment, steward, title, day, start, end):
    pass

def action_segment_del(iam, segment):
    pass

def action_talk_add(iam, confID, authors, title, abstract):
    cmd = f"INSERT INTO talks (IssuerRef,ConfRef,Authors,Title,Abstract)" + \
          f"VALUES ({user2ref(iam)}, {confID}, '{authors}', '{title}', '{abstract}')"
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

    def load_file(fn):
        lst = []
        with open('../data/' + fn, 'r') as f:
            while True:
                line = f.readline()
                if line == None or len(line) == 0:
                    break
                line = line.strip()
                if line[0] == '#':
                    continue
                lst.append(line)
        return lst

    for i in ['abstract','bio','email','name','place','session','title']:
        cmd = f"{i}s = load_file('rnd_{i}.txt')"
        exec(cmd)
    titles = random.sample(titles,len(titles))
    sessions = random.sample(sessions,len(sessions))
    
    # --- preparing the conference:

    action_user_add('Wendy', 'wendy@archive.org', 'DWeb Executive Producer')
    action_user_add('Bob',   'bob@archive.org',   'DWeb Assistant')
    action_user_add('Carol', 'carol@archive.org', 'DWeb Assistant')
    
    print("\n# create conference")
    confID = action_conference_add('Wendy', 'dWeb 1234')

    print("\n# promote a curator")
    action_role_promote('Wendy', confID, 'Carol', 'CURA')

    print("\n# promote a steward")
    action_role_promote('Wendy', confID, 'Bob', 'STEW')

    print("\n# define locations")
    place_ids = []
    for i in range(len(places)):
        try:
            place_ids.append( action_place_add('Carol', confID, places[i]) )
        except:
            pass

    # --- running the conference:

    print(f"\n# adding and registering {len(names)} users")
    for i in range(len(names)):
        try:
            action_user_add(names[i], emails[i], bios[i])
            action_register(names[i], confID, cancel=False)
        except:
            pass

    u = get_users()
    print('#', len(u), "users")

    print("\n# accept 450 users (e.g., they paid the fee)")
    for i in range(450):
        ref = user2ref(names[i])
        # print(i, names[i], ref)
        if ref == None:
            continue
        action_role_promote('Carol', confID, names[i], 'ATDE')

    print("\n# first 100 users submit a talk")
    talk_ids = []
    for i in range(len(titles)):
        try:
            talk_ids.append( action_talk_add(names[i], confID, names[i],
                                     titles[i], abstracts[i]) )
        except:
            pass

    print("\n# define a placeholder talk")
    talkHolder = action_talk_add('Wendy', confID, 'n.n.', 'tbd', 'unconf talk')

    print("\n# define two days with 4 blocks, 8 parallel sessions, 4 talks each")
    start_times = [8,10,14,16]
    seg_ids = []
    for day in range(2):
        where = random.sample(place_ids, 8)
        for i in range(len(start_times)):
            seg_titles = sessions[:8]
            sessions = sessions[8:]
            for j in range(8):
                sid = action_segment_add('Carol', confID, where[j],
                                 'Bob', seg_titles[j], day,
                                 start_times[i], start_times[i]+2)
                seg_ids.append( (sid,start_times[i]) )
                

    print("\n# accept 4 talks per segment")
    for i, sid in enumerate(seg_ids):
        start_t = sid[1]
        for k in range(4):
            action_booking_add('Carol', confID, sid[0], talk_ids[4*i+k],
                               start_t, start_t + 0.5)
            start_t += 0.5


    print("\n# create place holders for the day3 unconference")
    print("# (3 blocks with 4 parallel sessions with 4 discussions)")
    day = 2
    start_times = start_times[1:]
    for i in range(3):
        for j in range(4):
            where = random.sample(place_ids, 4)
            sid = action_segment_add('Carol', confID, where[j],
                                     'Bob', f"Unconference Discussion {i+1}.{j+1}", day,
                                 start_times[i], start_times[i]+2)
            start_t = start_times[i]
            for k in range(4):
                action_booking_add('Carol', confID, sid, talkHolder,
                               start_t, start_t + 0.5)
                start_t += 0.5


    # --- reports

    print("\n# print full program:")

    # for i,line in enumerate(get_roster()):
    #     print(i,line)

    day, conf, stt, seg = '', '', '', ''
    for d in range(3):
        k = 1
        for line in get_roster():
            if line[0] != conf:
                conf = line[0]
                print(f"\nCONFERENCE '{conf}'")
            if int(line[1]) != d:
                continue
            if day != line[1]:
                day = line[1]
                print("\n  DAY", day+1)
            if line[4] != seg:
                seg = line[4]
                x = f"{'%02d' % int(line[2])}-{line[3]}"
                if stt != x:
                    stt = x
                    print(f"\n    {stt} Block {k}")
                    k += 1
                print(f"\n      Session on '{seg}' in {line[5]}, steward={line[6]}\n")
            print(f"        {tim(line[7])}-{tim(line[8])} '{line[9]}' by {line[10]}")
    
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
