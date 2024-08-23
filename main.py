import os
import json
import logging
import hashlib
import argparse
from utils import clean_directories, clean_manifest
from ftp_server import FTPClient

def configure_logging(log_level='INFO'):
    numeric_level = getattr(logging, log_level, logging.INFO)
    logging.basicConfig(level=numeric_level, format='%(asctime)s - %(levelname)s - %(message)s')


def get_md5(file):
    with open(file, 'rb') as f:
        data = f.read()
        f.close()
        return hashlib.md5(data).hexdigest()

def write_manifest(manifest, folder):
    manifest_file = os.path.join(folder, "manifest.json").replace('\\', '/')
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=4)

def create_manifest(folder):
    logging.info('Generating manifest...')
    manifest = {}
    max_length = 0
    for root, dirs, files in os.walk(folder):
        relative_root = os.path.relpath(root, folder)
        if relative_root == ".":
            relative_root = ""
        for file in files:
            if file != 'manifest.json' and file != 'remote_manifest.json':
                message = f"Generating sum for {os.path.join(relative_root, file).replace('\\', '/')}"
                max_length = max(max_length, len(message))
                print(f"\r{' ' * max_length}\r{message}", end="", flush=True)
                manifest[os.path.join(relative_root, file).replace('\\', '/')] = get_md5(os.path.join(root, file))
    write_manifest(manifest, folder)

def check_manifest(folder, force=False):
    if not "manifest.json" in os.listdir(folder):
        logging.info('Manifest not found... create it now')
        create_manifest(folder)
    else:
        if force:
            logging.info('Manifest found... updating it')
            clean_manifest(folder)
            create_manifest(folder)
        else:
            logging.info('Manifest found... updating it')

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

def validate(directory):
    diff = check_differences(directory)
    if len(diff[0]) > 0 or len(diff[1]) > 0 or len(diff[2]) > 0:
        logging.info(f'Differences found: {diff}')
    else:
        logging.info('No differences found')
        os.remove(os.path.join(directory, 'remote_manifest.json'))


def process(args):
    if args.generate and args.update:
        raise Exception(
            'Cannot generate remote manifest and update at the same time')
    logging.info(f'Logging set to {logging.getLevelName(logging.root.level)}')
    logging.debug('arguments : ' + str(args))
    if args.update:
        ftp_client = FTPClient(args.hostname, args.username, args.password, args.enable_TLS)
        logging.info('Checking manifest presence...')
        check_manifest(args.mod_dir, force=args.force)
        ftp_client.get_remote_manifest(destination=args.mod_dir)
        differences = check_differences(args.mod_dir)
        logging.info(f'{len(differences[0])} file update(s) found')
        logging.info(f'{len(differences[1])} new file(s) found')
        logging.info(f'{len(differences[2])} file(s) to delete found')
        if len(differences[2]) > 0:
            delete_file(args.mod_dir, differences[2])
        if len(differences[0]) > 0 or len(differences[1]) > 0:
            ftp_client.update_file((differences[0], differences[1]), args.mod_dir)
        create_manifest(args.mod_dir)
        validate(args.mod_dir)
        ftp_client.close()
    if args.generate:
        clean_directories(args.mod_dir)
        create_manifest(args.mod_dir)

def main():
    if os.environ.get('NO_GUI') == '0':
        from gooey import Gooey, GooeyParser
        from menu import menu
        @Gooey(
            program_name='Mod Updater',
            menu=menu,
            default_size=(800, 600),
            show_success_modal=True,
            show_restart_button=False,
            description='Update files from FTP server'
        )
        def run_with_gui():
            g_parser = GooeyParser()
            add_arguments(g_parser)
            add_gui_arguments(g_parser)
            g_args = g_parser.parse_args()
            g_args.update = True
            g_args.generate = False
            configure_logging(g_args.log_level)
            process(g_args)
        run_with_gui()
    else:
        parser = argparse.ArgumentParser()
        add_arguments(parser)
        parser.add_argument('--mod_dir', type=str, help="Root mod's directory", required=True)
        parser.add_argument('--generate', help='Generate manifest file for mods', const=True, action='store_const')
        parser.add_argument('--update', help='Update mods', const=True, action='store_const')
        parser.add_argument('--log_level', help='Set level of logs', type=str, default='INFO',
                            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
        parser.add_argument(
            '--password',
            help='FTP server user password',
            type=str, default='anonymous@exemple.com')
        args = parser.parse_args()
        configure_logging(args.log_level)
        process(args)

def add_gui_arguments(parser):
    parser.add_argument('--mod_dir', type=str, help="Root files directory", required=True, widget='DirChooser')
    parser.add_argument('--log_level', help='Set level of logs', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], widget='Dropdown')
    parser.add_argument(
        '--password',
        help='FTP server user password',
        type=str, default='anonymous@exemple.com', widget='PasswordField')


def add_arguments(parser):
    parser.add_argument('--force', help='Force regenerate local manifest and update', const=True,
                        default=False, action='store_const')
    parser.add_argument(
        '--hostname',
        help='FTP server hostname',
        type=str, default=os.environ.get('FTP_HOSTNAME', 'localhost'))
    parser.add_argument(
        '--username',
        help='FTP server username',
        type=str, default='anonymous')
    parser.add_argument('--enable_TLS', help='Enable TLS if required', const=True,
                        default=False, action='store_const')

if __name__ == '__main__':
    if not 'NO_GUI' in os.environ:
        os.environ['NO_GUI'] = '0'
    main()


