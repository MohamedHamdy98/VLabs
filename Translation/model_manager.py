import os
from TTS.utils.manage import ModelManager
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts
from TTS.utils.generic_utils import get_user_data_dir

class ModelManagerWrapper:
    def __init__(self):
        # Define the model name and path for downloading and loading
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        # Download the model and get the path where it's saved
        self.model_path = self.download_model()
        # Load the model configuration and model itself
        self.config, self.model = self.load_model()

    def download_model(self):
        # Create an instance of ModelManager to manage model downloads
        model_manager = ModelManager()
        # Download the model specified by self.model_name
        model_manager.download_model(self.model_name)
        # Construct the path to where the model is saved
        return os.path.join(get_user_data_dir("tts"), self.model_name.replace("/", "--"))

    def load_model(self):
        # Initialize the configuration object for the XTTS model
        config = XttsConfig()
        # Load the model configuration from the downloaded model's config file
        config.load_json(os.path.join(self.model_path, "config.json"))
        # Initialize the XTTS model using the configuration
        model = Xtts.init_from_config(config)
        # Load the model's checkpoint and vocabulary
        model.load_checkpoint(
            config,
            checkpoint_path=os.path.join(self.model_path, "model.pth"),
            vocab_path=os.path.join(self.model_path, "vocab.json"),
            eval=True,  # Set the model to evaluation mode
            use_deepspeed=True  # Enable DeepSpeed for efficient model training and inference
        )
        # Move the model to GPU if available
        model.cuda()
        # Return the loaded configuration and model
        return config, model
