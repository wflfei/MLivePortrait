

import asyncio
import os
import threading
import time
import tempfile
import shutil
from uuid import uuid4

root_project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_dir = os.path.join(root_project, 'data')

if not os.path.exists(data_dir):
    os.mkdir(data_dir)

dirve_video_dir = os.path.join(data_dir, 'drive')
if not os.path.exists(dirve_video_dir):
    os.mkdir(dirve_video_dir)

user_image_dir = os.path.join(data_dir, 'user_image')
if not os.path.exists(user_image_dir):
    os.mkdir(user_image_dir)

watermark_video_dir = os.path.join(data_dir, 'watermarked')
if not os.path.exists(watermark_video_dir):
    os.mkdir(watermark_video_dir)

logo_file = os.path.join(root_project, 'assets/app/logo.png')


class AppFile:

    @staticmethod
    def new_user_image(old_file_name: str, content: bytes):
        file_name = str(uuid4()) + AppFile.get_file_suffix(old_file_name)
        with open(os.path.join(user_image_dir, file_name), 'wb') as f:
            f.write(content)

    @staticmethod
    def write_user_image(file_name: str, content: bytes):
        file_path = AppFile.get_user_image_file_path(file_name)
        if not os.path.exists(file_path):
            with open(file_path, 'wb') as f:
                f.write(content)
        return file_path

    @staticmethod
    def get_file_suffix(file_name):
        return os.path.splitext(file_name)[-1]

    @staticmethod
    def get_user_image_file_path(file_name):
        return os.path.join(user_image_dir, file_name)

    def delete_file(file_name):
        file_path = AppFile.get_user_image_file_path(file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

    def get_drive_file_path(file_id):
        # pkl_file = os.path.join(dirve_video_dir, file_id + '.pkl')
        # if os.path.exists(pkl_file):
        #     return pkl_file
        # check mp4 file
        mp4_file = os.path.join(dirve_video_dir, file_id + '.mp4')
        if os.path.exists(mp4_file):
            return mp4_file
        return None

    @staticmethod
    def get_watermark_video_file_path(file_id, check=False):
        mp4_file = os.path.join(watermark_video_dir, file_id + '.mp4')
        if check:
            if os.path.exists(mp4_file):
                return mp4_file
            else:
                return None
        else:
            return mp4_file

    @staticmethod
    def new_watermark_video_file():
        filename = str(uuid4()) + '.mp4'
        mp4_file = AppFile.get_watermark_video_file_path(filename)
        return mp4_file, filename

    @staticmethod
    def clean_data():
        print("cleaning user data ...")
        for file_name in os.listdir(user_image_dir):
            file_path = os.path.join(user_image_dir, file_name)
            create_time = os.path.getctime(file_path)
            # delete file more than 12 hours
            if os.path.isfile(file_path) and time.time() - create_time > 12 * 60 * 60:
                os.remove(file_path)


def loop_clean_data():
    while True:
        time.sleep(8 * 60 * 60)
        AppFile.clean_data()
        clean_gradio_tmp_files()


def schedule_clean_data():
    # loop = asyncio.get_event_loop()
    # loop.create_task(loop_clean_data())
    threading.Thread(target=loop_clean_data, daemon=True).start()


def force_remove_folder(folder_path):
    try:
        # 使用shutil.rmtree()强制删除文件夹及其所有内容
        shutil.rmtree(folder_path)
        print(f"文件夹 '{folder_path}' 已成功删除。")
    except FileNotFoundError:
        print(f"文件夹 '{folder_path}' 不存在。")
    except PermissionError:
        print(f"没有权限删除文件夹 '{folder_path}'。")
    except Exception as e:
        print(f"删除文件夹 '{folder_path}' 时发生错误: {str(e)}")


def clean_gradio_tmp_files():
    print("cleaning gradio tmp files ...")
    tmp_dir = tempfile.gettempdir()
    gradio_temp = os.path.join(tmp_dir, "gradio")
    for file_name in os.listdir(gradio_temp):
        file_path = os.path.join(gradio_temp, file_name)
        create_time = os.path.getctime(file_path)
        # delete dirs more than 12 hours
        if time.time() - create_time > 8 * 60 * 60:
            force_remove_folder(file_path)


if __name__ == '__main__':
    print(AppFile.get_file_suffix("sjdbu.png"))
