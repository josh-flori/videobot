import os
import glob


def initialize_folder():    
    files = glob.glob('/users/josh.flori/desktop/demo/*')
    for f in files:
        if 'template.jpg' not in f and  'music.wav' not in f:
            os.remove(f)

