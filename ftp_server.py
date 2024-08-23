from ftplib import FTP, FTP_TLS, error_perm
from tqdm import tqdm
import logging
import os

class FTPClient:
    def __init__(self, host=os.getenv('FTP_HOST')):
        self.host = host
        self.user = 'anonymous'
        self.password = 'anonymous@example.com'
        logging.debug(f"Using user {self.user} on {self.host}")

        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.user, self.password)
        except error_perm:
            self.ftp = FTP_TLS(self.host)
            self.ftp.login(self.user, self.password)
        except ConnectionRefusedError:
            logging.error(f"Connection refused by {self.host}")
            exit()
        logging.debug(self.ftp.getwelcome())

    def download_file(self, remote_dir, filename, local_dir):
        local_path = os.path.join(local_dir, f"remote_{filename}")
        try:
            logging.debug(f"Starting file download from {remote_dir}/{filename} to {local_path}.")

            # Ensure the local directory exists
            if not os.path.exists(local_dir):
                raise Exception(f"Local directory {local_dir} does not exist.")

            # Change to the remote directory
            try:
                self.ftp.cwd(remote_dir)
            except Exception as e:
                logging.error(f"Failed to change directory to {remote_dir}: {str(e)}")
                return

            # Download the file
            try:
                with open(local_path, 'wb') as local_file:
                    self.ftp.retrbinary(f'RETR {filename}', local_file.write)
                logging.info(f"Successfully downloaded {filename} to {local_path}.")
            except Exception as e:
                logging.error(f"Failed to retrieve file {filename}: {str(e)}")
                if os.path.exists(local_path):
                    os.remove(local_path)  # Clean up partially downloaded file
                return

        except Exception as overall_exception:
            logging.error(f"An unexpected error occurred: {str(overall_exception)}")

    def get_remote_manifest(self, destination):
        self.download_file('/BG3_Mod', 'manifest.json', destination)

    def update_file(self, list_tuple, local_dir):
        logging.info('Downloading new files...')
        self.update_and_download(local_dir, list_tuple[0])
        logging.info('Updating files...')
        self.update_and_download(local_dir, list_tuple[1])

    def update_and_download(self, local_directory, file_list):
        for file_path in tqdm(file_list):
            local_file_path = os.path.join(local_directory, file_path).replace('\\', '/')
            local_dir = os.path.dirname(local_file_path)

            try:
                if not os.path.exists(local_dir):
                    os.makedirs(local_dir)

                with open(local_file_path, 'wb') as local_file:
                    self.ftp.retrbinary(f'RETR {file_path}', local_file.write)
            except FileNotFoundError as fnf_error:
                logging.error(f"FileNotFoundError for {file_path}. Details: {fnf_error}")
            except Exception as e:
                logging.error(f"An error occurred for {file_path}. Details: {e}")

    def close(self):
        self.ftp.quit()
