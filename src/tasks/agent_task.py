import json
from typing import Tuple, Union

from tools import GeminiClient, GPTClient
from utils import log
from utils.filesys_utils import txt_load
from utils.common_utils import convert_time_to_segment



class AssignDepartment:
    def __init__(self, config):
        self.name = 'department'
        self.__init_env(config)
        self.system_prompt = txt_load(self._system_prompt_path)
        self.user_prompt_template = txt_load(self._user_prompt_path)
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __init_env(self, config):
        """
        Initialize necessary variables.

        Args:
            config (Config): Configuration for agent tasks.
        """
        self._system_prompt_path = config.department_task.system_prompt
        self._user_prompt_path = config.department_task.user_prompt

    
    @staticmethod
    def postprocessing(text: str) -> str:
        """
        Post-processing method of text output.

        Args:
            text (str): Text input.

        Returns:
            str: Post-processed text output.
        """
        text = text.split()[-1].strip()
        return text


    def __call__(self, agent_test_data: dict, agent_results: dict) -> dict:
        """
        Estimates the most appropriate medical department for each patient using an LLM agent.

        Args:
            agent_test_data (dict): A dictionary containing test data for a single hospital.
                Expected to include:
                    - 'agent_data': List of (ground_truth, test_data) pairs.
                    - 'department': Dictionary of available departments.
            agent_results (dict): Placeholder for compatibility; not used in this method.

        Returns:
            dict: A dictionary with:
                - 'gt': List of ground-truth departments.
                - 'pred': List of predicted departments from the LLM agent.
        """
        agent_data = agent_test_data['agent_data']
        departments = list(agent_test_data['department'].keys())
        options = ''.join([f'{i+1}. {department}\n' for i, department in enumerate(departments)])
        results = {'gt': [], 'pred': []}
        
        for data_pair in agent_data:
            gt, test_data = data_pair
            gt_department = gt['department']
            
            user_prompt = self.user_prompt_template.format(SYMPTOM=test_data['symptom'], OPTIONS=options)
            output = self.client(
                user_prompt,
                system_prompt=self.system_prompt, 
                using_multi_turn=False
            )
            output = AssignDepartment.postprocessing(output)

            results['gt'].append(gt_department)
            results['pred'].append(output)
        
        return results



