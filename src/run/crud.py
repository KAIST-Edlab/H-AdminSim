import os
import sys
import random
import numpy as np
from sconf import Config
from argparse import ArgumentParser
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from tools import FHIRManager
from utils import log
from utils.random_utils import random_uuid
from utils.filesys_utils import json_load, get_files


def env_setup(config):
    random.seed(config.seed)
    np.random.seed(config.seed)


def load_config(config_path):
    config = Config(config_path)
    return config


def main(args):
    # Init config
    config = load_config(args.config)
    config.yaml_file = args.config
    
    # Init environment
    env_setup(config)

    # Execute CRUD operation
    fhir_manager = FHIRManager(config)
    
    if args.mode == 'create':
        is_file = os.path.isfile(config.data_path)
        files = [config.data_path] if is_file else get_files(config.data_path, ext='json')
        
        for file in files:
            resource_data = json_load(file)
            resource_type = resource_data.get('resourceType')
            if 'id' not in resource_data:
                resource_data['id'] = random_uuid(args.is_develop)
            
            response = fhir_manager.create(resource_type, resource_data)
            log(f"Created {resource_type} with ID {response.get('id')}")

    elif args.mode == 'delete':
        if not args.id or not args.resource_type:
            log("ID and resource type are required for delete operation", level='error')
            return
        
        response = fhir_manager.delete(args.resource_type, args.id)
        log(f"Deleted {args.resource_type} with ID {args.id}")
    


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-c', '--config', type=str, required=True, help='Path to the configuration file')
    parser.add_argument('-m', '--mode', type=str, required=True, choices=['create', 'read', 'update', 'delete'], help='CRUD operation mode')
    parser.add_argument('-d', '--is_develop', action='store_true', required=False, help='Enable development mode for controlled random UUID generation')
    parser.add_argument('--id', type=str, required=False, help='Resource ID for read, update, or delete operations')
    parser.add_argument('--resource_type', type=str, required=False, help='Resource type for read, update, or delete operations')
    args = parser.parse_args()

    main(args)
