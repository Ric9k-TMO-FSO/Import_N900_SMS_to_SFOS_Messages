# import_n900sms_to_sfos-0_3.py
Python script to import SMS from the Nokia N900 into SFOS Messages.


Thanks to @pherjung's initial script, knowlage end corrections, here is a python script to import SMS from the legendary Nokia N900 into SFOS Messages.

Works and tested on SFOS 4.4.0.58 on a DUAL XA2, on 4.3.0.15 on a SINGLE XA2.

The following procedure might not be the cleanest one but it worked for me.

Please don't hesitate to share suggestions about the method or on the script.

## Preparation

Make a backup of your SFOS phone messages directory:

```sh
/home/defaultuser/.local/share/commhistory
```


When done, create a dedicated directory on your PC.

On the SFOS device, close the message application and by security, run:

```
devel-su pkill jolla-messages
```
to be sure it is off.

Move
```sh
/home/defaultuser/.local/share/commhistory/commhystory.db
/home/defaultuser/.local/share/commhistory/commhystory.db-wal
/home/defaultuser/.local/share/commhistory/commhystory.db-shm
```
to the directory you just created. (ensure you also have the backup somewhere else!)

Cd to the created directory.

As root or with sudo, change the ownership to your username so you can work on the files:
```
chown your_username:your_username ./commhystory.db*
```
Also copy the messages database 
```
el-v1.db
```
from your N900.
Now, you should have the 3 sfos files, the n900 file and the script in your directory.

Run the script:
```
python ./import_n900sms_to_sfos-0_3.py
```

Now, all your n900's SMS have been imported into the SFOS messages database.

As root or with sudo, re-set the ownership to SFOS username and correct group:
```
chown 100000:996 ./commhystory.db*
```
Copy the db back to your SFOS device. Enjoy your full sms history!

