# pick.py

A python3 script that presents a TK gui listing servers you may need to periodically ssh into.
This script was initially written in Windows, but I only use linux at home so this code has been updated to support that. Note, you may still need to install tk separately even if you already have python3.

At a previous job I had somewhere in the neighborhood of 45 servers that I needed to ssh into periodically, so remembering which server did what was hard enough, but on top of that we had a corporate system that regenerated new passwords for us daily, then manually copy and paste the daily password into each ssh connection.

There is a little code here to support copying the password to the clipboard from password.txt. It's not a big security issue considering the file would reside on your machine and its contents would become invalidated daily, and saved a ton of time, you select the server you want to connect to and the code would copy the password to your clipboard, then you can paste it into the terminal. The password is then cleared from your clipboard. The code for all of this is in the pick.sh shell script.
