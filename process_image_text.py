# known problem 1: when meme in paneled boxes, tessearct tries to read top down which doesn't work, it should be top left, top right, bottom left, bottom right. will need to at least set a network up to ignore these kinds of images....
# known problem 2: tessearct has no fucking idea what's happening and 90% of the words are nonsense and characters. solution: tokenize, match each against a known coprus, record the known frequency of tokenized word against corpus, if > threshold, remove image
# known problem 3: "this guy can upvote with his pinky, see? nobody care" ... just didn't even pick up on the second half which was at the bottom of the image.... idk?
# known problem 4: some images need the context of the title, add that in i gues..
# known problem 5: blank text, ignore those
import re
from spellchecker import SpellChecker


# replace these characters: '»' '|'





def process_image_text(text):    
    #for text in text_list:
#
    # remove leading single characters
    def remove_leading_single_characters(text):
        acceptable_first_characters = ['i','a','b','k','u','v']
        if text[1]==" " and text[0].lower() not in acceptable_first_characters:
            text=text[2:]
        return text
    #    
    # 
    def remove_at_character(text):
        # determine starting point, if copied from twitter or something there will usually be an '@'
        if '\n' in text:
            split_text=text.split('\n')
            # assumed @ will never be in this range unless it's a twitter handle or what have you, and assumes @ will always be on the last bad line
            if len(split_text)<4:
                loop=1
            else:
                loop=4
            for i in range(loop):
                if '@' in split_text[i]:
                    text='\n'.join(split_text[i+1:])
        return text
    #      
    #       
    def remove_time_frame(text):
        # assume (timeframe) "ago" indicates from some other post, remove per same logic as above
        if '\n' in text:
            split_text=text.split('\n')
            for i in range(4):
                if 'days ago' in split_text[i] or 'months ago' in split_text[i] or 'hours ago' in split_text[i] or 'day ago' in split_text[i] or 'years ago' in split_text[i]:
                    text='\n'.join(split_text[i+1:])
        return text
    #
    #
    def remove_trailing_newline_and_shit(text):
        # remove trailing \n and random characters...
        if '\n' in text:
            split_text=text.split('\n')
            i=0
            for chunk in reversed(split_text):
                if len(chunk.replace('\n','')) < 3:
                   i+=1
                else:
                    break 
                    text='\n'.join(split_text[0:-i])
        return text
    #
    def throw_out_bad_text_captures(text):
        # if \n is large proportion of entire text, throw it out
    #       print(text)
    #        print(len(text))
        t=text.replace('\n','')
        t=t.replace(' ','')
        if len(t) <20 and len(t)/len(text)<.3:
            text="thrown_out_completely_bad"
        return text
          #  
    #
    def clean_out_huge_leading_garbage(text):
        # same as above, but a little different....
        if '\n' in text:
            split_text=text.split('\n')
            i=0
            for chunk in split_text:
                if len(chunk.replace('\n','')) < 4:
                   i+=1
                else:
                    break 
                    text='\n'.join(split_text[i+1:])
        return text
        #
    def clean_out_bad_middle_chunks(text):
        acceptable_characters = ['i','k','a']
        new=[]
        if '\n\n' in text:
            split_text=text.split('\n\n')
            i=0 
            for chunk in split_text:
                if len(chunk) >2 or chunk in acceptable_characters:
                    new.append(chunk)
        if new !=[]:
            text=' '.join(new)
        return text
        
    def throw_out_completely_bad(text):
        if '\n' not in text and '.' not in text and '?' not in text and '!' not in text:
            text="thrown_out_completely_bad"
        return text
        #
    text=remove_leading_single_characters(text)
    text=remove_at_character(text)
    text=remove_time_frame(text)
    text=remove_trailing_newline_and_shit(text)
    text=throw_out_bad_text_captures(text)
    text=clean_out_huge_leading_garbage(text)
    text=clean_out_bad_middle_chunks(text)
    text=throw_out_completely_bad(text)
    #
    return text


process_image_text(text_list[2])



# debugging the @ removal......
# for text in text_list:
#
#     # determine starting point, if copied from twitter or something there will usually be an '@'
#     split_text=text.split('\n')
#     # assumed @ will never be in this range unless it's a twitter handle or what have you, and assumes @ will always be on the last bad line
#     for i in range(4):
#         if '@' in split_text[i]:
#             print("==============================\n\n",text,"\n\n==============================\n\n")
#             text=''.join(split_text[i+1:])
#             print(text,"\n\n==============================\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")