from moviepy.editor import VideoFileClip, concatenate_videoclips

from pydub import AudioSegment, silence
import numpy as np
import tempfile
import os

def remove_silences_from_video(input_video_path, output_video_path, silence_threshold=-50, silence_duration=1500, padding=500):
    video = VideoFileClip(input_video_path)
    audio = video.audio
    temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    audio.write_audiofile(temp_audio_file.name)
    
    audio_segment = AudioSegment.from_wav(temp_audio_file.name)
    silent_ranges = silence.detect_silence(audio_segment, min_silence_len=silence_duration, silence_thresh=silence_threshold)
    silent_ranges = [(max(0, start-padding), min(len(audio_segment), end+padding)) for start, end in silent_ranges]
    
    sound_ranges = []
    last_end = 0
    for start, end in silent_ranges:
        if last_end < start:
            sound_ranges.append((last_end, start))
        last_end = end
    if last_end < len(audio_segment):
        sound_ranges.append((last_end, len(audio_segment)))
    
    clips = []
    for start, end in sound_ranges:
        start_time = start / 1000.0
        end_time = end / 1000.0
        clips.append(video.subclip(start_time, end_time))
    
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_video_path, codec='libx264', audio_codec='aac', preset='slow', 
                               ffmpeg_params=['-crf', '18'], audio_bitrate='192k')
    
    os.remove(temp_audio_file.name)

def determine_silence_threshold(audio_segment, silence_duration=1500):
    chunk_length = silence_duration // 10  # shorter chunks for analysis
    loudness = [audio_segment[i:i+chunk_length].dBFS for i in range(0, len(audio_segment), chunk_length)]
    
    # Filter out -inf values which represent absolute silence
    loudness = [l for l in loudness if l != float('-inf')]
    
    # Ensure there's data left to process
    if not loudness:
        return -50  # Default to -50 dBFS if no valid loudness data is found

    hist, bin_edges = np.histogram(loudness, bins=100)
    peak_loudness_index = np.argmax(hist)
    silence_threshold = bin_edges[peak_loudness_index] - 5  # Shift threshold for a margin

    return silence_threshold


def extract_audio_from_video(input_video_path):
    from moviepy.editor import VideoFileClip
    
    video = VideoFileClip(input_video_path)
    audio = video.audio
    temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    audio.write_audiofile(temp_audio_file.name)
    
    return temp_audio_file.name

def get_silence_threshold(input_video_path):
    temp_audio_file = extract_audio_from_video(input_video_path)
    
    audio_segment = AudioSegment.from_wav(temp_audio_file)
    
    silence_threshold = determine_silence_threshold(audio_segment)    
    os.remove(temp_audio_file)
    return int(silence_threshold -8) #tweak the level by adding or substracting as per your taste.

if __name__ == '__main__':
  input_file_path = 'Pandas 1.mp4'
  remove_silences_from_video(
      input_video_path=input_file_path,
      output_video_path='output.mp4',
      silence_threshold= get_silence_threshold(input_file_path),
      silence_duration=1500,  # Silence duration threshold in ms
      padding=500  # Padding in ms, helps in creating smoother transitions between audio segments.
  )