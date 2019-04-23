# known problem 1: when meme in paneled boxes, tessearct tries to read top down which doesn't work, it should be top left, top right, bottom left, bottom right. will need to at least set a network up to ignore these kinds of images....
# known problem 2: tessearct has no fucking idea what's happening and 90% of the words are nonsense and characters. solution: tokenize, match each against a known coprus, record the known frequency of tokenized word against corpus, if > threshold, remove image
# known problem 3: "this guy can upvote with his pinky, see? nobody care" ... just didn't even pick up on the second half which was at the bottom of the image.... idk?
# known problem 4: some images need the context of the title, add that in i gues..
# known problem 5: blank text, ignore those
import re
from spellchecker import SpellChecker

def process_image_text(text_list):
    spell = SpellChecker()
    
    
    
for text in text_list:


text=text_list[6]
# remove leading single characters
acceptable_first_characters = ['i','a','b','k','u','v']
if text[1]==" " and text[0].lower() not in acceptable_first_characters:
    text=text[2:]





# determine starting point, if copied from twitter or something there will usually be an '@'
split_text=text.split('\n')
# assumed @ will never be in this range unless it's a twitter handle or what have you, and assumes @ will always be on the last bad line
for i in range(4):
    if '@' in split_text[i]:
        text=''.join(split_text[i+1:])

# assume (timeframe) "ago" indicates from some other post, remove per same logic as above
split_text=text.split('\n')
for i in range(4):
    if 'days ago' in split_text[i] or 'months ago' in split_text[i] or 'hours ago' in split_text[i] or 'day ago' in split_text[i] or 'years ago' in split_text[i]:
        text=''.join(split_text[i+1:])





# find those words that may be misspelled
# misspelled = spell.unknown(['autismbecause'])
#
# for word in misspelled:
#     # Get the one `most likely` answer
#     print(spell.correction(word))
#     # Get a list of `likely` options
#     print(spell.candidates(word))
#








# debugging the @ removal......
# for text in text_list:
#     # determine starting point, if copied from twitter or something there will usually be an '@'
#     split_text=text.split('\n')
#     # assumed @ will never be in this range unless it's a twitter handle or what have you, and assumes @ will always be on the last bad line
#     for i in range(4):
#         if '@' in split_text[i]:
#             print("==============================\n\n",text,"\n\n==============================\n\n")
#             text=''.join(split_text[i+1:])
#             print(text,"\n\n==============================\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")