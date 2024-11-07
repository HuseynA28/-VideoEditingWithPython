
from moviepy.editor import *

from moviepy.editor import VideoFileClip
from moviepy.video.fx.all import fadein, fadeout

def cut_long_scenes(video_path, max_duration=1):
    # Load the video
    clip = VideoFileClip(video_path)
    
    # List to hold the subclips
    subclips = []
    
    # Current start of the scene
    start = 0
    
    # Iterate through each frame by frame
    for t in range(1, int(clip.duration) + 1):
        # When the end of the video or a long scene is reached
        if t - start > max_duration:
            # Add the subclip from start to max_duration
            subclips.append(clip.subclip(start, start + max_duration))
            # Set the new start to the end of the last scene
            start = t
    
    # Combine all the subclips
    final_clip = concatenate_videoclips(subclips)
    
    # Output file
    final_clip.write_videofile("output_video.mp4", codec='libx264')

# Path to your video
video_path = 'Pandas 1.mp4'

# Call the function with the path to your video
cut_long_scenes(video_path)
