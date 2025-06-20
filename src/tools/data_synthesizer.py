import random
import numpy as np
from typing import Optional, Tuple

import registry
from registry import Hospital
from utils import Information
from utils.filesys_utils import txt_load
from utils.common_utils import padded_int, to_dict
from utils.random_utils import generate_random_names



class DataSynthesizer:
    def __init__(self, config):
        self._config = config

    
    def synthesize(self):
        hospitals = self.make_hospital(self._config.hospital_data.hospital_n)
        for hospital in hospitals:
            metadata, hospital_obj = self.define_hospital_info(self._config, hospital)
    

    # def build_data(self, metadata: Information, hospital_obj: Hospital) -> dict:
    #     # """
    #     # Build the data structure for the hospital based on the metadata and hospital object.

    #     # Args:
    #     #     metadata (Information): Metadata about the hospital.
    #     #     hospital_obj (Hospital): Hospital object containing its structure.

    #     # Returns:
    #     #     dict: A dictionary representation of the hospital data.
    #     # """
    #     for department_obj in hospital_obj.department:
    #         doctor = []
    #         department = department_obj.name
    #         for doctor_obj in department_obj.doctor:
    #             doctor.append(doctor_obj.name)


        

            
    def define_hospital_info(self, config, hospital_name: str) -> Tuple[Information, Hospital]:
        """
        Define the metadata and structure of a hospital, including its departments and doctors.

        Args:
            config (Config): Configuration object containing hospital data settings.
            hospital_name (str): Name of the hospital to be defined.

        Returns:
            Tuple[Information, Hospital]: Metadata about the hospital and a Hospital object containing its structure.
        """
        # Define hosptial metadata
        hospital_obj = Hospital(hospital_name)
        interval_hour = config.hospital_data.interval_hour
        start_hour = random.choice(
            np.arange(
                config.hospital_data.start_hour.min,
                config.hospital_data.start_hour.max+interval_hour,  # Ensure the end hour is inclusive
                interval_hour
            )
        )
        end_hour = random.choice(
            np.arange(
                config.hospital_data.end_hour.min,
                config.hospital_data.end_hour.max+interval_hour,  # Ensure the end hour is inclusive
                interval_hour
            )
        )
        department_n = random.randint(
            config.hospital_data.department_per_hospital.min,
            config.hospital_data.department_per_hospital.max
        )
        doctor_n = 0
        
        # Define hospital department and doctoral information
        departments = self.make_departments(department_n)
        for department in departments:
            # Add department to hospital
            department_obj = hospital_obj.add_department(department)
            
            # Add doctors to department
            doctors = self.make_doctors(
                random.randint(
                    config.hospital_data.doctor_per_department.min,
                    config.hospital_data.doctor_per_department.max
                )
            )
            for doctor in doctors:
                department_obj.add_doctor(doctor)
            doctor_n += len(doctors)

        # Update meatdata
        metadata = Information(
            hospital_name=hospital_name,
            department_num=department_n,
            docotor_num=doctor_n,
            time=Information(
                start_hour=start_hour,
                end_hour=end_hour,
                inteveal_hour=interval_hour
            )
        )
        
        return metadata, hospital_obj


    def make_hospital(self, hospital_n: int, file_path: Optional[str] = None) -> list[str]:
        """
        Generate a list of hospital names based on the number of hospitals.
        
        Args:
            hospital_n (int): Number of hospitals to generate.
            file_path (Optional[str]): Path to a file containing hospital names. If provided, it will be used to load names.
        
        Returns:
            list[str]: List of hospital names in the format "Hospital 001", "Hospital 002", etc.
        """
        if file_path:
            if registry.HOSPITALS is None:
                registry.HOSPITALS = [word.capitalize() for word in txt_load(file_path).split('\n')]
            return [f"{random.choice(registry.HOSPITALS)}" for _ in range(hospital_n)]
        return [f"hospital_{padded_int(i+1)}" for i in range(hospital_n)]

    
    def make_departments(self, department_n: int, file_path: Optional[str] = None) -> list[str]:
        """
        Generate a list of department names based on the number of departments.
        
        Args:
            department_n (int): Number of departments to generate.
            file_path (Optional[str]): Path to a file containing department names. If provided, it will be used to load names.
        
        Returns:
            list[str]: List of department names in the format "Department 001", "Department 002", etc.
        """
        if file_path:
            if registry.DEPARTMENTS is None:
                registry.DEPARTMENTS = [word.capitalize() for word in txt_load(file_path).split('\n')]
            return [f"{random.choice(registry.DEPARTMENTS)}" for _ in range(department_n)]
        return [f"department_{padded_int(i+1)}" for i in range(department_n)]
    

    def make_doctors(self,
                     doctor_n: int,
                     first_name_file_path: str = 'asset/names/firstname.txt',
                     last_name_file_path: str = 'asset/names/lastname.txt') -> list[str]:
        """
        Generate a list of doctor names based on the number of doctors.
        
        Args:
            doctor_n (int): Number of doctors to generate.
            first_name_file_path (str): Path to a file containing first names. Defaults to 'asset/names/firstname.txt'.
            last_name_file_path (str): Path to a file containing last names. Defaults to 'asset/names/lastname.txt'.
        
        Returns:
            list[str]: List of doctor names in the format "Doctor 001", "Doctor 002", etc.
        """
        return [f'Dr. {name}' for name in generate_random_names(doctor_n, first_name_file_path, last_name_file_path)]
