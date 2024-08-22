import os

def clean_directories(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file == 'desktop.ini':
                os.remove(os.path.join(root, file))

def clean_manifest(directory):
    if 'manifest.json' in os.listdir(directory):
        os.remove(os.path.join(directory, 'manifest.json'))