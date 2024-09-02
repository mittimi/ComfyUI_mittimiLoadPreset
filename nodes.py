import torch
import toml
#import tomllib
#from tomllib import load, loads
import os
import comfy.sd
import folder_paths
from server import PromptServer
from aiohttp import web


routes = PromptServer.instance.routes
@routes.post('/LoadAndSettingParametersMittimi_path')
async def my_function(request):
    the_data = await request.post()
    LoadAndSettingParametersMittimi01.handle_my_message(the_data)
    LoadAndSettingParametersMittimi02.handle_my_message(the_data)
    return web.json_response({})


my_directory_path = os.path.dirname((os.path.abspath(__file__)))
presets_directory_path = os.path.join(my_directory_path, "presets")
preset_list = [f for f in os.listdir(presets_directory_path) if os.path.isfile(os.path.join(presets_directory_path, f))]
if len(preset_list) > 1: preset_list.sort()
vae_new_list = folder_paths.get_filename_list("vae")
vae_new_list.insert(0,"Use_merged_checkpoints")


class LoadAndSettingParametersMittimi02:
    def __init__(self):
        self.device = comfy.model_management.intermediate_device()
    
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "preset": (preset_list,),
                    "checkpoint": (folder_paths.get_filename_list("checkpoints"),),
                    "ClipNum": ("INT", {"default": -1, "min": -10, "max": -1} ),
                    "vae": (vae_new_list,),
                    "PosPromptA": ("STRING", {"multiline": True}),
                    "PosPromptC": ("STRING", {"multiline": True}),
                    "NegPromptA": ("STRING", {"multiline": True}),
                    "NegPromptC": ("STRING", {"multiline": True}),
                    "Width": ("INT", {"default": 512, "min": 8, "max": 16384}),
                    "Height": ("INT", {"default": 512, "min": 8, "max": 16384}),
                    "BatchSize": ("INT", {"default": 1, "min": 1, "max": 999999}),
                    "Steps": ("INT", {"default": 20, "min": 1, "max": 999999}),
                    "CFG": ("FLOAT", ),
                    "SamplerName": (comfy.samplers.KSampler.SAMPLERS,),
                    "Scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                },
                "hidden": {"node_id": "UNIQUE_ID" }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "CONDITIONING", "CONDITIONING", "LATENT", "INT", "FLOAT", comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS, )
    RETURN_NAMES = ("ckpt", "stop_at_clip_layer", "vae", "positive_prompt", "negative_prompt", "Latent", "Steps", "CFG", "sampler_name", "scheduler", )
    FUNCTION = "loadAndSettingParameters02"
    CATEGORY = "mittimiTools"

    def loadAndSettingParameters02(self, preset, checkpoint, ClipNum, vae, PosPromptA, PosPromptC, NegPromptA, NegPromptC, Width, Height, BatchSize, Steps, CFG, SamplerName, Scheduler, node_id, ):

        ckpt_path = folder_paths.get_full_path("checkpoints", checkpoint)
        out3 = comfy.sd.load_checkpoint_guess_config(ckpt_path, output_vae=True, output_clip=True, embedding_directory=folder_paths.get_folder_paths("embeddings"))
        re_ckpt = out3[0]
        re_vae = out3[2]

        re_clip = out3[1].clone()
        re_clip.clip_layer(ClipNum)

        if (vae != "Use_merged_checkpoints"):
            vae_path = folder_paths.get_full_path("vae", vae)
            sd = comfy.utils.load_torch_file(vae_path)
            re_vae = comfy.sd.VAE(sd=sd)
        
        Latent = torch.zeros([BatchSize, 4, Height // 8, Width // 8], device=self.device)

        postxt = PosPromptA + ", " + PosPromptC
        negtxt = NegPromptA + ", " + NegPromptC
        postokens = re_clip.tokenize(postxt)
        negtokens = re_clip.tokenize(negtxt)
        posoutput = re_clip.encode_from_tokens(postokens, return_pooled=True, return_dict=True)
        negoutput = re_clip.encode_from_tokens(negtokens, return_pooled=True, return_dict=True)
        poscond = posoutput.pop("cond")
        negcond = negoutput.pop("cond")

        return(re_ckpt, re_clip, re_vae, [[poscond, posoutput]], [[negcond, negoutput]], {"samples":Latent}, Steps, CFG, SamplerName, Scheduler, )

    def handle_my_message(d):

        preset_data = ""
        preset_path = os.path.join(presets_directory_path, d['message'])
        with open(preset_path, 'r') as f:
            preset_data = toml.load(f)
        PromptServer.instance.send_sync("my.custom.message", {"message":preset_data, "node":d['node_id']})


class LoadAndSettingParametersMittimi01:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {
                    "preset": (preset_list,),
                    "PosPromptA": ("STRING", {"multiline": True}),
                    "PosPromptC": ("STRING", {"multiline": True}),
                    "NegPromptA": ("STRING", {"multiline": True}),
                    "NegPromptC": ("STRING", {"multiline": True}),
                    "checkpoint_name": (folder_paths.get_filename_list("checkpoints"),),
                    "ClipNum": ("INT", {"default": -1, "min": -10, "max": -1} ),
                    "vae_name": (folder_paths.get_filename_list("vae"),),
                    "Steps": ("INT", ),
                    "CFG": ("FLOAT", ),
                    "SamplerName": (comfy.samplers.KSampler.SAMPLERS,),
                    "Scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                },
                "hidden": {"node_id": "UNIQUE_ID" }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", folder_paths.get_filename_list("checkpoints"), "INT", "VAE", "INT", "FLOAT", comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS, )
    RETURN_NAMES = ("POS A", "POS C", "NEG A", "NEG C", "ckpt_name", "stop_at_clip_layer", "vae", "Steps", "CFG", "sampler_name", "scheduler", )
    FUNCTION = "loadAndSettingParameters01"
    CATEGORY = "mittimiTools"

    def loadAndSettingParameters01(self, preset, PosPromptA, PosPromptC, NegPromptA, NegPromptC, checkpoint_name, ClipNum, vae_name, Steps, CFG, SamplerName, Scheduler, node_id, ):

        vae_path = folder_paths.get_full_path("vae", vae_name)
        sd = comfy.utils.load_torch_file(vae_path)
        vae = comfy.sd.VAE(sd=sd)
        
        return(PosPromptA, PosPromptC, NegPromptA, NegPromptC, checkpoint_name, ClipNum, vae, Steps, CFG, SamplerName, Scheduler, )

    def handle_my_message(d):

        preset_data = ""
        preset_path = os.path.join(presets_directory_path, d['message'])
        with open(preset_path, 'r') as f:
            preset_data = toml.load(f)
        PromptServer.instance.send_sync("my.custom.message", {"message":preset_data, "node":d['node_id']})


class LoadPresetForSettingParametersMittimi01:
    @classmethod
    def INPUT_TYPES(s):
        return {"required": {"preset": (preset_list,),}}
    
    RETURN_TYPES = ("TOMLDATA", )
    RETURN_NAMES = ("preset_data", )
    FUNCTION = "loadPreset"
    CATEGORY = "mittimiTools"

    def loadPreset(self, preset):
        preset_path = os.path.join(presets_directory_path, preset)
        with open(preset_path, 'r') as f:
            d = toml.load(f)
        return (d, )


class SettingParametersMittimi01:
    @classmethod
    def INPUT_TYPES(s):
        return {"optional": {"preset_data": ("TOMLDATA", {})},
                "required": {
                    "PosPromptA": ("STRING", {"multiline": True}),
                    "PosPromptC": ("STRING", {"multiline": True}),
                    "NegPromptA": ("STRING", {"multiline": True}),
                    "NegPromptC": ("STRING", {"multiline": True}),
                    "checkpoint_name": (folder_paths.get_filename_list("checkpoints"),),
                    "ClipNum": ("INT", {"default": -1, "min": -10, "max": -1} ),
                    "vae_name": (folder_paths.get_filename_list("vae"),),
                    "Steps": ("INT", ),
                    "CFG": ("FLOAT", ),
                    "SamplerName": (comfy.samplers.KSampler.SAMPLERS,),
                    "Scheduler": (comfy.samplers.KSampler.SCHEDULERS,),
                },
                "hidden": {"node_id": "UNIQUE_ID" }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", folder_paths.get_filename_list("checkpoints"), "INT", "VAE", "INT", "FLOAT", comfy.samplers.KSampler.SAMPLERS, comfy.samplers.KSampler.SCHEDULERS, )
    RETURN_NAMES = ("POS A", "POS C", "NEG A", "NEG C", "ckpt_name", "stop_at_clip_layer", "vae", "Steps", "CFG", "sampler_name", "scheduler", )
    FUNCTION = "settingParameters01"
    CATEGORY = "mittimiTools"

    def settingParameters01(self, PosPromptA, PosPromptC, NegPromptA, NegPromptC, checkpoint_name, ClipNum, vae_name, Steps, CFG, SamplerName, Scheduler, node_id, preset_data=None):

        if (preset_data != None):

            PromptServer.instance.send_sync("my.custom.message", {"message":preset_data, "node":node_id})

            vae_path = folder_paths.get_full_path("vae", preset_data['VAE'])
            sd = comfy.utils.load_torch_file(vae_path)
            vae = comfy.sd.VAE(sd=sd)

            return(preset_data['PositivePromptA'], preset_data['PositivePromptC'], preset_data['NegativePromptA'], preset_data['NegativePromptC'], preset_data['CheckpointName'], preset_data['ClipSet'], vae, preset_data['Steps'], preset_data['CFG'], preset_data['SamplerName'], preset_data['Scheduler'], )
        
        vae_path = folder_paths.get_full_path("vae", vae_name)
        sd = comfy.utils.load_torch_file(vae_path)
        vae = comfy.sd.VAE(sd=sd)
        
        return(PosPromptA, PosPromptC, NegPromptA, NegPromptC, checkpoint_name, ClipNum, vae, Steps, CFG, SamplerName, Scheduler, )



NODE_CLASS_MAPPINGS = {
    "LoadAndSettingParametersMittimi01": LoadAndSettingParametersMittimi01,
    "LoadAndSettingParametersMittimi02": LoadAndSettingParametersMittimi02,
    "LoadPresetForSettingParametersMittimi01": LoadPresetForSettingParametersMittimi01,
    "SettingParametersMittimi01": SettingParametersMittimi01,    
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadAndSettingParametersMittimi01": "LoadAndSettingParameters01",
    "LoadAndSettingParametersMittimi02": "(testing)LoadAndSettingParameters02",
    "LoadPresetForSettingParametersMittimi01": "LoadPresetForSetting01",
    "SettingParametersMittimi01": "SettingParameters01",    
}