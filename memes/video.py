import os
from moviepy.video.VideoClip import ImageClip
from moviepy.editor import concatenate_videoclips
from pydub import AudioSegment

AudioSegment.ffmpeg = '/users/josh.flori/pycharmprojects/bla/'


def combine_audio(audio_output_path, output_audio_fname, i):
    """ Combine audio for a single meme"""
    combined = AudioSegment.empty()
    for f in sorted(os.listdir(audio_output_path)):
        if f[0:len(str(i)) + 1] == str(i) + '.':
            combined += AudioSegment.from_mp3(audio_output_path + f)
    combined.export(audio_output_path + output_audio_fname, format="mp3")
    audio_length = len(combined)
    return audio_length


def compute_slide_durations(audio_output_path, audio_text, slide_text, img_num, padding_path):
    """ The purpose of this function is to distribute the length of each audio clip across all relevant
        slide_texts which make up that audio but are at a smaller chunked level than the audio clips themselves"""
    n = 0  # to be used to iterate through slide_text to match up against audio_text
    slide_durations = []
    padding_time = len(AudioSegment.from_mp3(padding_path)) / 1000
    # loop through the text that created the audio files
    for i in range(len(audio_text)):
        audio_len = len(AudioSegment.from_mp3(audio_output_path + str(img_num) + '.' + str(i) + '.mp3')) / 1000
        temp_text = ''
        for text in slide_text[n:]:
            # print('Loop: ' + str(i) + 'n: ' + str(n) + '\nSlide_text: ' + text + '\nAudio_text[i]: ' + audio_text[i])
            # you want a way to break out of this loop because the problem is otherwise it will continue on through
            # the end which is bad because then it would increment n based on the presense of 'empty' which may exist
            # later in slide text than you want to go, thus skipping past where you need to be next iteration through
            # slide_text[n:]...
            if i < len(audio_text) - 1 and text != 'empty':
                look_ahead = any([text in audio_text[ii].replace('\n', ' ') for ii in range(i + 1, len(audio_text))])
                if look_ahead:
                    print('hit')
                    break
                # this will be triggered when slide_text is longer than audio_text, like this:
                # audio_text == 'BUT...\n', 'HAVE YOU EVER SEEN ONE OF THESE???\n' and slide text like
                # slide_text == 'BUT... HAVE YOU EVER SEEN ONE OF THESE???'
                if text != 'first_frame' and not look_ahead and text not in audio_text[i].replace('\n', ' '):
                    if audio_text[i].replace('\n', '') in text:
                        temp_text += audio_text[i]
                        audio_len += len(AudioSegment.from_mp3(
                            audio_output_path + str(img_num) + '.' + str(i) + '.mp3')) / 1000
                        # fast-forward through audio_text
                        for a in range(i+1, len(audio_text)):
                            if audio_text[a].replace('\n','') in text:
                                temp_text+=audio_text[a]
                                audio_len += len(AudioSegment.from_mp3(
                                    audio_output_path + str(img_num) + '.' + str(a) + '.mp3')) / 1000
                                i+=1
                            else:
                                break
                            slide_durations.append((len(text) / len(temp_text)) * audio_len)
            if text == 'first_frame':
                slide_durations.append(0)
                n += 1
            elif text == 'empty':
                slide_durations.append(padding_time)
                n += 1
                break
            elif text in audio_text[i].replace('\n', ' '):
                # proportionalize the amount that text is of the entire text
                slide_durations.append((len(text) / len(audio_text[i])) * audio_len)
                n += 1
    return slide_durations


def create_video(slide_durations, meme_output_path, audio_output_path, output_audio_fname, i):
    image_paths = [meme_output_path + f for f in sorted(os.listdir(meme_output_path)) if
                   f[0:len(str(i)) + 1] == str(i) + '.']
    print(image_paths)
    print(slide_durations)
    print(len(image_paths))
    print(len(slide_durations))

    # DEBUGGING
    # print(len(image_paths))
    # print(len(slide_durations))
    clips = [ImageClip(image_paths[i]).set_duration(slide_durations[i]) for i in range(len(image_paths))]
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile('/users/josh.flori/desktop/out' + str(i) + '.mp4',
                                audio=audio_output_path + output_audio_fname, fps=15)
