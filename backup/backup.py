import os
import configparser
import glob, shutil
import datetime
import pysftp

config = configparser.ConfigParser()
config.read('backup.ini')

#Get server configuration for SFTP
server = str(config['credentials']['sftp-server'])
user = str(config['credentials']['user'])
passwrd = str(config['credentials']['password'])
temp_dir = str(config['credentials']['temp_backup_dir'])
date = datetime.datetime.now().strftime('%Y-%m-%d')

#create the temp directory, and the directory for the backup if they don't exist 
if not os.path.exists(temp_dir):
    os.mkdir(temp_dir)

if not os.path.exists(temp_dir+'/'+date):
    os.mkdir(temp_dir+'/'+date)

# ==================================== TO DO =================================

### Copy over the restore.py script that gets run  
### when the user downloads the entire package from 
### the file server 

# ==================================== TO DO =================================

# Here i'm creating an object for a new config file to be written. THis config file 
# will go into the date directory and is used by the restore.py script to place the files in the proper dircetoy 
# based on the original location of the file. 
restore_config = configparser.ConfigParser()
restorefile = open(temp_dir+'/'+date+'/restore.ini', 'w')
restore_config.read(temp_dir+'/'+date+'/restore.ini')
restore_config.add_section('restore')


# This section is a little confusing, but it basically just looks for if the directory exists, if it doenst it generates it
# then copies the entire tree structure for each backup directory listed in the backup.ini file. 
for directory in config['backup_dirs']:
    if not os.path.exists(temp_dir+'/'+date+'/'+directory):
        shutil.copytree(config['backup_dirs'][directory], temp_dir+'/'+date+'/'+directory)
        restore_config.set('restore', '/'+directory, config['backup_dirs'][directory])
restore_config.write(restorefile)
restorefile.close()

#Zip 'er up 
shutil.make_archive(temp_dir+'/'+date, 'zip', temp_dir+'/'+date)

#send to the sftp server which is also the same directory as the Apache file server. 
cnopts = pysftp.CnOpts()
cnopts.hostkeys=None
with pysftp.Connection(host=server, username=user, password=passwrd, cnopts=cnopts) as sftp:

    sftp.put(temp_dir+'/'+date+'.zip', 'backups/'+date+'.zip')
    sftp.close()
