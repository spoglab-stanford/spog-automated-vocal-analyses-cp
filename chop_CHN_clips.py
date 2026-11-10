from pydub import AudioSegment
import os


#{audio}_{chn clip}_segment_{segment id}

def chop_audio(child_id, input_file, output_dir, metadata_file):
    # Load the audio file
    audio = AudioSegment.from_file(input_file)
    
    # Define the chunk length
    chunk_length_ms = 500
    
    # Prepare to store segments
    segments = []

    clip_id = input_file.split("/")[-1].split("_")[1]
    print("clip id",clip_id)
    
    # Chop the audio into 500 ms bits
    for start in range(0, len(audio), chunk_length_ms):
        end = start + chunk_length_ms
        segment = audio[start:end]
        segments.append(segment)

    # Check for remainder
    remainder_start = len(audio) // chunk_length_ms * chunk_length_ms
    remainder = audio[remainder_start:]
    print(len(remainder))

    if len(remainder) > 0:
        if len(remainder) < 200:
            # Append to the last segment
            segments[-2] += remainder    
            segments.pop()  # Remove the last segment

        os.makedirs(output_dir, exist_ok=True)

        # Ensure metadata directory exists
        metadata_dir = os.path.dirname(metadata_file)  # Get the directory of the metadata file
        os.makedirs(metadata_dir, exist_ok=True)  # Create it if it doesn't exist

        # Check if the metadata file exists
        file_exists = os.path.isfile(metadata_file)
        
        with open(metadata_file, 'a') as meta_file:
            if not file_exists:
                meta_file.write("child_id, CHN_clip_id, segment_id, duration (ms), filename, corresponding_CHN_clip, \n")  # Write header only if file does not exist
                                    
            for i, segment in enumerate(segments):
                segment_id = f"{i + 1}"
                segment_file = f"{child_id}_{clip_id}_segment_{i + 1}"
                segment_length = len(segment)
                segment.export(os.path.join(output_dir, f"{child_id}_{clip_id}_segment_{segment_id}.wav"), format="wav")
                corresponding_CHN_clip = f"{child_id}_{clip_id}"
                
                # Write segment info to the metadata file
                meta_file.write(f"{child_id}, {clip_id}, {segment_id}, {segment_length}, {segment_file},{corresponding_CHN_clip}\n")

if __name__ == "__main__":
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # Construct the path to the audio file

    # box input directory for CHN clips
    input_dir = "" 
    # box input directory for CHN info and output
    working_dir = ""
    # directories for processed its files and chn timestamps on local machine
    chn_dir = os.path.join(input_dir, "chn_clips/") 
    current_directory = os.path.dirname(os.path.abspath(__file__))

    count = 0

    for folder in os.listdir(chn_dir):
        folder_path = os.path.join(chn_dir, folder)
        # Extract child ID from the CSV filename (e.g., "001TP1" from "001TP1_CHN_timestamps.csv")
        child_id = folder_path.split("/")[-1].split("_")[0]
        print(child_id)
        # Skip hidden files like .DS_Store (common on macOS)
        if folder.startswith("."):
            print(f"Skipping hidden file/folder: {folder}")
            continue

        output_dir = os.path.join(current_directory, f"500ms_segments/{child_id}")
        if os.path.exists(output_dir):
            print(f"Skipping {child_id}: output directory already exists.")
            continue  # Skip this child_id if output directory already exists

        metadata_file_path = os.path.join(current_directory, f"500ms_segment_metadata/{child_id}_segment_metadata.csv")  # Define your metadata file path

        # Iterate through the files in this folder
        for clip in os.listdir(folder_path):
            clip_path = os.path.join(folder_path, clip)
            
            # Check if the file is a .wav audio file
            if clip.endswith(".wav") and os.path.isfile(clip_path):
                count += 1
                #print(f"Found audio file: {clip_path}")

                
                chop_audio(child_id, clip_path, output_dir, metadata_file_path)
                print(f"Chopping CHN clip: {clip}")

        # After processing the folder, add child_id to the processed list
        print(f"Completed processing for child_id: {child_id}. Added to processed list.")


