import os
import glob


def initialize_folder(folder):    
    files = glob.glob('/users/josh.flori/desktop/'+folder+'/*')
    for f in files:
        if 'template.jpg' not in f and  'music.wav' not in f and 'padding' not in f:
            os.remove(f)

