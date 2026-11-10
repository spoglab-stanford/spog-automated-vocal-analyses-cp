import re
import sys
import os
from pydub import AudioSegment
import random
import pandas as pd
import datetime
from lxml import etree
import numpy as np

def load_audio(audio_file):
    init = datetime.datetime.now()
    print("loading audio")
    fullAudio = AudioSegment.from_wav(audio_file)
    print("audio for", os.path.basename(audio_file), "loaded in", datetime.datetime.now()-init, "min.sec.ms")
    return fullAudio

#_______________________________________________________________________________
def extract_first_5_CHN_clips(csv_file, audio):
    # Extract child ID from the CSV filename
    child_id = os.path.splitext(os.path.basename(csv_file))[0].split('_')[0]
    print(child_id)

    # Create output directory
    output_dir = os.path.join(working_dir,f"chn_clips/{child_id}_CHN_clips")
    os.makedirs(output_dir, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(csv_file)

    for index, row in df.iterrows():
        if row['segment_type'] == 'CHN':
            # Get the clip onset and offset times
            clip_onset = row['clip_onset'] * 1000  # Convert to milliseconds
            clip_offset = row['clip_offset'] * 1000  # Convert to milliseconds
            
            # Extract the segment
            extracted_clip = audio[clip_onset:clip_offset]

            # Create the output filename
            output_filename = f"{output_dir}/{child_id}_{row['seg_id']}_CHN_clip.wav"
            extracted_clip.export(output_filename, format="wav")
            print(f"Extracted: {output_filename}")

#_______________________________________________________________________________
def extract_audio_clips(csv_file, audio_file):
    # Extract child ID from the CSV filename
    # This identifies the recording, so same children at different time points are looked at as unique
    child_id = os.path.splitext(os.path.basename(csv_file))[0].split('_')[0]
    
    # Create output directory
    output_dir = os.path.join(working_dir,f"chn_clips/{child_id}_CHN_clips")
    os.makedirs(output_dir, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(csv_file)

    # Load the audio file
    audio = AudioSegment.from_file(audio_file)

    for index, row in df.iterrows():
        if row['segment_type'] == 'CHN':
            # Get the clip onset and offset times
            clip_onset = row['clip_onset'] * 1000  # Convert to milliseconds
            clip_offset = row['clip_offset'] * 1000  # Convert to milliseconds
            
            # Extract the segment
            extracted_clip = audio[clip_onset:clip_offset]

            # Create the output filename
            output_filename = f"{output_dir}/{child_id}_{row['seg_id']}_CHN_clip.wav"
            extracted_clip.export(output_filename, format="wav")
            print(f"Extracted: {output_filename}")

#_______________________________________________________________________________
if __name__ == "__main__":
    # Get the directory of the current script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    
    # box input directory for raw audio files
    input_dir = "" 
    # box input directory for CHN info and output
    working_dir = ""
    # directories for processed its files and chn timestamps on local machine
    chn_dir = working_dir+"chn_timestamp_metadata/"
    count = 0

    for csv_file in os.listdir(chn_dir):
        if csv_file.endswith("_CHN_timestamps.csv"):
            # Extract child ID from the CSV filename (e.g., "001TP1" from "001TP1_CHN_timestamps.csv")
            child_id = csv_file.split("_")[0]
            count += 1
            print(child_id)
            csv_file_path = os.path.join(chn_dir, csv_file)
            audio_file_path = os.path.join(input_dir, f"{child_id}.wav")

            print(audio_file_path)

            if os.path.exists(audio_file_path):
        
                # Skip this folder if it has already been processed
                if child_id in processed_child_ids:
                    print(f"Skipping already processed child_id: {child_id}")
                    continue
                    
                # load raw audio
                print("loading audio for " + child_id + "...")
                audio = load_audio(audio_file_path)


                # create 500 ms wav chunks
                extract_first_5_CHN_clips(csv_file_path,audio)    
                processed_child_ids.append(child_id) # append to processed_files list after processing

                # Display the first few rows of the DataFrame to ensure it's the right file
                print(f"Processing child ID: {child_id}")
                print(f"CSV File: {csv_file_path}")
                print(f"Audio File: {audio_file_path}")
                
            else:
                print("ERROR: audio file does not exist for " + child_id)
            
