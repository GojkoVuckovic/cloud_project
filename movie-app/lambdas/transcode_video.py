import os
import boto3
import json
import subprocess
import time

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']
ffmpeg_path = '/opt/ffmpeg'  # Path where Lambda mounts the layer

def handler(event, context):
    
    
    for record in event['Records']:
        message = json.loads(record['body'])
        file_key = message['file_key']
        format = message['resolution']

        # Determine the resolution based on format
        resolution_mapping = {
            "360p": "320",
            "720p": "720",
            "1080p": "1080",
        }

        resolution_new = format.replace("p", "")

        timestamp = int(time.time())
        width = resolution_mapping.get(format, "1280")  # Default to 720p width

        print(f"Transcoding {file_key} to {format} with width {width} in bucket: {bucket_name}")

        # Extract file name without extension
        video_id, file_extension = os.path.splitext(file_key)

        new_input_key = f"{timestamp}_{video_id}_input_{format}{file_extension}"
        new_output_key = f"{timestamp}_{video_id}_output_{format}{file_extension}"



        # Prepare local file paths with timestamp
        local_input_path = f"/tmp/{new_input_key}"
        local_output_path = f"/tmp/{new_output_key}"

        # Ensure the output directory exists
        # os.makedirs(local_output_dir, exist_ok=True)

        # Download the video file from S3
        try:
            s3_client.download_file(bucket_name, file_key, local_input_path)
        except Exception as e:
            print(f"Error downloading file {file_key}: {e}")
            continue

        # Run FFmpeg command to scale while preserving aspect ratio
        command = [
            ffmpeg_path,
            '-i', local_input_path,
            '-vf', f'scale=-2:{resolution_new}',
            '-preset', 'fast',
            local_output_path
        ]

        try:
            result = subprocess.run(command, check=True, capture_output=True)
            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr.decode()}")
                raise Exception(f"FFmpeg command failed with exit code {result.returncode}")

            print(f"Transcoded {file_key} to {local_output_path} with resolution {format}")

            # Upload the transcoded video back to S3
            transcoded_file_name = f"{format}/{video_id}{file_extension}"
            s3_client.upload_file(local_output_path, bucket_name, transcoded_file_name)

        except subprocess.CalledProcessError as e:
            print(f"Error during transcoding: {e}")

        finally:
            # Clean up local files
            if os.path.exists(local_input_path):
                os.remove(local_input_path)
            if os.path.exists(local_output_path):
                os.remove(local_output_path)
