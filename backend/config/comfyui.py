"""ComfyUI工作流配置 - 电商图片生成流水线"""
import os
from typing import Any

# ComfyUI服务地址
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://127.0.0.1:8188")

# 各平台图片规范配置
PLATFORM_IMAGE_CONFIG = {
    "pdd": {
        "main_image": {"size": (800, 800), "bg": "white", "count": 5},
        "style_prompt": "clean white background, professional product photo, studio lighting, high resolution, e-commerce style",
    },
    "taobao": {
        "main_image": {"size": (800, 800), "bg": "white", "count": 3},
        "style_prompt": "clean white background, e-commerce product photo, professional lighting",
    },
    "douyin": {
        "main_image": {"size": (1080, 1080), "bg": "scene", "count": 9},
        "style_prompt": "lifestyle scene, trendy, vibrant colors, young aesthetic, high quality",
    },
    "xiaohongshu": {
        "main_image": {"size": (1080, 1080), "bg": "scene", "count": 9},
        "style_prompt": "instagram style, warm tones, minimalist, lifestyle photography, high saturation",
    },
}


def load_workflow(workflow_type: str) -> dict:
    """
    加载ComfyUI工作流模板

    Args:
        workflow_type: 工作流类型（birefnet_cutout / sdxl_scene / controlnet_pose等）

    Returns:
        工作流JSON配置
    """
    workflows = {
        "birefnet_cutout": {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "birefnet_v2.safetensors"},
            },
            "2": {
                "class_type": "LoadImage",
                "inputs": {"image": ""},  # 动态注入
            },
            "3": {
                "class_type": "BiRefNetProcessor",
                "inputs": {
                    "image": ["2", 0],
                    "model": "birefnet_v2",
                },
            },
            "4": {
                "class_type": "SaveImage",
                "inputs": {"images": ["3", 0], "filename_prefix": "output"},
            },
        },
        "sdxl_scene": {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sdxl_v1.0.safetensors"},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": ""},  # 动态注入prompt
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "low quality, blurry, distorted"},
            },
            "4": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["2", 0],
                    "negative": ["3", 0],
                    "seed": 42,
                    "steps": 30,
                    "cfg": 7.5,
                },
            },
            "5": {
                "class_type": "SaveImage",
                "inputs": {"images": ["4", 0], "filename_prefix": "output"},
            },
        },
        "controlnet_canny": {
            "1": {
                "class_type": "ControlNetLoader",
                "inputs": {"control_net_name": "control_v11p_sd15_canny.safetensors"},
            },
            "2": {
                "class_type": "ControlNetApply",
                "inputs": {
                    "conditioning": ["3", 0],
                    "control_net": ["1", 0],
                    "image": ["4", 0],
                },
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": ""},  # 动态注入prompt
            },
            "4": {
                "class_type": "LoadImage",
                "inputs": {"image": ""},  # 动态注入cutout图片
            },
        },
    }

    return workflows.get(workflow_type, {})


def inject_image(workflow: dict, image_path: str) -> dict:
    """在工作流中注入图片路径"""
    import copy
    wf = copy.deepcopy(workflow)

    for node_id, node in wf.items():
        inputs = node.get("inputs", {})
        for key, value in inputs.items():
            if isinstance(value, str) and value == "":
                # 找到需要注入图片的输入
                if key in ("image",):
                    inputs[key] = [image_path]
            elif isinstance(value, list) and len(value) == 2 and value[1] == 0:
                # 检查上游节点是否是LoadImage
                upstream = wf.get(str(value[0]), {})
                if upstream.get("class_type") == "LoadImage":
                    upstream_inputs = upstream.get("inputs", {})
                    if "image" in upstream_inputs and upstream_inputs["image"] == "":
                        upstream_inputs["image"] = image_path

    return wf


def get_platform_prompt(platform: str, product_title: str = "") -> str:
    """获取平台的图片风格prompt"""
    config = PLATFORM_IMAGE_CONFIG.get(platform, {})
    base_prompt = config.get("style_prompt", "")
    if product_title:
        base_prompt += f", featuring {product_title}"
    return base_prompt


def resize_for_platform(images: list[str], platform: str) -> list[str]:
    """
    将图片缩放到平台要求的尺寸

    Args:
        images: 输入图片路径列表
        platform: 平台名称（pdd/taobao/douyin/xiaohongshu）

    Returns:
        缩放后的图片路径列表
    """
    config = PLATFORM_IMAGE_CONFIG.get(platform, {})
    target_size = config.get("main_image", {}).get("size", (800, 800))
    resized = []

    for img_path in images:
        # TODO: 使用PIL进行缩放
        import shutil
        base, ext = os.path.splitext(img_path)
        resized_path = f"{base}_{target_size[0]}x{target_size[1]}{ext}"
        shutil.copy(img_path, resized_path)
        resized.append(resized_path)

    return resized
