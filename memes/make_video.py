import os
from moviepy.video.VideoClip import ImageClip
from moviepy.editor import concatenate_videoclips
from pydub import AudioSegment
from itertools import chain

AudioSegment.ffmpeg = '/users/josh.flori/pycharmprojects/bla/'


def get_frame_duration(all_text_with_pauses):
    def map_text_to_time(text):
        if text == 'empty':
            return .67
        elif text == 'first_frame':
            return .01
        else:
            return len(text) / 24

    frame_durations = list(chain(*[[map_text_to_time(ii) for ii in i] for i in all_text_with_pauses]))
    return frame_durations


def create_video(durations, meme_output_path):
    image_paths = [meme_output_path + f for f in sorted(os.listdir(meme_output_path))]
    print(len(image_paths))
    print(len(durations))
    clips = [ImageClip(image_paths[i]).set_duration(durations[i]) for i in range(len(image_paths))]
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile('/users/josh.flori/desktop/out.mp4', fps=5)  # , audio=directory + audio_file
