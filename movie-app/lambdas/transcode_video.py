import os
import boto3
import json
import subprocess

s3_client = boto3.client('s3')
bucket_name = os.environ['BUCKET_NAME']
ffmpeg_path = '/opt/ffmpeg'  # Path where Lambda mounts the layer

def handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        video_id = message['video_id']
        file_name = message['file_name']
        format = message['format']

        # Determine the resolution based on format
        resolution_mapping = {
            "360p": "640x360",
            "720p": "1280x720",
            "1080p": "1920x1080",
        }
        resolution = resolution_mapping.get(format, "1280x720")  # Default to 720p

        # Download the video file from S3
        local_input_path = f"/tmp/{file_name}"
        local_output_path = f"/tmp/{video_id}_{format}.mp4"

        s3_client.download_file(bucket_name, file_name, local_input_path)

        # Run FFmpeg command
        command = [
            ffmpeg_path,
            '-i', local_input_path,
            '-vf', f'scale={resolution}',
            local_output_path
        ]

        try:
            result = subprocess.run(command, check=True)
            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
                raise Exception(f"FFmpeg command failed with exit code {result.returncode}")

            print(f"Transcoded {file_name} to {local_output_path} with resolution {format}")



            # Upload the transcoded video back to S3
            transcoded_file_name = f"{format}/{video_id}.mp4"
            s3_client.upload_file(local_output_path, bucket_name, transcoded_file_name)

        except subprocess.CalledProcessError as e:
            print(f"Error during transcoding: {e}")

        finally:
            # Clean up local files
            os.remove(local_input_path)
            os.remove(local_output_path)
