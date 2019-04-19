# Auto-Video Creator

The purpose of this project is to create videos automatically.

# OUTLINE:
1) Initalize script to take reddit url as argument input and return top n comments (we can debate whether to exclude comments under certain threshold length and also whether we should return subcomments. But let's start by not returning subcomments. Clean bad characters etc...)
2) Send text to amazon's api and process returned mp3.
3) Figure out how to create base image template in python.
4) Figure out how to get text to base image.
4.1) Figure out how to create video file with images and audio.
5) Create rules for segmenting text in logical chunks (delimate on character, minimum word count = 7, maximum word count = 15? if no characters are found by then... play around with these parameters)
6) Find timing for lining up text and audio, in other words, what is the average length to pronounce a single character? - ensure audio syncs up correctly
7) .... brain
