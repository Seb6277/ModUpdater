from ftplib import FTP, FTP_TLS, error_perm
import logging
import os

class FTPClient:
    def __init__(self):
        self.host = os.getenv('FTP_HOST')
        self.user = os.getenv('FTP_USER')
        self.password = os.getenv('FTP_PASSWD')
        logging.debug(f"Using user {self.user} on {self.host}")

        try:
            self.ftp = FTP(self.host)
            self.ftp.login(self.user, self.password)
        except error_perm:
            self.ftp = FTP_TLS(self.host)
            self.ftp.login(self.user, self.password)
        logging.debug(self.ftp.getwelcome())

    def copy_file(self, source, destination, filename):
        try:
            logging.info(f"Starting file copy from {source} to {destination}.")
            self.ftp.cwd(source)
            with open(f'temp_{filename}', 'wb') as f:
                self.ftp.retrbinary(f'RETR {filename}', f.write)
            self.ftp.cwd(destination)
            with open(f'temp_{filename}', 'rb') as f:
                self.ftp.storbinary(f'STOR {filename}', f)
        except Exception as e:
            logging.error(f"An error occurred: {str(e)}")
        finally:
            os.remove(f'temp_{filename}')
    
    def close(self):
        self.ftp.quit()
