# coding: utf-8

"""
The entrance of the gradio for human
"""

import os
import shutil
import time
import tyro
import subprocess
import gradio as gr
import os.path as osp
from custom.app_file import AppFile, schedule_clean_data, root_project
from custom.facedit_demo_image import get_facedit_demo_image_path
from custom.watermark import add_app_watermark
from src.utils.helper import load_description
from src.gradio_pipeline import GradioPipeline
from src.config.crop_config import CropConfig
from src.config.argument_config import ArgumentConfig
from src.config.inference_config import InferenceConfig


def partial_fields(target_class, kwargs):
    return target_class(**{k: v for k, v in kwargs.items() if hasattr(target_class, k)})


def fast_check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except:
        return False


# set tyro theme
tyro.extras.set_accent_color("bright_cyan")
args = tyro.cli(ArgumentConfig)

ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
if osp.exists(ffmpeg_dir):
    os.environ["PATH"] += (os.pathsep + ffmpeg_dir)

if not fast_check_ffmpeg():
    raise ImportError(
        "FFmpeg is not installed. Please install FFmpeg (including ffmpeg and ffprobe) before running this script. https://ffmpeg.org/download.html"
    )
# specify configs for inference
inference_cfg = partial_fields(InferenceConfig, args.__dict__)  # use attribute of args to initial InferenceConfig
crop_cfg = partial_fields(CropConfig, args.__dict__)  # use attribute of args to initial CropConfig
# global_tab_selection = None

gradio_pipeline = GradioPipeline(
    inference_cfg=inference_cfg,
    crop_cfg=crop_cfg,
    args=args
)

if args.gradio_temp_dir not in (None, ''):
    os.environ["GRADIO_TEMP_DIR"] = args.gradio_temp_dir
    os.makedirs(args.gradio_temp_dir, exist_ok=True)


def gpu_wrapped_execute_video(*args, **kwargs):
    return gradio_pipeline.execute_video(*args, **kwargs)


def gpu_wrapped_execute_image_retargeting(*args, **kwargs):
    return gradio_pipeline.execute_image_retargeting(*args, **kwargs)


def gpu_wrapped_execute_video_retargeting(*args, **kwargs):
    return gradio_pipeline.execute_video_retargeting(*args, **kwargs)


def reset_sliders(*args, **kwargs):
    return 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.5, True, True


# -- custom --
def wrapped_init_retargeting_image(*args, **kwargs):
    source_eye_ratio, source_lip_ratio, crop_img = gradio_pipeline.init_retargeting_image(*args, **kwargs)
    file_name = f"{int(time.time() * 1000)}{AppFile.get_file_suffix(args[3])}"
    file_location = AppFile.get_user_image_file_path(file_name)
    shutil.copyfile(args[3], file_location)
    return source_eye_ratio, source_lip_ratio, source_eye_ratio, source_lip_ratio, file_name, crop_img


def gpu_wrapped_execute_video_bypath(*args, **kwargs):
    drive_video_path = args[3]
    # args = args[:3] + AppFile.get_drive_file_path(drive_video_path) + args[4:]
    list_args = list(args)
    driving_path = AppFile.get_drive_file_path(drive_video_path)
    list_args[3] = driving_path
    if driving_path and driving_path.endswith('pkl'):
        list_args[2] = driving_path
        list_args[20] = "Pickle"
    else:
        list_args[20] = "Video"

    video_path, video_path_concat = gradio_pipeline.execute_video(*list_args, **kwargs)
    # add watermark
    watermarked_video_path, watermarked_video_id = AppFile.new_watermark_video_file()
    full_source_path = os.path.join(root_project, video_path)
    add_app_watermark(full_source_path, watermarked_video_path)
    return video_path, watermarked_video_path


