#!/usr/bin/env python3
import argparse
import getpass
import ftplib as FTP
import datetime
import os

parser = argparse.ArgumentParser(description='Download specified folders from the RADAR FTP.' \
                                 'Defaults to looking at folders in "/RADAR-CNS/HDFS_CSV/output/"')
parser.add_argument('-u', '--user', help='The FTP user account',
                    default='cstewart')
parser.add_argument('-ip', '--hostname', help='The FTP hostname',
                    default='159.92.120.21')
foldergroup = parser.add_mutually_exclusive_group(required=True)
foldergroup.add_argument('-f', '--folder',
                         help='A string of the folder to be downloaded',
                         default='')
foldergroup.add_argument('-fs', '--folders',
                         help='A file containing a list of folders to be downloaded',
                         type=argparse.FileType('r'), default='-')
parser.add_argument('-p', '--path',
                    help='The path within which to search. Defaults to ' \
                        '"/RADAR-CNS/HDFS_CSV/output/"',
                    default='/RADAR-CNS/HDFS_CSV/output/')
parser.add_argument('-df', '--dateformat', help='The format of the date supplied in' \
                        'startdate. For use in datetime.strptime(). e.g. "%Y-%m-%d"',
                    default='%Y-%m-%d')
parser.add_argument('-ds', '--startdate', help='Only downloads files past this date',
                    default='2000-01-01')
parser.add_argument('-de', '--enddate', help='Only download files up to this date',
                    default='2200-01-01')

parser.add_argument('--overwrite', help='Flag to overwrite existing files',
                    action='store_true')
parser.add_argument('-o', '--outpath', help='Parent path to save files to',
                    default='.')

def parse_folders(ftp, folder):
    try:
        ftp.cwd(folder)
    except FTP.error_perm:
        print('Can\'t change to folder: ', folder)
        print(ftp.pwd())
        return
    dir_contents = ftp.mlsd()
    child_folders = []
    files = []
    for f in dir_contents:
        if f[1]['type'] == 'dir':
            child_folders.append(f[0])
        elif f[1]['type'] == 'file':
            file_time = datetime.datetime.strptime(f[1]['modify'], '%Y%m%d%H%M%S')
            if args.startdate < file_time and file_time < args.enddate:
                files.append(f[0])
    if files:
        retrieve_files(ftp, files)
        
    for cfolder in child_folders:
        parse_folders(ftp, cfolder)
    ftp.cwd('..')
    

def retrieve_files(ftp, files):
    def retrieve_file(ftp, filename, local_dir):
        local_file = os.path.join(local_dir, filename)
        if os.path.isfile(local_file) and not args.overwrite:
            return
        else:
            with open(local_file, 'wb') as f:
                ftp.retrbinary('RETR ' + filename, f.write)
        
    local_dir = os.path.join(args.outpath, os.path.relpath(ftp.pwd(), args.path))
    os.makedirs(local_dir, exist_ok=True)
    for f in files:
        retrieve_file(ftp, f, local_dir)

# Main
args = parser.parse_args()
if args.folder:
    folders = [args.folder]
else:
    folders = args.folders.read().split()
args.startdate = datetime.datetime.strptime(args.startdate, args.dateformat)
args.enddate = datetime.datetime.strptime(args.enddate, args.dateformat)
password = getpass.getpass()

ftp = FTP.FTP(args.hostname)
try:
    ftp.login(args.user, password)
except FTP.error_perm:
    print('Incorrect login')
    raise SystemExit
    
try:
    ftp.cwd(args.path)
except FTP.error_perm:
    print('Can not change directory to given path: %s', args.path)
    raise SystemExit
    
for folder in folders:
    parse_folders(ftp, folder)