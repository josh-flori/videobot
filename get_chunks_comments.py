from PIL import Image, ImageDraw, ImageFont
from nltk.tokenize import TweetTokenizer
import numpy as np
import itertools
import wave
from mutagen.mp3 import MP3


"""The purpose of this file is to take each comment paragraph and split
   it into suitably sized chunks of text for creating the frames of the video.
   In other words, chunks of text from each comment will be displayed in the video
   in sequence. The entirety of the comment text does NOT all show up on screen
   at the same time. This helps maintain viewer attention."""

def get_chunks(comment,path_to_audio,audio_padding_length):

    font = ImageFont.truetype('/users/josh.flori/downloads/verdana.ttf' , 12)
    
    # counts the number of characters in that line so far
    count = 0
    # chunked holds total chunked list (a chunk is the new text in a given frame)
    chunked=[]
    # temp holds each letter as the for loop progress, dumped into chunked once character limit or sentence end is reached
    temp=[]
    # contains information about whether that chunk is the end of a sentence, to be passed in when creating the images so that the image thing knows to put the next chunk on the same line rather than the next line
    is_eos=[]
    # when the above is triggered, the image thing needs to know how far to indent the next chunk on the same line, so this will govern that
    indent=[]
    # used for setting movie duration for that frame
    chunk_len=[]
    # loop through each letter
    for i in range(len(comment)):
        # append that letter to temporary holding list
        temp.append(comment[i])
        # increase count of letters
        count+=1
        # true when reached the end of the comment and no other condition was met
        if i == len(comment)-1:
            dump="".join(temp).lstrip()
            chunked.append(dump)
            is_eos.append(False)
            indent.append(0)
            chunk_len.append(len(dump))
        # test if end of line has been reached
        elif count >67:
            # wait until end of current word
            if comment[i]==" ":
                dump="".join(temp).lstrip()
                chunked.append(dump)
                temp=[]
                count=0
                is_eos.append(False)
                indent.append(0)
                chunk_len.append(len(dump))
        # true when sentence has ended before the end of the line
        elif all([any([comment[i] == "." or comment[i] == "!" or comment[i] == "?"]),comment[i+1]==" "]):
            # join letters together into single string
            dump="".join(temp).lstrip()
            # append to chunked
            chunked.append(dump)
            # reset temporary holding list
            temp=[]
            # this will be used to govern the x_adjust parameter in the image thing
            is_eos.append(True)
            # this will be used to govern the x_adjust parameter in the image thing        
            indent.append(font.getsize(dump)[0])
            chunk_len.append(len(dump))
           # get_text_metrics("verdana", 14, ".")
        # true when sentence has ended before the end of the line but when sentence ends with a quote
        elif all([any([comment[i-1]==".",comment[i-1]=="?",comment[i-1]=="!"]),comment[i]=='"' and comment[i+1]==" "]):
            dump="".join(temp).lstrip()
            chunked.append(dump)
            temp=[]
            is_eos.append(True)
            
            indent.append(font.getsize(dump)[0])
            
            chunk_len.append(len(dump))
    
    
    # now you will need to figure out how long the timing should be for each clip.....
    def get_timing(chunked,chunk_len):
        # when creating the video, this will be passed into the set_timing argument of the video maker, or whatever it's called. tells how long it should be.
        timing_temp=[]
        # figure out how long all of the chunks are. each chunk will be divided by this to get the proportion.
        print(np.sum(chunk_len),"<<<<<<")
        total_chunk_length=np.sum(chunk_len)
        for i in range(len(chunked)):
            # as a baseline, figure out how long that chunk_len is out of all chunk lens

            # checks to see whether this chunk contains the end of a sentence or comma. in that case, the audio will slow when reading that chunk which means the timing of that frame should be slowed down from what it otherwise would be
            slow_events=0
            slow_events+=chunked[i].count('! ')
            slow_events+=chunked[i].count('? ')
            slow_events+=chunked[i].count('. ')
            slow_events+=chunked[i].count('." ')
            slow_events+=chunked[i].count(".' ")
            slow_events+=chunked[i].count('?" ')
            slow_events+=chunked[i].count("?' ")
            slow_events+=chunked[i].count('!" ')
            slow_events+=chunked[i].count("!' ")
            slow_events+=chunked[i].count(", ")
            print(slow_events)
            # arbitrarily guess a slow event to be worth 4 characters space....
            timing_temp.append(slow_events*4+chunk_len[i])
        # this gets the proportion that each chunk is out of the total. we will multiply that by the total number of seconds in the audio (excluding the padding at the end) to get the number of seconds each frame should extend for. 
        timing=list(np.divide(timing_temp,np.sum(timing_temp)))


        audio = MP3(path_to_audio)
        audio_duration = audio.info.length-audio_padding_length
        timing=np.multiply(timing,audio_duration)    
        
        return timing
                
    timing=get_timing(chunked,chunk_len)            
                
    
            
    # make sure everything was looped over correctly...
    assert(len(chunked)==len(is_eos)==len(indent)==len(chunk_len)==len(timing))
    
    # get them together for easier processing when creating the frames
    parameters=list(zip(chunked,is_eos,indent,chunk_len,timing))
        
    # we now need to determine how many lines there are. We can't fit more than x lines on an image. Two things must occur. we must check if lines exceed limit, if so, remove comment and don't include it in the video. also return number of lines, which will be used to adjust the y_adjust in the image
    num_lines=int(len(is_eos)-is_eos.count(True))
    
    exceeds_limit=num_lines>13    
    
    
    print(parameters)
    return parameters,num_lines,exceeds_limit    
        




