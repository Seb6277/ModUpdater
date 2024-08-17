# Installation

install requirements using `pip install -r requirements.txt`

simulate ftp by creating ``ftp`` folder and local by creating ``local`` folder

create the ``.env`` file with this information:

````python
FTP_HOST=<ftp hostname>
FTP_USER=<ftp username>
FTP_PASSWD=<ftp password>
LOG_LEVEL=INFO
````

# Usage

Use ``python main.py --generate`` to create a mod manifest

use ``python main.py --update`` to sync via the local and remote manifest

# TODO

- Use file tree instead of a listdir
- Continue FTP integration