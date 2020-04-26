import os
import glob
from distutils.dir_util import copy_tree




def initialize_folder(folder,which):    
    
    if which=='first':
    
        if not os.path.exists(folder):
            copy_tree('/users/josh.flori/desktop/init', folder)
    
        files = glob.glob(folder+'/*')
    
        for f in files:
            if 'template.jpg' not in f and  'music.wav' not in f and 'padding' not in f:
                os.remove(f)
    
    else:
        files = glob.glob(folder+'/*')
        for f in files:
            if 'finished.mp4' not in f:
                os.remove(f)
