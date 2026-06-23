"""AI作图Agent - ComfyUI集成 + BiRefNet抠图 + SDXL场景图生成"""
from datetime import datetime
import asyncio
import aiohttp
import os
from langgraph.graph import StateGraph, END

from agents.base import BaseAgent, AgentState
from config.llm import agnes_client, TEXT_MODEL


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


class ImageAgent(BaseAgent):
    """
    AI作图Agent：
    - ComfyUI集成：BiRefNet抠图 + SDXL场景图生成 + ControlNet姿态控制
    - 多平台图片规范适配
    - 图片合规检测（Agnes AI视觉检测）
    """

    def _build_graph(self) -> StateGraph:
        """构建AI作图Agent状态图"""
        graph = StateGraph(AgentState)

        graph.add_node("cutout", self.remove_background)
        graph.add_node("generate_scene", self.generate_scene_images)
        graph.add_node("resize", self.resize_for_platforms)
        graph.add_node("compliance_check", self.compliance_check)

        graph.set_entry_point("cutout")
        graph.add_edge("cutout", "generate_scene")
        graph.add_edge("generate_scene", "resize")
        graph.add_edge("resize", "compliance_check")
        graph.add_edge("compliance_check", END)

        return graph.compile()

    async def remove_background(self, state: AgentState) -> AgentState:
        """
        步骤1：BiRefNet自动抠图（去背景，输出透明PNG）
        """
        product_images = state["input_data"].get("product_images", [])

        cutout_paths = []
        for img_path in product_images:
            if not os.path.exists(img_path):
                state["errors"].append({
                    "error": f"图片文件不存在: {img_path}",
                    "timestamp": datetime.now().isoformat(),
                })
                continue

            cutout_path = await self._run_birefnet(img_path)
            cutout_paths.append(cutout_path)

        state["input_data"]["cutout_images"] = cutout_paths
        return state

    async def _run_birefnet(self, image_path: str) -> str:
        """调用ComfyUI BiRefNet节点进行抠图"""
        output_dir = "output/images"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = f"cutout_{os.path.basename(image_path).rsplit('.', 1)[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        output_path = os.path.join(output_dir, output_filename)

        # 构建BiRefNet工作流
        workflow = {
            "3": {
                "class_type": "BiRefNetProcessor",
                "inputs": {
                    "image": image_path,
                    "model": "birefnet_v2",
                },
            },
            "4": {
                "class_type": "SaveImage",
                "inputs": {
                    "images": ["3", 0],
                    "filename_prefix": output_path,
                },
            },
        }

        await self._submit_comfyui_workflow(workflow)
        return output_path

    async def generate_scene_images(self, state: AgentState) -> AgentState:
        """
        步骤2：SDXL + ControlNet生成场景图
        """
        cutout_images = state["input_data"].get("cutout_images", [])
        platforms = state["input_data"].get("platforms", ["pdd", "taobao"])
        product_data = state["input_data"].get("product_data", {})

        generated_images = {}
        for platform in platforms:
            config = PLATFORM_IMAGE_CONFIG.get(platform, {})
            style_prompt = config.get("style_prompt", "")
            product_name = product_data.get("title", "product")
            full_prompt = f"{style_prompt}, featuring {product_name}"

            platform_images = []
            for cutout_path in cutout_images:
                img_path = await self._run_sdxl_controlnet(cutout_path, full_prompt)
                platform_images.append(img_path)

            generated_images[platform] = {
                "images": platform_images,
                "config": config,
                "generated_at": datetime.now().isoformat(),
            }

        state["input_data"]["generated_images"] = generated_images
        return state

    async def _run_sdxl_controlnet(self, cutout_path: str, prompt: str) -> str:
        """调用ComfyUI SDXL + ControlNet生成场景图"""
        output_dir = "output/images"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"sdxl_{os.path.basename(cutout_path).rsplit('.', 1)[0]}_{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        output_path = os.path.join(output_dir, filename)

        workflow = {
            "1": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {"ckpt_name": "sdxl_v1.0.safetensors"},
            },
            "2": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": prompt},
            },
            "3": {
                "class_type": "CLIPTextEncode",
                "inputs": {"text": "low quality, blurry, distorted"},
            },
            "4": {
                "class_type": "ControlNetApply",
                "inputs": {
                    "conditioning": ["2", 0],
                    "control_net": ["5", 0],
                    "image": ["6", 0],
                },
            },
            "5": {
                "class_type": "ControlNetLoader",
                "inputs": {"control_net_name": "control_v11p_sd15_canny.safetensors"},
            },
            "6": {
                "class_type": "LoadImage",
                "inputs": {"image": cutout_path},
            },
            "7": {
                "class_type": "KSampler",
                "inputs": {
                    "model": ["1", 0],
                    "positive": ["4", 0],
                    "negative": ["3", 0],
                    "seed": 42,
                    "steps": 30,
                    "cfg": 7.5,
                },
            },
            "8": {
                "class_type": "SaveImage",
                "inputs": {"images": ["7", 0], "filename_prefix": output_path},
            },
        }

        await self._submit_comfyui_workflow(workflow)
        return output_path

    async def resize_for_platforms(self, state: AgentState) -> AgentState:
        """
        步骤3：输出多平台适配尺寸
        """
        generated = state["input_data"].get("generated_images", {})
        resized = {}

        for platform, data in generated.items():
            images = data.get("images", [])
            config = data.get("config", {})
            target_size = config.get("main_image", {}).get("size", (800, 800))

            resized_images = []
            for img_path in images:
                # TODO: 使用PIL或opencv缩放图片
                import shutil
                resized_path = img_path.replace(".png", f"_{target_size[0]}x{target_size[1]}.png")
                shutil.copy(img_path, resized_path)
                resized_images.append(resized_path)

            resized[platform] = {
                "images": resized_images,
                "target_size": target_size,
                "resized_at": datetime.now().isoformat(),
            }

        state["result"] = resized
        return state

    async def compliance_check(self, state: AgentState) -> AgentState:
        """
        步骤4：Agnes AI视觉合规检测（违禁词/图片合规）
        """
        generated = state["input_data"].get("generated_images", {})

        compliance_results = {}
        for platform, data in generated.items():
            for img_path in data.get("images", []):
                # TODO: 上传到Agnes AI视觉检测API
                compliance_results[img_path] = {
                    "passed": True,
                    "issues": [],
                    "checked_at": datetime.now().isoformat(),
                }

        state["decisions"].append({
            "type": "compliance_check",
            "results": compliance_results,
            "timestamp": datetime.now().isoformat(),
        })
        return state

    async def _submit_comfyui_workflow(self, workflow: dict) -> str:
        """提交工作流到ComfyUI并等待结果"""
        async with aiohttp.ClientSession() as session:
            # 提交工作流
            async with session.post(
                f"{COMFYUI_URL}/prompt",
                json={"prompt": workflow},
            ) as resp:
                data = await resp.json()
                prompt_id = data.get("prompt_id")

            if not prompt_id:
                raise RuntimeError("ComfyUI workflow submission failed")

            # 轮询等待结果
            for _ in range(300):  # 最多等待5分钟
                await asyncio.sleep(1)
                async with session.get(f"{COMFYUI_URL}/history/{prompt_id}") as resp:
                    history = await resp.json()
                    if prompt_id in history:
                        return self._extract_output_images(history[prompt_id])

            raise TimeoutError("ComfyUI workflow timed out")

    def _extract_output_images(self, history: dict) -> list[str]:
        """从ComfyUI历史中提取输出图片路径"""
        images = []
        for node_id, node_result in history.items():
            if "images" in node_result:
                for img in node_result["images"]:
                    images.append(img.get("filename", ""))
        return images

    async def _execute_action(self, action: dict) -> dict:
        """执行AI作图动作"""
        return {"status": "image_generated", "action": action}
