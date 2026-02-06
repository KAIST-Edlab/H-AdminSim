# Hospital Data Synthesis
Here, we introduce how to synthesize hospital data, including basic information about hospitals, departments, doctors, and patients.

&nbsp;

## Synthesizing Guides
### 0. Preliminary
We need to complete the `config/data_synthesis.yaml` file.
```yaml
# Base
seed: 9999

# FHIR server url
fhir_url: http://localhost:8080/fhir    # Optional: set your FHIR server URL here

# Data configs
project: ./synthetic_data/
data_name: hospital_small    # Output path: ./synthetic_data/hospital_small/data
hospital_data:
    hospital_n: 10           # Number of hospitals to synthesize
    start_date:
        min: 2025-03-17      # ISO format: YYYY-MM-DD
        max: 2025-09-21      
    days: 7                  # Simulation period (in days)
    interval_hour: 0.25      # Time unit expressed in hours
    start_hour:              # Possible hospital opening hours
        min: 9
        max: 10
    end_hour:                # Possible hospital closing hours
        min: 18
        max: 19
    department_per_hospital:
        min: 7
        max: 9
    doctor_per_department:
        min: 1
        max: 1
    working_days:                   # Number of days each doctor works during the simulation period
        min: 3
        max: 4
    doctor_capacity_per_hour:
        min: 1
        max: 4
    doctor_has_schedule_prob: 0     # Probability that a doctor has at least one fixed schedule
    schedule_coverage_ratio:        # Proportion of fixed schedules relative to total working hours
        min: 0.4
        max: 0.6
    appointment_coverage_ratio:   # Proportion of appointments scheduled outside fixed schedules
        min: 0.2
        max: 0.5
    preference:
        type: ['asap', 'doctor', 'date']    # Types of patient scheduling preferences
        probs: [0.4, 0.4, 0.2]              # Probability distribution for each preference type
    symptom:
        type: ['simple', 'with_history']    # 'simple' = no referral; 'with_history' = referral case
        probs: [0.7, 0.3]                   # Probability distribution for symptom types
```
>* `project`, `data_name`: The generated data will be saved to the path ${project}/${data_name}. This directory is created automatically, so manual setup is not required.
>* `hospital_n`: Number of hospitals to generate synthetic data for.
>* `start_date`: The possible starting date range (min/max) used to randomly sample the beginning of the simulation period.
>* `days`: Number of days included in the simulation window.
>* `interval_hour`: The default time resolution of schedules. All time-related elements (appointments, schedules, availability blocks) are expressed as multiples of interval_hour.
>* `start_hour`: Possible hospital opening time range (min/max). Actual opening time is sampled per hospital.
>* `end_hour`: Possible hospital closing time range (min/max). Actual closing time is sampled per hospital.
>* `department_per_hospital`: Number of medical departments assigned to each hospital (sampled between min/max).
>* `doctor_per_department`: Number of doctors assigned to each department (sampled between min/max).
>* `working_days`: Number of working days each doctor is assigned within the simulation period (sampled between min/max).
>* `doctor_capacity_per_hour`: Number of patients a doctor can see per hour (sampled between min/max).
>* `doctor_has_schedule_prob`: Probability that a doctor has at least one fixed schedule block (e.g., meeting, break, specialized clinic) independent of patient appointments.
>* `schedule_coverage_ratio`: If a doctor has fixed schedules, the proportion of their total working hours that these fixed schedules occupy.
>* `appointment_coverage_ratio`: Among the doctor’s free hours excluding fixed schedules, the proportion allocated to pre-scheduled patient appointments.
>* `preference`.`type`: Available patient scheduling preference types (asap, doctor, date).
>* `preference`.`probs`: Probability distribution over scheduling preference types.
>* `symptom`.`type`: Symptom categories (simple = no referral, with_history = referral case).
>* `symptom`.`probs`: Probability distribution over symptom types.


&nbsp;

### 1. Data Generation
You can synthesize hospital data using the following command:
```bash
python3 src/run/synthesize_data.py --config config/data_synthesis.yaml

# If you want to check whether the generated data are compatible with the Hospital object, 
# you can use the --sanity_check option.
python3 src/run/synthesize_data.py --config config/data_synthesis.yaml --sanity_check

# If you want to make not only synthetic data but also FHIR-converted data,
# you can use the --convert_to_fhir option.
# Supported resource types:
# > `Practitioner`
# > `PractitionerRole`
# > `Patient`
# > `Schedule`
# > `Slot`
# > `Appointment`
python3 src/run/synthesize_data.py --config config/data_synthesis.yaml --sanity_check --convert_to_fhir
```

&nbsp;