def gpu_wrapped_execute_image_retargeting_bypath(*args, **kwargs):
    retargeting_input_image_path: str = args[19]
    # args = args[:19] + AppFile.get_file_path(retargeting_input_image_path) + args[20:]
    list_args = list(args)
    demo_image = get_facedit_demo_image_path(retargeting_input_image_path)
    if demo_image is not None:
        list_args[19] = demo_image
    else:
        list_args[19] = AppFile.get_user_image_file_path(retargeting_input_image_path)
    return gradio_pipeline.execute_image_retargeting(*list_args, **kwargs)


# assets
title_md = "assets/gradio/gradio_title.md"
example_portrait_dir = "assets/examples/source"
example_video_dir = "assets/examples/driving"
data_examples_i2v = [
    [osp.join(example_portrait_dir, "s9.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, False],
    [osp.join(example_portrait_dir, "s6.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, False],
    [osp.join(example_portrait_dir, "s10.jpg"), osp.join(example_video_dir, "d0.mp4"), True, True, True, False],
    [osp.join(example_portrait_dir, "s5.jpg"), osp.join(example_video_dir, "d18.mp4"), True, True, True, False],
    [osp.join(example_portrait_dir, "s7.jpg"), osp.join(example_video_dir, "d19.mp4"), True, True, True, False],
    [osp.join(example_portrait_dir, "s2.jpg"), osp.join(example_video_dir, "d13.mp4"), True, True, True, True],
]
data_examples_v2v = [
    [osp.join(example_portrait_dir, "s13.mp4"), osp.join(example_video_dir, "d0.mp4"), True, True, True, False, False, 3e-7],
    # [osp.join(example_portrait_dir, "s14.mp4"), osp.join(example_video_dir, "d18.mp4"), True, True, True, False, False, 3e-7],
    # [osp.join(example_portrait_dir, "s15.mp4"), osp.join(example_video_dir, "d19.mp4"), True, True, True, False, False, 3e-7],
    [osp.join(example_portrait_dir, "s18.mp4"), osp.join(example_video_dir, "d6.mp4"), True, True, True, False, False, 3e-7],
    # [osp.join(example_portrait_dir, "s19.mp4"), osp.join(example_video_dir, "d6.mp4"), True, True, True, False, False, 3e-7],
    [osp.join(example_portrait_dir, "s20.mp4"), osp.join(example_video_dir, "d0.mp4"), True, True, True, False, False, 3e-7],
]
#################### interface logic ####################

# Define components first
retargeting_source_scale = gr.Number(minimum=1.8, maximum=3.2, value=2.5, step=0.05, label="crop scale")
video_retargeting_source_scale = gr.Number(minimum=1.8, maximum=3.2, value=2.3, step=0.05, label="crop scale")
driving_smooth_observation_variance_retargeting = gr.Number(value=3e-6, label="motion smooth strength", minimum=1e-11, maximum=1e-2, step=1e-8)
eye_retargeting_source_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="source eyes-open ratio", interactive=False)
lip_retargeting_source_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="source lip-open ratio", interactive=False)
eye_retargeting_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="target eyes-open ratio")
lip_retargeting_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="target lip-open ratio")
video_lip_retargeting_slider = gr.Slider(minimum=0, maximum=0.8, step=0.01, label="target lip-open ratio")
head_pitch_slider = gr.Slider(minimum=-15.0, maximum=15.0, value=0, step=1, label="relative pitch")
head_yaw_slider = gr.Slider(minimum=-25, maximum=25, value=0, step=1, label="relative yaw")
head_roll_slider = gr.Slider(minimum=-15.0, maximum=15.0, value=0, step=1, label="relative roll")
mov_x = gr.Slider(minimum=-0.19, maximum=0.19, value=0.0, step=0.01, label="x-axis movement")
mov_y = gr.Slider(minimum=-0.19, maximum=0.19, value=0.0, step=0.01, label="y-axis movement")
mov_z = gr.Slider(minimum=0.9, maximum=1.2, value=1.0, step=0.01, label="z-axis movement")
lip_variation_zero = gr.Slider(minimum=-0.09, maximum=0.09, value=0, step=0.01, label="pouting")
lip_variation_one = gr.Slider(minimum=-20.0, maximum=15.0, value=0, step=0.01, label="pursing 😐")
lip_variation_two = gr.Slider(minimum=0.0, maximum=15.0, value=0, step=0.01, label="grin 😁")
lip_variation_three = gr.Slider(minimum=-90.0, maximum=120.0, value=0, step=1.0, label="lip close <-> open")
smile = gr.Slider(minimum=-0.3, maximum=1.3, value=0, step=0.01, label="smile 😄")
wink = gr.Slider(minimum=0, maximum=39, value=0, step=0.01, label="wink 😉")
eyebrow = gr.Slider(minimum=-30, maximum=30, value=0, step=0.01, label="eyebrow 🤨")
eyeball_direction_x = gr.Slider(minimum=-30.0, maximum=30.0, value=0, step=0.01, label="eye gaze (horizontal) 👀")
eyeball_direction_y = gr.Slider(minimum=-63.0, maximum=63.0, value=0, step=0.01, label="eye gaze (vertical) 🙄")
retargeting_input_image = gr.Image(type="filepath")
retargeting_input_video = gr.Video()
output_image = gr.Image(type="numpy")
output_image_paste_back = gr.Image(type="numpy")
retargeting_output_image = gr.Image(type="numpy")
retargeting_output_image_paste_back = gr.Image(type="numpy")
output_video = gr.Video(autoplay=False)
output_video_paste_back = gr.Video(autoplay=False)
output_video_i2v = gr.Video(autoplay=False)
output_video_concat_i2v = gr.Video(autoplay=False)

