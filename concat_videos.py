from moviepy.editor import VideoFileClip, concatenate_videoclips

def concat_videos():
clip1 = VideoFileClip("/users/josh.flori/desktop/demo/slide_title.mp4")
clip2 = VideoFileClip("/users/josh.flori/desktop/demo/first_video.mp4")
final_clip = concatenate_videoclips([clip1,clip2])
final_clip.write_videofile("/users/josh.flori/desktop/demo/concat.mp4")