class AssignSchedule:
    def __init__(self, config):
        self.name = 'schedule'
        self.__init_env(config)
        self.system_prompt = txt_load(self._system_prompt_path)
        self.user_prompt_template = txt_load(self._user_prompt_path)
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __init_env(self, config):
        """
        Initialize necessary variables.

        Args:
            config (Config): Configuration for agent tasks.
        """
        self._system_prompt_path = config.schedule_task.system_prompt
        self._user_prompt_path = config.schedule_task.user_prompt

    
    @staticmethod
    def postprocessing(text: str) -> Union[str, dict]:
        """
        Attempts to parse the given text as JSON. If parsing succeeds, returns a dictionary;
        otherwise, returns the original string.

        Args:
            text (str): The text output to post-process, potentially a JSON-formatted string.

        Returns:
            Union[str, dict]: A dictionary if the text is valid JSON, otherwise the original string.
        """
        try:
            return json.loads(text)
        except:
            return text


    def __extract_departments(self, agent_data: list[Tuple[dict, dict]], agent_results: dict) -> list[str]:
        """
        Extracts the predicted department from agent results.
        If predictions are not available, falls back to using ground truth labels.

        Args:
            agent_data (list[Tuple[dict, dict]]): A list of (ground_truth, test_data) pairs for each patient.
            agent_results (dict): A dictionary that may contain predicted department results under the key 'department'.

        Returns:
            list[str]: A list of departments, either predicted or ground truth.
        """
        try:
            departments = agent_results['department']['pred']
        except:
            log('Predicted departments are not given. Ground truth values will be used.', 'warning')
            departments = [gt['department'] for gt, _ in agent_data]
        
        assert len(departments) == len(agent_data), log('The number of departments does not match the agent data.', 'error')

        return departments
    

    def _sanity_check(self,
                      prediction: Union[str, dict], 
                      patient_condition: dict,
                      doctor_information: dict) -> Tuple[bool, Union[str, dict]]:
        """
        Validates a predicted schedule for a doctor by checking its structure, time validity, 
        duplication with existing schedules, and updates the doctor's schedule if valid.

        Args:
            prediction (Union[str, dict]): The predicted allocation result, either a string (if parsing failed)
                or a dictionary mapping a doctor's name to a schedule with 'start' and 'end' times.
            patient_condition (dict): The conditions including duration, etc.
            doctor_information (dict): Dictionary of doctor data including their existing schedules.
                Each key is a doctor's name, and each value includes a 'schedule' field.

        Returns:
            Tuple[bool, Union[str, dict]]: 
                - A boolean indicating whether the prediction passed all sanity checks.
                - The original prediction (either unchanged or used for debugging/logging if invalid).
        """
        # Check the prediciton format
        if not isinstance(prediction, dict):
            return False, prediction    # Could not be parsed as a dictionary
        elif len(prediction) > 1:
            return False, prediction    # Allocated more than one doctor; cannot determine target
        
        # Check the predicted schedule type and validities
        try:
            doctor_name = list(prediction.keys())[0]
            start = prediction[doctor_name]['start']
            end = prediction[doctor_name]['end']
            fixed_schedules = doctor_information[doctor_name]['schedule']
            assert isinstance(start, float) and isinstance(end, float) \
                and start < end and start >= self._START_HOUR and end <= self._END_HOUR
            assert patient_condition['department'] == doctor_information[doctor_name]['department'] \
                and patient_condition['duration'] == round(end - start, 4)
        except KeyError:
            return False, prediction    # Schedule allocation missing or doctor not found
        except AssertionError:
            return False, prediction    # Invalid schedule times or department

        # Check the duplication of the schedules
        prediction_schedule_segemnts = convert_time_to_segment(self._START_HOUR,
                                                               self._END_HOUR,
                                                               self._TIME_UNIT,
                                                               [start, end])
        fixed_schedule_segments = sum([convert_time_to_segment(self._START_HOUR, 
                                                          self._END_HOUR, 
                                                          self._TIME_UNIT, 
                                                          fs) for fs in fixed_schedules], [])
        
        if len(set(prediction_schedule_segemnts) & set(fixed_schedule_segments)):
            return False, prediction    # Overlaps with an existing schedule
        
        # Finally update schedule of the doctor
        doctor_information[doctor_name]['schedule'].append([start, end])    # In-place logic
        prediction = {
            'patient': patient_condition.get('patient'),
            'attending_physician': doctor_name,
            'department': patient_condition.get('department'),
            'schedule': [start, end]
        }
        return True, prediction
            

    def __call__(self, agent_test_data: dict, agent_results: dict) -> dict:
        """
        This method uses agent test data to prompt an LLM for scheduling decisions, post-processes
        the output, runs sanity checks on predicted schedules, and collects the results for evaluation.

        Args:
            agent_test_data (dict): Dictionary containing test data and metadata for a single hospital.
                Expected keys include:
                    - 'metadata': A dict containing start_hour, end_hour, and interval_hour under 'time'.
                    - 'agent_data': A list of (ground_truth, test_data) pairs.
                    - 'doctor': A dictionary of doctor profiles with department and schedule info.
            agent_results (dict): Optional dictionary containing prior department predictions.
                Used to extract department-level guidance per patient. Can be empty.

        Returns:
            dict: A dictionary with three keys:
                - 'gt': List of ground truth results, each including patient info, attending physician, department, and schedule.
                - 'pred': List of predicted results (either valid dict or fallback string).
                - 'sanity': List of booleans indicating whether each prediction passed sanity checks.
        """
        self._START_HOUR = agent_test_data.get('metadata').get('time').get('start_hour')
        self._END_HOUR = agent_test_data.get('metadata').get('time').get('end_hour')
        self._TIME_UNIT = agent_test_data.get('metadata').get('time').get('interval_hour')
        agent_data = agent_test_data.get('agent_data')
        doctor_information = agent_test_data.get('doctor')
        departments = self.__extract_departments(agent_data, agent_results)
        results = {'gt': [], 'pred': [], 'sanity': []}
        
        for data_pair, department in zip(agent_data, departments):
            gt, test_data = data_pair
            duration = test_data.get('constraint').get('duration')
            doctor_information_str = json.dumps(doctor_information, indent=2)   # String-converted ditionary 

            user_prompt = self.user_prompt_template.format(
                START_HOUR=self._START_HOUR,
                END_HOUR=self._END_HOUR,
                TIME_UNIT=self._TIME_UNIT,
                DEPARTMENT=department,
                DURATION=duration,
                DOCTOR=doctor_information_str
            )
            output = self.client(
                user_prompt,
                system_prompt=self.system_prompt, 
                using_multi_turn=False
            )
            output = AssignSchedule.postprocessing(output)
            status, output = self._sanity_check(
                output, 
                {'patient': test_data.get('patient'), 'department': department, 'duration': duration},
                doctor_information
            )
            
            gt_results = {
                'patient': gt.get('patient'),
                'attending_physician': gt.get('attending_physician'),
                'department': gt.get('department'),
                'schedule': gt.get('schedule').get('time')
            }
            results['gt'].append(gt_results)
            results['pred'].append(output)
            results['sanity'].append(status)
            
        return results



class MakeFHIRResource:
    def __init__(self, config):
        self.name = 'fhir_resource'
        self.__init_env(config)
        self.system_prompt = txt_load(self._system_prompt_path)
        self.user_prompt_template = txt_load(self._user_prompt_path)
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __init_env(self, config):
        self._system_prompt_path = config.fhir_resource_task.system_prompt
        self._user_prompt_path = config.fhir_resource_task.user_prompt


    @staticmethod
    def postprocessing(text: str) -> str:
        text = text.split()[-1].strip()
        return text


    def __call__(self, agent_test_data: dict, agent_results: dict) -> dict:
        agent_data = agent_test_data['agent_data']
        departments = list(agent_test_data['department'].keys())
        options = ''.join([f'{i+1}. {department}\n' for i, department in enumerate(departments)])
        results = {'gt': [], 'pred': []}
        
        for data_pair in agent_data:
            gt, test_data = data_pair
            gt_department = gt['department']
            
            user_prompt = self.user_prompt_template.format(SYMPTOM=test_data['symptom'], OPTIONS=options)
            output = self.client(
                user_prompt,
                system_prompt=self.system_prompt, 
                using_multi_turn=False
            )
            output = AssignDepartment.postprocessing(output)

            results['gt'].append(gt_department)
            results['pred'].append(output)
        
        return results



class MakeFHIRAPI:
    def __init__(self, config):
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __call__(self):
        pass
