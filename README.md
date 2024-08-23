````

 __       __                  __  __    __                  __             __                         
|  \     /  \                |  \|  \  |  \                |  \           |  \                        
| $$\   /  $$  ______    ____| $$| $$  | $$  ______    ____| $$  ______  _| $$_     ______    ______  
| $$$\ /  $$$ /      \  /      $$| $$  | $$ /      \  /      $$ |      \|   $$ \   /      \  /      \ 
| $$$$\  $$$$|  $$$$$$\|  $$$$$$$| $$  | $$|  $$$$$$\|  $$$$$$$  \$$$$$$\\$$$$$$  |  $$$$$$\|  $$$$$$\
| $$\$$ $$ $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$| $$  | $$ /      $$ | $$ __ | $$    $$| $$   \$$
| $$ \$$$| $$| $$__/ $$| $$__| $$| $$__/ $$| $$__/ $$| $$__| $$|  $$$$$$$ | $$|  \| $$$$$$$$| $$      
| $$  \$ | $$ \$$    $$ \$$    $$ \$$    $$| $$    $$ \$$    $$ \$$    $$  \$$  $$ \$$     \| $$      
 \$$      \$$  \$$$$$$   \$$$$$$$  \$$$$$$ | $$$$$$$   \$$$$$$$  \$$$$$$$   \$$$$   \$$$$$$$ \$$      
                                           | $$                                                       
                                           | $$                                                       
                                            \$$                                                       

````

<p align="center">
    <img src="./images/img.png" alt="ModUpdater">
</p>

# Installation

install requirements using `pip install -r requirements.txt`

create ``.env`` file with this information:

````python
FTP_HOST=<ftp hostname> #REQUIRED ONLY IN NO_GUI MODE
FTP_USER=<ftp username> #REQUIRED ONLY IN NO_GUI MODE
FTP_PASSWD=<ftp password> #REQUIRED ONLY IN NO_GUI MODE
NO_GUI=0 # SET TO 0 FOR GUI OR 1 FOR COMMAND LINE
LOG_LEVEL=INFO
````

# Usage
ModUpdater use a server side manifest and a local manifest to check REAL differences between files based on MD5 Checksum of the file content.

You have to generate a server side manifest after each server update using the cli.

Next all your client can update easily with GUI enabled by entering server hostname and the local folder to sync.

## Command line mode (manifest generation only)
Command line is on ly available for server side manifest generation
Use ``python main.py --generate --mod_dir <path/to/your/folder>`` to create a mod manifest

## GUI Mode (local sync only)
use ``python main.py`` to launch the gui

# Troubleshoot
## GUI not starting
Check your ``.env`` file if ``NO_GUI`` is present and is set to ``0``

# TODO
This work was done for urgent personal purpose, many overhaul can be made like:

- Add ftp login for non-anonymous enabled ftp server
- Make possible to specify server side path
- Add server side generation from local GUI app

# Contributing
This is not a very complex project so this can be great for python beginner.
Pull request will be read.

