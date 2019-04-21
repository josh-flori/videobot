"""The purpose of this file is to take each comment paragraph and split
   it into suitably sized chunks of text for creating the frames of the video.
   In other words, chunks of text from each comment will be displayed in the video
   in sequence. The entirety of the comment text does NOT all show up on screen
   at the same time. This helps maintain viewer attention."""

def get_chunks(title_text):
    
    # counts the number of characters in that line so far
    count = 0
    # chunked holds total chunked list (a chunk is the new text in a given frame)
    chunked=[]
    # temp holds each letter as the for loop progress, dumped into chunked once character limit or sentence end is reached
    temp=[]
    # used for setting movie duration for that frame
    chunk_len=[]
    # loop through each letter
    for i in range(len(title_text)):
        # append that letter to temporary holding list
        temp.append(title_text[i])
        # increase count of letters
        count+=1
        # true when reached the end of the comment and no other condition was met
        if i == len(title_text)-1:
            dump="".join(temp).lstrip()
            chunked.append(dump)
            chunk_len.append(len(dump))
        # test if end of line has been reached
        elif count >35:
            # wait until end of current word
            if title_text[i]==" ":
                dump="".join(temp).lstrip()
                chunked.append(dump)
                temp=[]
                count=0
                chunk_len.append(len(dump))
            
    # make sure everything was looped over correctly...
    assert(len(chunked)==len(chunk_len))
    
    # get them together for easier processing when creating the frames
    parameters=list(zip(chunked,chunk_len))
        
    # we now need to determine how many lines there are. We can't fit more than x lines on an image. Two things must occur. we must check if lines exceed limit, if so, remove comment and don't include it in the video. also return number of lines, which will be used to adjust the y_adjust in the image
    num_lines=len(chunked)
    
    return parameters,num_lines
        




