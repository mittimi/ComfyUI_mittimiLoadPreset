import toml
# import tomllib
# from tomllib import load, loads
import os
import comfy.sd
import folder_paths
from server import PromptServer
from aiohttp import web


routes = PromptServer.instance.routes
@routes.post('/LoadAndSettingParametersMittimi01_path')
async def my_function(request):
    the_data = await request.post()
    LoadAndSettingParametersMittimi01.handle_my_message(the_data)
    return web.json_response({})


my_directory_path = os.path.dirname((os.path.abspath(__file__)))
presets_directory_path = os.path.join(my_directory_path, "presets")
preset_list = [f for f in os.listdir(presets_directory_path) if os.path.isfile(os.path.join(presets_directory_path, f))]
if len(preset_list) > 1: preset_list.sort()


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

        if d['message'] == "SaveAsNewFile":
            filename = "" #filedialog.asksaveasfilename(filetypes=["toml"],)

        else:
            preset_data = ""
            preset_path = os.path.join(presets_directory_path, d['message'])
            # with open(preset_path, mode='rb') as f:
            #     preset_data = tomllib.load(f)
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
        # with open(preset_path, mode='rb') as f:
        #     d = tomllib.load(f)
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
    "LoadPresetForSettingParametersMittimi01": LoadPresetForSettingParametersMittimi01,
    "SettingParametersMittimi01": SettingParametersMittimi01,    
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoadAndSettingParametersMittimi01": "LoadAndSettingParameters01",
    "LoadPresetForSettingParametersMittimi01": "LoadPresetForSetting01",
    "SettingParametersMittimi01": "SettingParameters01",    
}