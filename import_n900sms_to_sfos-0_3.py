#!/usr/bin/env python3

#Initial script: @pherjung
#Thanks to @pherjung, some add-ons + comments: @Ric9k

import sqlite3
from os.path import exists
import time

# Ensure files have the user ownership.
# commhistory.db must be copied in the current directory with, if they exist, commhistory.db-wal and commhistory.db-shm
# commhistory.db-wal and commhistory.db-shm contain changes not yet applied to the db. commhistory.db must not be modified by this script while wal and shm files exist somewhere else.
# All this may be unacurate. For more info/security, RTFM more than I did :--)

file_exists = exists('./commhistory.db-wal')

if not file_exists:
    print ('Be sure you also copied the -wal and -shm files if they were present along commhistory.db in your phone.')
    print ('Read the note inside this script ')
    print ('press CTRL-C within 10 seconds to abort')
    time.sleep(10)

# List remote identities
connectionMaemo = sqlite3.connect('./el-v1.db')
cursor = connectionMaemo.cursor()
cursor.execute('SELECT DISTINCT remote_uid FROM Events')
remote_uid = cursor.fetchall()

# Get messages
# service_id = 3 are SMS only
INFORMATION_SQL = ("""SELECT start_time,
    end_time,
    outgoing,
    bytes_received,
    local_uid,
    remote_Uid,
    free_text
FROM Events WHERE service_id = 3 """)

cursor.execute(INFORMATION_SQL)
datas = cursor.fetchall()

connectionMaemo.close()

connectionSailfish = sqlite3.connect('./commhistory.db')
cursorSailfish = connectionSailfish.cursor()

SQL_INSERT = """INSERT INTO Groups (localUid,
                                    type,
                                    lastModified,
                                    remoteUids)
VALUES('/org/freedesktop/Telepathy/Account/ring/tel/ril_0',
       0,
       0,
       ?
)"""

cursorSailfish.execute('SELECT id, remoteUids FROM Groups')
phones_before = cursorSailfish.fetchall()
print('All phones before update:', phones_before)

#Insert phone_number into table 'Groups'
for uid in remote_uid:
    #TODO?: find a trick to have the same group for same numbers with different beginning (+3361234... vs 003361234... vs 061234...)
    # But this will shift with numbers stored in contacts if they were imported from the N900 too.
    # HINT : save all data in a dictionary. Key is an ID and item phone number.
    # Keep last 9 numbers and compare and remove all similar with [9:]
    
    # Search wether the remote phone number exists into SFOS Db
    cursorSailfish.execute('SELECT remoteUids FROM Groups WHERE remoteUids = ?', [uid[0]])
    phone_found = cursorSailfish.fetchall()
    # Automatically false if list is empty
    if not phone_found:
        print("Add new number")
        cursorSailfish.execute(SQL_INSERT, [uid[0]])
        connectionSailfish.commit()

cursorSailfish.execute('SELECT id, remoteUids FROM Groups')
phones_after = cursorSailfish.fetchall()
print('All phones before update:', phones_after)


# Get the group ID
REMOTE_SQL = "SELECT id FROM Groups WHERE remoteUids=?"

# Insert datas
INSERT_MSG = """INSERT INTO EVENTS(type,
                                   startTime,
                                   endTime,
                                   direction,
                                   isDraft,
                                   isRead,
                                   isMissedCall,
                                   isEmergencyCall,
                                   status,
                                   bytesReceived,
                                   localUid,
                                   remoteUid,
                                   freeText,
                                   groupId,
                                   reportDelivery,
                                   validityPeriod,
                                   readStatus,
                                   reportRead,
                                   reportedReadRequested,
                                   isAction,
                                   hasExtraProperties,
                                   hasMessageParts)
VALUES (2, ?, ?, ?, 0, 1, 0, 0, ?, ?, '/org/freedesktop/Telepathy/Account/ring/tel/ril_0', ?, ?, ?, 0, 0, 0, 0, 0, 0, 1, 0)"""

for data in datas:
    # Import event if text field is not empty
    if data[6] != "":
        
        #Get the correspondant's group number from it its phone number
        cursorSailfish.execute(REMOTE_SQL, [data[5]]) 
        remoteID = cursorSailfish.fetchall()
        #Remove unwanted chars
        corr_group_id = int(remoteID[0][0])
        print corr_group_id
        
        #Convert SMS direction (in/out) from n900 notation to SFOS notation
        #match data[2]:
            #case 1:
                ##SFOS out is 2
                #direction = 2
                #in_out_status = 2
            #case 0:
                ##SFOS in is 1
                #direction = 1
                #in_out_status = 0

        if data[2] == 1:
            #SFOS out is 2
            direction = 2
            in_out_status = 2
        #outgoing = 0
        elif data[2] == 0:
            #SFOS in is 1
            direction = 1
            in_out_status = 0
        
            
        #Events seem to be sorted following endtime
        #If Endtime is empty, we fill it with start time + 3
        if data[1] == 0 or data[1] == "":
            end_time_new = data[0] + 3
            
            

        cursorSailfish.execute(INSERT_MSG, [data[0], #start_time
                                            end_time_new, #end_time
                                            direction, #outgoing
                                            in_out_status, #Again in/out (?)
                                            data[3], #bytes_received
                                            data[5], #remote_Uid
                                            data[6], #free_text
                                            corr_group_id])
        connectionSailfish.commit()


connectionSailfish.close()
print "Don't forget to chown the file ! (chown 100000:996 ./commhistory.db )"
 
