import ffmpeg
import os

"""
Скрипт для локального препроцессинга mp3 файлов в HLS формат
Сейчас нигде не используется, но мало ли вдруг пригодится
"""

path_to_files = "audios"
path_to_raw_files = os.path.join("audios", "raw")
segment_duration = 10
bitrates = [256, 128, 32]

def process_raw_files(raw_files):
    for raw_file, raw_dir in raw_files:
        input_file = os.path.join(path_to_raw_files, raw_file)
        output_dir = os.path.join(path_to_files, raw_dir)
        os.makedirs(output_dir, exist_ok=True)
        for bitrate in bitrates:
            output_dir_bitrate = f"{str(bitrate)}k"
            os.makedirs(os.path.join(output_dir, output_dir_bitrate), exist_ok=True)
            playlist = os.path.join(os.path.join(output_dir, output_dir_bitrate), f"{str(bitrate)}k.m3u8")
            input_file_bitrate = str(bitrate) + "k.mp3"
            print(os.path.join(output_dir, output_dir_bitrate))
            print(input_file)
            ffmpeg.FFmpeg().input(input_file).output(
                os.path.join(os.path.join(output_dir, output_dir_bitrate), input_file_bitrate),
                {"b:a": str(bitrate) + "k"},
                acodec='libmp3lame'
            ).execute()
            print(os.path.join(os.path.join(output_dir, output_dir_bitrate), input_file_bitrate))
            print(os.path.join(os.path.join(output_dir, output_dir_bitrate), 'output.ts'))
            ffmpeg.FFmpeg().input(os.path.join(os.path.join(output_dir, output_dir_bitrate), input_file_bitrate)).output(
                playlist,
                format="hls",
                acodec="aac",
                hls_time=5,
                hls_list_size=0,
                hls_segment_filename=f"{os.path.join(output_dir, output_dir_bitrate)}/output%03d.ts",
                hls_base_url=f"http://localhost:8080/stream/{raw_dir}%5C{bitrate}k%5C",
            ).execute()

if __name__ == "__main__":
    # указать свои файлы
    raw_files = [
        ("Fall Out Boy - Sugar, We're Goin Down.mp3", "Fall Out Boy - Sugar, We're Goin Down"),
        ("3 Doors Down - When I'm Gone.mp3", "3 Doors Down - When I'm Gone")
    ]
    process_raw_files(raw_files)
