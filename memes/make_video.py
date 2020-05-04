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


def GET_FRAME_DURATION_FOR_REAL_THIS_TIME(audio_output_path, audio_text, frame_text, img_num, padding_path):
    """ The purpose of this function is to distribute the length of each audio clip across all relevant
        frame_texts which make up that audio but are at a smaller chunked level than the audio clips themselves"""
    n = 0  # to be used to iterate through frame_text to match up against audio_text
    frame_durations = []
    padding_time = len(AudioSegment.from_mp3(padding_path)) / 1000
    # loop through the text that created the audio files
    for i in range(len(audio_text)):
        audio_len = len(AudioSegment.from_mp3(audio_output_path + str(img_num) + '.' + str(i) + '.mp3'))/1000
        for text in frame_text[n:]:
            if text == 'first_frame':
                frame_durations.append(0)
                n += 1
            elif text == 'empty':
                frame_durations.append(padding_time)
                n += 1
                break
            elif text in audio_text[i].replace('\n',' '):
                # proportionalize the amount that text is of the entire text
                frame_durations.append((len(text)/len(audio_text[i]))*audio_len)
                n += 1
    return frame_durations


def create_video(frame_durations, meme_output_path, audio_output_path, output_audio_fname, i):
    image_paths = [meme_output_path + f for f in sorted(os.listdir(meme_output_path)) if
                   f[0:len(str(i)) + 1] == str(i) + '.']
    # DEBUGGING
    # print(len(image_paths))
    # print(len(frame_durations))
    clips = [ImageClip(image_paths[i]).set_duration(frame_durations[i]) for i in range(len(image_paths))]
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile('/users/josh.flori/desktop/out' + str(i) + '.mp4',
                                audio=audio_output_path + output_audio_fname, fps=15)

