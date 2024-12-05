import os
import json
from paramiko.sftp_client import SFTPClient
from fabric import Connection
from fabric.transfer import Transfer

from watch import watch_folder, ChangeType

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    raise Exception("Could not find config file: " + CONFIG_FILE)

with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
    config = json.load(f)

props_to_check = [
    'ip',
    'user',
    'port',
    'private_key',
    'local_folder',
    'remote_folder'
]

for prop in props_to_check:
    if not prop in config:
        raise Exception(f'Could not find property {prop} in config.json')
    if config[prop] == "":
        raise Exception(f'Property {prop} in {CONFIG_FILE} was empty')

ip = config['ip']
user = config['user']
port = config['port']
key_file = config['private_key']
local_folder = config['local_folder']
remote_folder = config['remote_folder']

con = Connection(ip, user, port, connect_kwargs = {
    "key_filename": key_file
})

tran = Transfer(con)
sftp: SFTPClient = tran.sftp

if not tran.is_remote_dir(remote_folder):
    raise Exception(f'Remote folder {remote_folder} does not exist')

if not os.path.exists(local_folder):
    raise Exception(f'Local folder {local_folder} does not exist')

def ensure_folder(path: str, part_idx: int = 0):
    parts = path.split('/')
    rel_path = '/'.join(parts[part_idx:])
    remote_dir = remote_folder + rel_path
    local_dir = local_folder + rel_path
    if part_idx >= len(parts):
        return
    
    if not os.path.exists(local_dir):
        raise Exception(f'Could not find local folder {local_dir}')
    
    if not os.path.isdir(local_dir):
        return

    if not tran.is_remote_dir(remote_dir):
        sftp.mkdir(remote_dir)
    
    ensure_folder(path, part_idx + 1)


def transfer_folder(folder: str):
    lf = local_folder + '/' + folder
    rf = remote_folder + '/' + folder
    remote_files = sftp.listdir(rf)
    for file in os.listdir(lf):
        local_file = lf + '/' + file
        remote_file = rf + '/' + file
        if os.path.isfile(local_file) and not file in remote_files:
            print(f'Transferring {remote_file}')
            tran.put(local_file, remote_file)

        if os.path.isfile(local_file) and file in remote_files:
            local_mod_time = os.path.getmtime(local_file)
            remote_mod_time = sftp.stat(remote_file).st_mtime
            if local_mod_time > remote_mod_time:
                print(f'Updating {remote_file}')
                tran.put(local_file, remote_file)

        if os.path.isdir(local_file) and not tran.is_remote_dir(remote_file):
            sftp.mkdir(rf)
            transfer_folder(folder + '/' + file)

def change_cb(path: str, ct: ChangeType):
    rel_path = path.replace(local_folder, "")
    local_path = local_folder + rel_path
    remote_path = remote_folder + rel_path.replace('\\', '/')
    print(f'{ct.value}: {rel_path}')
    match ct:
        case ChangeType.ADD:
            ensure_folder(rel_path)
            tran.put(local_path, remote_path)
        case ChangeType.DELETE:
            sftp.remove(remote_path)
        case ChangeType.MODIFY:
            tran.put(local_path, remote_path)
        case ChangeType.MOVE:
            sftp.remove(remote_path)
            tran.put(local_path, remote_path)

transfer_folder('')

watch_folder(local_folder, change_cb)