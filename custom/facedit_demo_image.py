
import os


root_project = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
facedit_demo_image_dir = os.path.join(root_project, 'assets/app')


def is_facedit_demo_image(file_id: str):
    return file_id.startswith("facedit_demo")


def get_facedit_demo_image_path(file_id: str):
    if is_facedit_demo_image(file_id):
        return os.path.join(facedit_demo_image_dir, file_id)
    return None
