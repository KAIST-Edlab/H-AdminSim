import os
import random
import numpy as np
from sconf import Config
from pathlib import Path
from importlib import resources
from typing import Optional, Union

from h_adminsim.tools import DataSynthesizer, DataConverter, AgentDataBuilder
from h_adminsim.utils import Information, log



class DataGenerator:
    def __init__(self,
                 care_level: str = 'primary',
                 config: Optional[Union[str, Config]] = None):
        
        # Initialize
        self.config = self.load_config(care_level, config)
        self.__env_setup(config)
        self.save_dir = Path(os.path.join(config.project, config.name))
        self.data_synthesizer = DataSynthesizer(config)

        
    def load_config(self, care_level: str, config: Optional[Union[str, Config]]) -> Config:
        """
        Load a configuration object.

        If `config` is None, a default configuration is loaded based on the given
        `care_level`. If `config` is a string, it is treated as a file path and
        loaded as a Config object. If a Config instance is provided, it is returned
        as-is.

        Args:
            care_level (str): Care level used to select the default config.
            config (Optional[Union[str, Config]]): A file path or Config instance.

        Returns:
            Config: A fully initialized Config object.

        Raises:
            TypeError: If `config` is not None, str, or Config.
        """
        # Case 1: config is None -> load built-in config based on care_level
        if config is None:
            log(f"No config provided; using default {care_level} config.", "warning")
            default_path = str(resources.files("h_adminsim.assets.configs").joinpath(f"data4{care_level}.yaml"))
            return Config(default_path)

        # Case 2: config is a string path
        if isinstance(config, str):
            config_inst = Config(config)
            config_inst.yaml_file = config
            return config_inst

        # Case 3: config is already a Config object
        if isinstance(config, Config):
            return config

        # Otherwise error
        raise TypeError(
            log(f"Invalid config: expected None, str, or Config, got {type(config).__name__}", "error")
        )


    def __env_setup(config: Config) -> None:
        """
        Initialize environment-level random seeds using the given configuration.

        Args:
            config (Config): Configuration containing the seed value.
        """
        random.seed(config.seed)
        np.random.seed(config.seed)
    

    def build(self, 
              sanity_check: bool = True,
              convert_to_fhir: bool = False,
              build_agent_data: bool = True):
        # Data generator
        try:
            data, hospital_obj = self.data_synthesizer.synthesize(sanity_check=sanity_check)
            log(f"Data synthesis completed successfully", color=True)
        except Exception as e:
            log("Data synthesis failed.", level="error")
            raise e
        
        # FHIR conversion
        if convert_to_fhir:
            all_resource_list = None
            converter = DataConverter(self.config)
            try:
                all_resource_list = converter(self.save_dir / 'fhir_data', sanity_check)
                log(f"Data FHIR conversion completed successfully", color=True)
            except Exception as e:
                log("Data FHIR conversion failed.", level='error')
                raise e
            
        # Build data for agent simulation
        if build_agent_data:
            agent_data_list = None
            builder = AgentDataBuilder(self.config)
            try:
                agent_data_list = builder(self.save_dir / 'agent_data')
                log(f"Agent data generation completed successfully", color=True)
            except Exception as e:
                log("Agent data generation failed.", level='error')
                raise e
        
        output = Information(
            data=data,
            fhir_data=all_resource_list,
            agent_data=agent_data_list
        )
        
        return output
    