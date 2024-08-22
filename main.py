import os
import json
import logging
import hashlib
import argparse
from utils import clean_directories, update_manifest, clean_manifest
from tqdm import tqdm
from dotenv import load_dotenv
from ftp_server import FTPClient

def configure_logging():
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


def get_md5(file):
    with open(file, 'rb') as f:
        data = f.read()
        f.close()
        return hashlib.md5(data).hexdigest()

def write_manifest(manifest, folder):
    manifest_file = os.path.join(folder, "manifest.json")
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=4)

def create_manifest(folder):
    logging.info('Generating manifest...')
    manifest = {}
    for root, dirs, files in os.walk(folder):
        relative_root = os.path.relpath(root, folder)
        if relative_root == ".":
            relative_root = ""
        for file in tqdm(files):
            if file != 'manifest.json':
                manifest[os.path.join(relative_root, file)] = get_md5(os.path.join(root, file))
    write_manifest(manifest, folder)

def check_manifest(folder):
    if not "manifest.json" in os.listdir(folder):
        logging.info('Manifest not found... create it now')
        create_manifest(folder)
    else:
        logging.info('Manifest found... updating it')
        clean_manifest(folder)
        create_manifest(folder)

def check_differences(directory):
    to_update = []
    to_download = []
    to_delete = []
    local_manifest = json.load(open(os.path.join(directory, 'manifest.json'), 'r'))
    remote_manifest = json.load(open(os.path.join(directory, 'remote_manifest.json'), 'r'))
    for file in local_manifest:
        if file not in remote_manifest:
            to_delete.append(file)
    for file in remote_manifest:
        if file not in local_manifest:
            to_download.append(file)
        else:
            if remote_manifest[file] != local_manifest[file]:
                to_update.append(file)
    return to_update, to_download, to_delete

def delete_file(root, file_list):
    for file in file_list:
        os.remove(os.path.join(root, file))

if __name__ == '__main__':
    load_dotenv()
    configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument('--mod_dir', type=str, help="Root mod's directory", required=True)
    parser.add_argument('--generate', type=bool, help='Generate manifest file for mods',
                        nargs='?', const=True)
    parser.add_argument('--update', type=bool, help='Update mods', nargs='?', const=True)
    args = parser.parse_args()
    if args.generate and args.update:
        raise Exception(
            'Cannot generate remote manifest and update at the same time')
    logging.info(f'Logging set to {logging.getLevelName(logging.root.level)}')
    logging.debug('arguments : ' + str(args))
    if args.update:
        ftp_client = FTPClient()
        logging.info('Checking manifest presence...')
        check_manifest(args.mod_dir)
        ftp_client.get_remote_manifest(destination=args.mod_dir)
        differences = check_differences(args.mod_dir)
        logging.info(f'{len(differences[0])} mod update(s) found')
        logging.info(f'{len(differences[1])} new mod(s) found')
        logging.info(f'{len(differences[2])} mod to delete found')
        if len(differences[2]) > 0:
            delete_file('local', differences[2])
        if len(differences[0]) > 0 or len(differences[1]) > 0:
            ftp_client.update_file((differences[0], differences[1]), args.mod_dir)
        update_manifest(args.mod_dir)
        ftp_client.close()
    if args.generate:
        clean_directories(args.mod_dir)
        create_manifest(args.mod_dir)


