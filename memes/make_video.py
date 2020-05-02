import os
from moviepy.video.VideoClip import ImageClip
from moviepy.editor import concatenate_videoclips





def get_frame_duration(all_text_with_pauses):
    frame_durations=[]
    for text in all_text_with_pauses:
        if text != 'empty':
            for subtext in text.split('\n')[0:-1]: # [0:-1] avoids empty string split introduces
                frame_durations.append(len(subtext)/22)
        else:
            frame_durations.append(.67)
    return frame_durations


def create_video(durations,meme_output_path):
    image_paths = [meme_output_path + f for f in sorted(os.listdir(meme_output_path))]
    print(len(image_paths))
    print(len(durations))
    clips = [ImageClip(image_paths[i]).set_duration(durations[i]) for i in range(len(image_paths))]
    concat_clip = concatenate_videoclips(clips, method='compose')
    concat_clip.write_videofile('/users/josh.flori/desktop/out.mp4', fps=5)  # , audio=directory + audio_file

