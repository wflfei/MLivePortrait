


import subprocess
from custom.app_file import logo_file


def exec_cmd(cmd):
    return subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def get_video_dimensions(video_path):
    # 使用ffprobe获取视频的宽度和高度
    probe_cmd = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 {video_path}'
    result = subprocess.run(probe_cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    width, height = map(int, result.stdout.strip().split('x'))
    return width, height

def add_app_watermark(source_path, dest_path, watermark_path=logo_file):
    video_width, video_height = get_video_dimensions(source_path)
    left = int(video_width * 0.05)
    top = int(video_height * 0.025)
    print(f'add watermark, origin w: {video_width}, origin h: {video_height}')

    cmd = (
        f'ffmpeg -i "{source_path}" '
        f'-i "{watermark_path}" '
        '-filter_complex "'
        f'[1]scale=w={int(video_width / 5)}:h=-1:force_original_aspect_ratio=decrease,setsar=1[wm];'
        f'[0][wm]overlay=x={left}:y={top}" '
        '-c:v libopenh264 -crf 23 -c:a copy '
        f'"{dest_path}" -y'
    )
    exec_cmd(cmd)
