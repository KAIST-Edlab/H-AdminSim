from tools import GeminiClient, GPTClient
from utils.filesys_utils import txt_load



class AssignDepartment:
    def __init__(self, config):
        self.name = 'department'
        self.__init_env(config)
        self.system_prompt = txt_load(self._system_prompt_path)
        self.user_prompt_template = txt_load(self._user_prompt_path)
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __init_env(self, config):
        self._system_prompt_path = config.department_taks.system_prompt
        self._user_prompt_path = config.department_taks.user_prompt

    
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



class AssignSchedule:
    def __init__(self, config):
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __call__(self):
        pass



class MakeFHIRResource:
    def __init__(self, config):
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __call__(self):
        pass



class MakeFHIRAPI:
    def __init__(self, config):
        self.client = GeminiClient(config.model) if 'gemini' in config.model.lower() else GPTClient(config.model)


    def __call__(self):
        pass