# -- custom --
# retargeting_input_image_path = gr.Textbox(type="text", label="Input Image Path")
# driving_video_input_path = gr.Textbox(type="text", label="Driving Video Path")


with gr.Blocks(theme=gr.themes.Soft(font=[gr.themes.GoogleFont("Plus Jakarta Sans")])) as demo:
    gr.HTML(load_description(title_md))

    gr.Markdown(load_description("assets/gradio/gradio_description_upload.md"))
    with gr.Row():
        with gr.Column():
            with gr.Tabs():
                with gr.TabItem("🖼️ Source Image") as tab_image:
                    with gr.Accordion(open=True, label="Source Image"):
                        source_image_input = gr.Image(type="filepath")
                        gr.Examples(
                            examples=[
                                [osp.join(example_portrait_dir, "s9.jpg")],
                                [osp.join(example_portrait_dir, "s6.jpg")],
                                [osp.join(example_portrait_dir, "s10.jpg")],
                                [osp.join(example_portrait_dir, "s5.jpg")],
                                [osp.join(example_portrait_dir, "s7.jpg")],
                                [osp.join(example_portrait_dir, "s12.jpg")],
                                [osp.join(example_portrait_dir, "s22.jpg")],
                                [osp.join(example_portrait_dir, "s23.jpg")],
                            ],
                            inputs=[source_image_input],
                            cache_examples=False,
                        )

                with gr.TabItem("🎞️ Source Video") as tab_video:
                    with gr.Accordion(open=True, label="Source Video"):
                        source_video_input = gr.Video()
                        gr.Examples(
                            examples=[
                                [osp.join(example_portrait_dir, "s13.mp4")],
                                # [osp.join(example_portrait_dir, "s14.mp4")],
                                # [osp.join(example_portrait_dir, "s15.mp4")],
                                [osp.join(example_portrait_dir, "s18.mp4")],
                                # [osp.join(example_portrait_dir, "s19.mp4")],
                                [osp.join(example_portrait_dir, "s20.mp4")],
                            ],
                            inputs=[source_video_input],
                            cache_examples=False,
                        )

                tab_selection = gr.Textbox(visible=False)
                tab_image.select(lambda: "Image", None, tab_selection)
                tab_video.select(lambda: "Video", None, tab_selection)
            with gr.Accordion(open=True, label="Cropping Options for Source Image or Video"):
                with gr.Row():
                    flag_do_crop_input = gr.Checkbox(value=True, label="do crop (source)")
                    scale = gr.Number(value=2.3, label="source crop scale", minimum=1.8, maximum=3.2, step=0.05)
                    vx_ratio = gr.Number(value=0.0, label="source crop x", minimum=-0.5, maximum=0.5, step=0.01)
                    vy_ratio = gr.Number(value=-0.125, label="source crop y", minimum=-0.5, maximum=0.5, step=0.01)

        with gr.Column():
            with gr.Tabs():
                with gr.TabItem("🎞️ Driving Video") as v_tab_video:
                    with gr.Accordion(open=True, label="Driving Video"):
                        driving_video_input = gr.Video()
                        gr.Examples(
                            examples=[
                                [osp.join(example_video_dir, "d0.mp4")],
                                [osp.join(example_video_dir, "d18.mp4")],
                                [osp.join(example_video_dir, "d19.mp4")],
                                [osp.join(example_video_dir, "d14.mp4")],
                                [osp.join(example_video_dir, "d6.mp4")],
                                [osp.join(example_video_dir, "d20.mp4")],
                            ],
                            inputs=[driving_video_input],
                            cache_examples=False,
                        )
                with gr.TabItem("📁 Driving Pickle") as v_tab_pickle:
                    with gr.Accordion(open=True, label="Driving Pickle"):
                        driving_video_pickle_input = gr.File(type="filepath", file_types=[".pkl"])
                        gr.Examples(
                            examples=[
                                [osp.join(example_video_dir, "d1.pkl")],
                                [osp.join(example_video_dir, "d2.pkl")],
                                [osp.join(example_video_dir, "d5.pkl")],
                                [osp.join(example_video_dir, "d7.pkl")],
                                [osp.join(example_video_dir, "d8.pkl")],
                            ],
                            inputs=[driving_video_pickle_input],
                            cache_examples=False,
                        )

                v_tab_selection = gr.Textbox(visible=False)
                v_tab_pickle.select(lambda: "Pickle", None, v_tab_selection)
                v_tab_video.select(lambda: "Video", None, v_tab_selection)
            # with gr.Accordion(open=False, label="Animation Instructions"):
                # gr.Markdown(load_description("assets/gradio/gradio_description_animation.md"))
            with gr.Accordion(open=True, label="Cropping Options for Driving Video"):
                with gr.Row():
                    flag_crop_driving_video_input = gr.Checkbox(value=False, label="do crop (driving)")
                    scale_crop_driving_video = gr.Number(value=2.2, label="driving crop scale", minimum=1.8, maximum=3.2, step=0.05)
                    vx_ratio_crop_driving_video = gr.Number(value=0.0, label="driving crop x", minimum=-0.5, maximum=0.5, step=0.01)
                    vy_ratio_crop_driving_video = gr.Number(value=-0.1, label="driving crop y", minimum=-0.5, maximum=0.5, step=0.01)

    with gr.Row():
        with gr.Accordion(open=True, label="Animation Options"):
            with gr.Row():
                flag_relative_input = gr.Checkbox(value=True, label="relative motion")
                flag_remap_input = gr.Checkbox(value=True, label="paste-back")
                flag_stitching_input = gr.Checkbox(value=True, label="stitching")
                driving_option_input = gr.Radio(['expression-friendly', 'pose-friendly'], value="expression-friendly", label="driving option (i2v)")
                driving_multiplier = gr.Number(value=1.0, label="driving multiplier (i2v)", minimum=0.0, maximum=2.0, step=0.02)
                flag_video_editing_head_rotation = gr.Checkbox(value=False, label="relative head rotation (v2v)")
                driving_smooth_observation_variance = gr.Number(value=3e-7, label="motion smooth strength (v2v)", minimum=1e-11, maximum=1e-2, step=1e-8)

    gr.Markdown(load_description("assets/gradio/gradio_description_animate_clear.md"))
    with gr.Row():
        process_button_animation = gr.Button("🚀 Animate", variant="primary")
    with gr.Row():
        with gr.Column():
            with gr.Accordion(open=True, label="The animated video in the original image space"):
                output_video_i2v.render()
        with gr.Column():
            with gr.Accordion(open=True, label="The animated video"):
                output_video_concat_i2v.render()
    with gr.Row():
        process_button_reset = gr.ClearButton([source_image_input, source_video_input, driving_video_pickle_input, driving_video_input, output_video_i2v, output_video_concat_i2v], value="🧹 Clear")

    with gr.Row():
        # Examples
        gr.Markdown("## You could also choose the examples below by one click ⬇️")
    with gr.Row():
        with gr.Tabs():
            with gr.TabItem("🖼️ Portrait Animation"):
                gr.Examples(
                    examples=data_examples_i2v,
                    fn=gpu_wrapped_execute_video,
                    inputs=[
                        source_image_input,
                        driving_video_input,
                        flag_relative_input,
                        flag_do_crop_input,
                        flag_remap_input,
                        flag_crop_driving_video_input,
                    ],
                    outputs=[output_image, output_image_paste_back],
                    examples_per_page=len(data_examples_i2v),
                    cache_examples=False,
                )
            with gr.TabItem("🎞️ Portrait Video Editing"):
                gr.Examples(
                    examples=data_examples_v2v,
                    fn=gpu_wrapped_execute_video,
                    inputs=[
                        source_video_input,
                        driving_video_input,
                        flag_relative_input,
                        flag_do_crop_input,
                        flag_remap_input,
                        flag_crop_driving_video_input,
                        flag_video_editing_head_rotation,
                        driving_smooth_observation_variance,
                    ],
                    outputs=[output_image, output_image_paste_back],
                    examples_per_page=len(data_examples_v2v),
                    cache_examples=False,
                )

    # -- custom --
    with gr.Row():
        driving_video_input_path = gr.Textbox(type="text", label="Driving Video Path")
        retargeting_input_image_path = gr.Textbox(type="text", label="Input Image Path")
        path_generate_btn = gr.Button("Path Video Execute")
        path_retargeting_btn = gr.Button("Path Retargeting")
        path_generate_btn.click(
            fn=gpu_wrapped_execute_video_bypath,
            inputs=[
                source_image_input,
                source_video_input,
                driving_video_pickle_input,
                driving_video_input_path,
                flag_relative_input,
                flag_do_crop_input,
                flag_remap_input,
                flag_stitching_input,
                driving_option_input,
                driving_multiplier,
                flag_crop_driving_video_input,
                flag_video_editing_head_rotation,
                scale,
                vx_ratio,
                vy_ratio,
                scale_crop_driving_video,
                vx_ratio_crop_driving_video,
                vy_ratio_crop_driving_video,
                driving_smooth_observation_variance,
                tab_selection,
                v_tab_selection,
            ],
            outputs=[output_video_i2v, output_video_concat_i2v],
            show_progress=True
        )

    # Retargeting Image
    gr.Markdown(load_description("assets/gradio/gradio_description_retargeting.md"), visible=True)
    with gr.Row(visible=True):
        flag_do_crop_input_retargeting_image = gr.Checkbox(value=True, label="do crop (source)")
        flag_stitching_retargeting_input = gr.Checkbox(value=True, label="stitching")
        eye_retargeting_source_slider.render()
        lip_retargeting_source_slider.render()
        retargeting_source_scale.render()
        eye_retargeting_slider.render()
        lip_retargeting_slider.render()
    with gr.Row(visible=True):
        with gr.Column():
            with gr.Accordion(open=True, label="Facial movement sliders"):
                with gr.Row(visible=True):
                    head_pitch_slider.render()
                    head_yaw_slider.render()
                    head_roll_slider.render()
                with gr.Row(visible=True):
                    mov_x.render()
                    mov_y.render()
                    mov_z.render()
        with gr.Column():
            with gr.Accordion(open=True, label="Facial expression sliders"):
                with gr.Row(visible=True):
                    lip_variation_zero.render()
                    lip_variation_one.render()
                    lip_variation_two.render()
                with gr.Row(visible=True):
                    lip_variation_three.render()
                    smile.render()
                    wink.render()
                with gr.Row(visible=True):
                    eyebrow.render()
                    eyeball_direction_x.render()
                    eyeball_direction_y.render()
    with gr.Row(visible=True):
        reset_button = gr.Button("🔄 Reset")
        reset_button.click(
            fn=reset_sliders,
            inputs=None,
            outputs=[
                head_pitch_slider, head_yaw_slider, head_roll_slider, mov_x, mov_y, mov_z,
                lip_variation_zero, lip_variation_one, lip_variation_two, lip_variation_three, smile, wink, eyebrow, eyeball_direction_x, eyeball_direction_y,
                retargeting_source_scale, flag_stitching_retargeting_input, flag_do_crop_input_retargeting_image
            ]
        )
    with gr.Row(visible=True):
        with gr.Column():
            with gr.Accordion(open=True, label="Retargeting Image Input"):
                retargeting_input_image.render()
                gr.Examples(
                    examples=[
                        [osp.join(example_portrait_dir, "s9.jpg")],
                        [osp.join(example_portrait_dir, "s6.jpg")],
                        [osp.join(example_portrait_dir, "s10.jpg")],
                        [osp.join(example_portrait_dir, "s5.jpg")],
                        [osp.join(example_portrait_dir, "s7.jpg")],
                        [osp.join(example_portrait_dir, "s12.jpg")],
                        [osp.join(example_portrait_dir, "s22.jpg")],
                        # [osp.join(example_portrait_dir, "s23.jpg")],
                        [osp.join(example_portrait_dir, "s42.jpg")],
                    ],
                    inputs=[retargeting_input_image],
                    cache_examples=False,
                )
        with gr.Column():
            with gr.Accordion(open=True, label="Retargeting Result"):
                retargeting_output_image.render()
        with gr.Column():
            with gr.Accordion(open=True, label="Paste-back Result"):
                retargeting_output_image_paste_back.render()
    with gr.Row(visible=True):
        process_button_reset_retargeting = gr.ClearButton(
            [
                retargeting_input_image,
                retargeting_output_image,
                retargeting_output_image_paste_back,
            ],
            value="🧹 Clear"
        )

    # Retargeting Video
    gr.Markdown(load_description("assets/gradio/gradio_description_retargeting_video.md"), visible=True)
    with gr.Row(visible=True):
        flag_do_crop_input_retargeting_video = gr.Checkbox(value=True, label="do crop (source)")
        video_retargeting_source_scale.render()
        video_lip_retargeting_slider.render()
        driving_smooth_observation_variance_retargeting.render()
    with gr.Row(visible=True):
        process_button_retargeting_video = gr.Button("🚗 Retargeting Video", variant="primary")
    with gr.Row(visible=True):
        with gr.Column():
            with gr.Accordion(open=True, label="Retargeting Video Input"):
                retargeting_input_video.render()
                gr.Examples(
                    examples=[
                        [osp.join(example_portrait_dir, "s13.mp4")],
                        # [osp.join(example_portrait_dir, "s18.mp4")],
                        [osp.join(example_portrait_dir, "s20.mp4")],
                        [osp.join(example_portrait_dir, "s29.mp4")],
                        [osp.join(example_portrait_dir, "s32.mp4")],
                    ],
                    inputs=[retargeting_input_video],
                    cache_examples=False,
                )
        with gr.Column():
            with gr.Accordion(open=True, label="Retargeting Result"):
                output_video.render()
        with gr.Column():
            with gr.Accordion(open=True, label="Paste-back Result"):
                output_video_paste_back.render()
    with gr.Row(visible=True):
        process_button_reset_retargeting = gr.ClearButton(
            [
                video_lip_retargeting_slider,
                retargeting_input_video,
                output_video,
                output_video_paste_back
            ],
            value="🧹 Clear"
        )

    # binding functions for buttons
    process_button_animation.click(
        fn=gpu_wrapped_execute_video,
        inputs=[
            source_image_input,
            source_video_input,
            driving_video_pickle_input,
            driving_video_input,
            flag_relative_input,
            flag_do_crop_input,
            flag_remap_input,
            flag_stitching_input,
            driving_option_input,
            driving_multiplier,
            flag_crop_driving_video_input,
            flag_video_editing_head_rotation,
            scale,
            vx_ratio,
            vy_ratio,
            scale_crop_driving_video,
            vx_ratio_crop_driving_video,
            vy_ratio_crop_driving_video,
            driving_smooth_observation_variance,
            tab_selection,
            v_tab_selection,
        ],
        outputs=[output_video_i2v, output_video_concat_i2v],
        show_progress=True
    )

    retargeting_input_image.change(
        fn=wrapped_init_retargeting_image,
        inputs=[retargeting_source_scale, eye_retargeting_slider, lip_retargeting_slider, retargeting_input_image],
        outputs=[eye_retargeting_source_slider, lip_retargeting_source_slider, eye_retargeting_slider, lip_retargeting_slider, retargeting_input_image_path, retargeting_output_image]
    )

    sliders = [eye_retargeting_slider, lip_retargeting_slider, head_pitch_slider, head_yaw_slider, head_roll_slider, mov_x, mov_y, mov_z, lip_variation_zero, lip_variation_one, lip_variation_two, lip_variation_three, smile, wink, eyebrow, eyeball_direction_x, eyeball_direction_y]
    for slider in sliders:
        # NOTE: gradio >= 4.0.0 may cause slow response
        slider.change(
            fn=gpu_wrapped_execute_image_retargeting,
            inputs=[
                eye_retargeting_source_slider, lip_retargeting_source_slider, eye_retargeting_slider, lip_retargeting_slider, head_pitch_slider, head_yaw_slider, head_roll_slider, mov_x, mov_y, mov_z,
                lip_variation_zero, lip_variation_one, lip_variation_two, lip_variation_three, smile, wink, eyebrow, eyeball_direction_x, eyeball_direction_y,
                retargeting_input_image, retargeting_source_scale, flag_stitching_retargeting_input, flag_do_crop_input_retargeting_image
            ],
            outputs=[retargeting_output_image, retargeting_output_image_paste_back],
        )

    process_button_retargeting_video.click(
        fn=gpu_wrapped_execute_video_retargeting,
        inputs=[video_lip_retargeting_slider, retargeting_input_video, video_retargeting_source_scale, driving_smooth_observation_variance_retargeting, flag_do_crop_input_retargeting_video],
        outputs=[output_video, output_video_paste_back],
        show_progress=True
    )

    path_retargeting_btn.click(
        fn=gpu_wrapped_execute_image_retargeting_bypath,
        inputs=[
            eye_retargeting_source_slider, lip_retargeting_source_slider, eye_retargeting_slider, lip_retargeting_slider, head_pitch_slider, head_yaw_slider, head_roll_slider, mov_x, mov_y, mov_z,
            lip_variation_zero, lip_variation_one, lip_variation_two, lip_variation_three, smile, wink, eyebrow, eyeball_direction_x, eyeball_direction_y,
            retargeting_input_image_path, retargeting_source_scale, flag_stitching_retargeting_input, flag_do_crop_input_retargeting_image
        ],
        outputs=[retargeting_output_image, retargeting_output_image_paste_back],
        show_progress=True
    )

schedule_clean_data()
demo.launch(
    server_port=args.server_port,
    share=False,
    server_name="0.0.0.0",
    auth=("yesit", "itsme")
)
