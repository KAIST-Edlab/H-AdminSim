# Agent Simulation
We introduce how to test the capabilities required of agents in a hospital booking system.
To begin, you should first build the agent test data by following [this guideline 2.2](./3_data_synthesis.md).
<br><br>We support [Gemini-based LLMs](https://ai.google.dev/gemini-api/docs/models) and [GPT-based LLMs](https://platform.openai.com/docs/pricing).

&nbsp;

## Agent Simulation Guides
### 0. Preliminary
We need to complete the `config/agent_test.yaml` file.
```yaml
# Base
seed: 9999

# LLM model
supervisor_model: gpt-5-nano
task_model: gpt-5-nano
vllm_url: http://0.0.0.0:8000     # Used only when using vllm.

# Agent test data and converted FHIR data folder
agent_test_data: hospital_data/primary/agent_data
fhir_url: http://localhost:8080/fhir
integration_with_fhir: False

# Hospital environment
booking_days_before_simulation: 3       # Number of days before the simulation date when appointment booking can start
fhir_max_connection_retries: 5          # Maximum number of retry attempts when retrieving data from the FHIR server
schedule_cancellation_prob: 0.05
request_early_schedule_prob: 0.1
intake_max_inference: 5

# Prompt paths
outpatient_intake:
    use_supervisor: False
    staff_task_user_prompt: assets/prompts/intake_staff_task_user.txt
    supervisor_system_prompt: assets/prompts/intake_supervisor_system.txt
    supervisor_user_prompt: assets/prompts/intake_supervisor_user.txt
schedule_task:
    scheduling_strategy: llm   # ['llm', 'tool_calling', 'rule'], If you set 'tool_calling' or 'rule', use_supervisor will be ignored.
    use_supervisor: False
    max_feedback_number: 5
    supervisor_system_prompt: assets/prompts/schedule_supervisor_system.txt
    supervisor_user_prompt: assets/prompts/schedule_supervisor_user.txt
    task_system_prompt: assets/prompts/schedule_task_system.txt
    task_user_prompt: assets/prompts/schedule_task_user.txt
    tool_calling_prompt: assets/prompts/schedule_tool_calling_system.txt
```
> * `seed`: Random seed used for reproducibility.
> * `supervisor_model`: LLM model used for the supervisor agent.
> * `task_model`: LLM model used for the task-performing agent (intake or scheduling).
> * `vllm_url`: URL for vLLM inference; required only when using Hugging Face models.
> * `agent_test_data`: Path to the pre-built agent test data folder.
> * `fhir_url`: The base URL of the FHIR server.
> * `integration_with_fhir`: Whether to integrate with the FHIR server during simulation.
> * `booking_days_before_simulation`: Number of days prior to the simulation date when appointment booking can start.
> * `fhir_max_connection_retries`: Maximum number of retry attempts when connecting to the FHIR server.
> * `schedule_cancellation_prob`: Probability that a scheduled appointment is cancelled.
> * `request_early_schedule_prob`: Probability that a patient requests an earlier appointment.
> * `intake_max_inference`: Maximum number dialogue rounds (e.g., 5 rounds == 10 turns)
> * `outpatient_intake`.`use_supervisor`: Whether to use a supervisor agent for intake tasks.
> * `outpatient_intake`.`staff_task_user_prompt`: Path to the staff-task user prompt template for intake.
> * `outpatient_intake`.`supervisor_system_prompt`: Path to the supervisor system prompt for intake.
> * `outpatient_intake`.`supervisor_user_prompt`: Path to the supervisor user prompt for intake.
> * `schedule_task`.`scheduling_strategy`: Strategy for scheduling ('llm', 'tool_calling', or 'rule').
> * `schedule_task`.`use_supervisor`: Whether to use a supervisor agent for scheduling tasks.
> * `schedule_task`.`max_feedback_number`: Maximum number of supervisor feedback iterations during scheduling.
> * `schedule_task`.`supervisor_system_prompt`: Path to the supervisor system prompt for scheduling.
> * `schedule_task`.`supervisor_user_prompt`: Path to the supervisor user prompt for scheduling.
> * `schedule_task`.`task_system_prompt`: Path to the task system prompt for scheduling.
> * `schedule_task`.`task_user_prompt`: Path to the task user prompt for scheduling.
> * `schedule_task`.`tool_calling_prompt`: Path to the tool-calling system prompt for scheduling.


&nbsp;


#### 0.1 Agent Models
You can use three types of models:
* *gemini-\**: If you set the model to a Gemini LLM, you must have your own GCP API key in the `.env` file, with the name `GOOGLE_API_KEY`. The code will automatically communicate with GCP.
* *gpt-\**: If you set the model to a GPT LLM, you must have your own OpenAI API key in the `.env` file, with the name `OPENAI_API_KEY`. The code will automatically use the OpenAI chat format.
* *Otherwise* (e.g. `meta-llama/Llama-3.1-8B-Instruct`): You must serve the model you chose via the vLLM framework. You must have your own HuggingFace token in the `.env` file, with the name `HF_TOKEN`.

For the *otherwise* case, you can serve the model using the vLLM with the below command:
```bash
sh ./run_vllm_docker.sh 
```

&nbsp;

#### 0.2 FHIR Resources
If `integration_with_fhir = True` is set in the configuration, you must add the following FHIR resources in sequence before starting the agent simulation.
If these FHIR resources are not created in the correct order, errors may occur due to reference relationships.
For instructions on how to create FHIR resources, please refer to [here](2_fhir_crud.md).
* `Practitioner`
* `PractitionerRole`
* `Schedule`
* `Slot`


&nbsp;


### 1. Agent Tasks Execution
#### 1.1 Overview
In this framework, we evaluate whether an agent can successfully perform the core administrative tasks that constitute the outpatient booking workflow in a hospital setting. These tasks include:
> 1. `intake`: Collecting key patient information and assigning the appropriate medical department based on the patient's symptoms.
> 2. `schedule`: Based on the assigned department, selecting an attending physician and scheduling an appointment according to physician availability and the required patient's preferences.


<br>These tasks form a **sequential administrative pipeline**. For example, if the agent fails to determine the correct `department` during intake, the scheduling task cannot be completed appropriately.

Accordingly, this framework supports both individual capability evaluation and end-to-end assessment of the agent’s ability to perform the entire administrative workflow.
When evaluating `schedule` independently, we assume that the `intake` output is correct.
In contrast, during sequential evaluation, the output of each task directly influences subsequent steps, reflecting real-world administrative dependencies.

&nbsp;

#### 1.2 Execution
You can execute the agent tasks using the below commands:
```bash
# Simulating only the `intake` task
python3 -u src/run/agent_simulate.py --config config/agent_simulate.yaml --type intake --output_dir ${SYNTHETIC_DATA_FOLDER}/agent_results

# Simulating all administrative tasks (intake → scheduling)
python3 -u src/run/agent_simulate.py --config config/agent_simulate.yaml --type intake schedule --output_dir ${SYNTHETIC_DATA_FOLDER}/agent_results
```

&nbsp;

#### 1.3 Evaluation
You can evaluate the agent task results using the below command:
```bash
python3 -u src/run/evaluate.py --path ${SYNTHETIC_DATA_FOLDER}/agent_results --type task feedback department rounds
```

&nbsp;