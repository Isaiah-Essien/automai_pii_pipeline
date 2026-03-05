#!/usr/bin/env python3
"""
Comprehensive Name PHI Generator
==================================

Generates 10,000 rows of name PHI data using 200 unique sentence templates
across 4 categories: Patient as Subject, Third-Party Narrator, Family/Social Context,
and Administrative/Institutional Context.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class ComprehensiveNamePHIGenerator:
    """Generator for comprehensive name-focused PHI data with 200 templates."""

    def __init__(self, config_path: str = "../phi_configs/PHI_name.json", seed: Optional[int] = None):
        """Initialize with configuration file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        if seed:
            random.seed(seed)
        
        self.first_names = self.config['african_first_names']
        self.last_names = self.config['african_last_names']
        
        # Supporting data for placeholders
        self.ages = list(range(1, 91))
        self.genders = ["male", "female"]
        self.times = [f"{h:02d}:{m:02d}" for h in range(24) for m in [0, 15, 30, 45]]
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        self.conditions = [
            "malaria", "typhoid", "tuberculosis", "hypertension", "diabetes",
            "pneumonia", "asthma", "HIV", "hepatitis B", "meningitis",
            "cholera", "dengue fever", "yellow fever", "ebola", "measles",
            "chickenpox", "diarrhea", "dysentery", "anemia", "sickle cell disease",
            "heart disease", "stroke", "cancer", "kidney disease", "liver disease",
            "arthritis", "epilepsy", "depression", "anxiety", "schizophrenia",
            "malnutrition", "schistosomiasis", "trypanosomiasis", "leishmaniasis",
            "onchocerciasis", "lymphatic filariasis", "chronic obstructive pulmonary disease"
        ]
        
        self.medications = [
            "Paracetamol", "Ibuprofen", "Amoxicillin", "Ciprofloxacin", "Metronidazole",
            "Artemether", "Lumefantrine", "Quinine", "Chloroquine", "Malarone",
            "Metformin", "Glibenclamide", "Insulin", "Atenolol", "Amlodipine",
            "Lisinopril", "Hydrochlorothiazide", "Salbutamol", "Prednisolone",
            "Antiretroviral therapy", "Lamivudine", "Zidovudine", "Nevirapine",
            "Rifampicin", "Isoniazid", "Pyrazinamide", "Ethambutol", "Streptomycin",
            "Diazepam", "Carbamazepine", "Phenobarbital", "Fluoxetine", "Amitriptyline"
        ]
        
        self.procedures = [
            "caesarean section", "appendectomy", "hernia repair", "surgery",
            "biopsy", "endoscopy", "colonoscopy", "dialysis", "blood transfusion",
            "vaccination", "immunisation", "surgery", "operation", "transplant",
            "chemotherapy", "radiotherapy", "physical therapy", "occupational therapy",
            "coronary bypass", "angioplasty", "cataract surgery", "tonsillectomy",
            "mastectomy", "hysterectomy", "prostatectomy", "cholecystectomy"
        ]
        
        self.tests = [
            "blood test", "urine test", "stool test", "X-ray", "CT scan",
            "MRI scan", "ultrasound", "ECG", "EEG", "biopsy",
            "HIV test", "malaria test", "tuberculosis test", "pregnancy test",
            "glucose test", "cholesterol test", "liver function test",
            "kidney function test", "blood culture", "sputum culture",
            "complete blood count", "urinalysis", "chest X-ray", "abdominal ultrasound"
        ]
        
        self.facilities = [
            "Kenyatta National Hospital", "Chris Hani Baragwanath Hospital",
            "Lagos University Teaching Hospital", "Groote Schuur Hospital",
            "Addis Ababa University Medical Center", "Muhimbili National Hospital",
            "Korle-Bu Teaching Hospital", "Charlotte Maxeke Hospital",
            "University College Hospital Ibadan", "Medina Clinic",
            "St. Mary's Hospital", "Central Hospital", "District Hospital",
            "Regional Referral Hospital", "Community Health Center",
            "Primary Health Care Clinic", "Aga Khan Hospital", "Nairobi Hospital"
        ]
        
        self.streets = [
            "Uhuru Street", "Independence Avenue", "Kaunda Road", "Mandela Boulevard",
            "Nkrumah Drive", "Lumumba Street", "Haile Selassie Avenue", "Kenyatta Road",
            "Obote Street", "Nyerere Road", "Azikiwe Street", "Sankara Avenue",
            "Machel Drive", "Sobukwe Street", "Biko Road", "Tambo Avenue",
            "Marina Road", "Victoria Island", "Lekki Phase 1", "Allen Avenue",
            "Opebi Road", "Ademola Adetokunbo Street", "Murtala Mohammed Way"
        ]
        
        self.wards = [
            "Ward 1", "Ward 2", "Ward 3", "Ward A", "Ward B", "Ward C",
            "ICU", "Paediatric Ward", "Maternity Ward", "Surgical Ward",
            "Medical Ward", "Orthopaedic Ward", "Isolation Ward", "HDU"
        ]
        
        self.departments = [
            "Emergency", "Surgery", "Medicine", "Paediatrics", "Obstetrics",
            "Gynaecology", "Orthopaedics", "Ophthalmology", "ENT", "Psychiatry",
            "Radiology", "Laboratory", "Pharmacy", "Oncology", "Cardiology"
        ]
        
        self.programs = [
            "TB treatment", "HIV care", "Maternal health", "Child health",
            "Immunisation", "Malaria control", "Diabetes management",
            "Hypertension management", "Mental health", "Palliative care"
        ]
        
        self.occupations = [
            "teacher", "farmer", "trader", "driver", "nurse", "engineer",
            "accountant", "lawyer", "doctor", "mechanic", "tailor", "cook",
            "security guard", "cleaner", "student", "businessman", "civil servant"
        ]
        
        # All 200 templates organized by category
        self.templates = self._get_all_templates()
    
    def _get_all_templates(self) -> List[str]:
        """Return all 200 templates across 4 categories."""
        return [
            # CATEGORY A — PATIENT AS SUBJECT (1-50)
            "[First] [Last] is a [age]-year-old patient admitted on [date] with complaints of [condition].",
            "[First] [Middle] [Last] was referred to this facility by Dr. [First] [Last] on [date].",
            "[First] [Last], aged [age], presented at the emergency unit with acute [condition].",
            "[First] [Middle] [Last] has been under the care of Dr. [First] [Last] since [date].",
            "[First] [Last] (ID: [ID]) was discharged on [date] following treatment for [condition].",
            "[First] [Last], a [age]-year-old [gender], tested positive for [condition] on [date].",
            "[First] [Middle] [Last] is currently scheduled for surgery with Dr. [First] [Last].",
            "[First] [Last] has a family history of [condition]; her mother, [First] [Last], was diagnosed at [age].",
            "[First] [Last] (DOB: [date]) is allergic to [medication] and has been prescribed [medication] instead.",
            "[First] [Last] was seen at the outpatient clinic on [date] and diagnosed with [condition].",
            "[First] [Middle] [Last], medical record [ID], is awaiting results for a [test] conducted on [date].",
            "[First] [Last] has been on [medication] since [date] as prescribed by Dr. [First] [Last].",
            "[First] [Last], aged [age], reported recurring symptoms of [condition] during her visit on [date].",
            "[First] [Middle] [Last] was brought in by her husband, [First] [Last], on [date].",
            "[First] [Last] (Patient ID: [ID]) is due for a follow-up with Dr. [First] [Last] on [date].",
            "[First] [Last] underwent a successful [procedure] performed by Dr. [First] [Last].",
            "[First] [Middle] [Last], [age] years old, lives at [Street] and can be reached at [phone].",
            "[First] [Last] is a [age]-year-old male presenting with symptoms consistent with [condition].",
            "[First] [Last] has been diagnosed with [condition] and referred to the [department] ward.",
            "[First] [Middle] [Last] signed the consent form on [date] prior to the [procedure].",
            "[First] [Last], born on [date], has been enrolled in the [program] program since [date].",
            "[First] [Last] reported to Nurse [First] [Last] that she had not taken her [medication] since [date].",
            "[First] [Middle] [Last] is a known diabetic and was admitted via the emergency unit on [date].",
            "[First] [Last]'s medical report, compiled by Dr. [First] [Last], indicates [condition].",
            "[First] [Last] (Reg. No: [ID]) had a consultation with Dr. [First] [Last] regarding [condition].",
            "[First] [Last], age [age], is currently in Ward [ward] under observation for [condition].",
            "[First] [Middle] [Last] transferred from [facility] to this hospital on [date] with records attached.",
            "[First] [Last] has been on dialysis since [date] and is under Dr. [First] [Last]'s supervision.",
            "[First] [Last], a [age]-year-old mother of [number], was diagnosed with [condition] postpartum.",
            "[First] [Middle] [Last] (DOB: [date]) had her [test] results reviewed by Dr. [First] [Last].",
            "[First] [Last] requires immediate attention; please contact next of kin, [First] [Last], at [phone].",
            "[First] [Last] was assisted by Nurse [First] [Last] during the procedure on [date].",
            "[First] [Middle] [Last] has not responded to [medication] and has been escalated to Dr. [First] [Last].",
            "[First] [Last], residing at [Street], visited the clinic on [date] for a routine [test].",
            "[First] [Last]'s prescription was updated by Dr. [First] [Last] on [date] to include [medication].",
            "[First] [Middle] [Last] is the primary patient in case file [ID], opened on [date].",
            "[First] [Last], [age] years old, is recovering in Ward [ward] following her [procedure] on [date].",
            "[First] [Last] has been flagged for a second opinion; Dr. [First] [Last] will review on [date].",
            "[First] [Middle] [Last] (ID: [ID]) is enrolled in the [condition] management program.",
            "[First] [Last]'s emergency contact is her sister, [First] [Last], reachable at [phone].",
            "[First] [Last], DOB [date], was seen by Dr. [First] [Last] for a follow-up on [condition].",
            "[First] [Middle] [Last] has chronic [condition] and attends monthly reviews with Dr. [First] [Last].",
            "[First] [Last] was admitted at [time] on [date]; attending physician is Dr. [First] [Last].",
            "[First] [Last], residing on [Street], has been on the transplant waiting list since [date].",
            "[First] [Middle] [Last] presented a prior diagnosis of [condition] from Dr. [First] [Last] of [facility].",
            "[First] [Last] is a [age]-year-old with no known allergies, currently taking [medication].",
            "[First] [Last]'s lab results, processed on [date], were forwarded to Dr. [First] [Last].",
            "[First] [Middle] [Last] was administered [medication] by Nurse [First] [Last] at [time] on [date].",
            "[First] [Last], case no. [ID], was stabilised on [date] and moved out of intensive care.",
            "[First] [Last], a [age]-year-old [occupation], was referred by Dr. [First] [Last] for [procedure].",
            
            # CATEGORY B — THIRD-PARTY NARRATOR (51-100)
            "The patient, [First] [Last], arrived at [time] complaining of severe [condition].",
            "This report concerns [First] [Middle] [Last], admitted under Dr. [First] [Last] on [date].",
            "Medical record [ID] belongs to [First] [Last], a [age]-year-old [gender] from [Street].",
            "The following test results are for [First] [Middle] [Last], processed by Dr. [First] [Last].",
            "As per Dr. [First] [Last]'s notes, [First] [Last] has shown improvement since [date].",
            "These discharge papers are prepared for [First] [Middle] [Last] (DOB: [date]).",
            "The attending nurse, [First] [Last], documented that patient [First] [Last] refused [medication].",
            "Consent for the procedure was obtained from [First] [Last] on [date] by Dr. [First] [Last].",
            "The test request for [First] [Last] was submitted by Dr. [First] [Last] on [date].",
            "Surgical notes from Dr. [First] [Last] confirm that [First] [Middle] [Last] is stable.",
            "The prescription for [First] [Last] (ID: [ID]) was authorised by Dr. [First] [Last].",
            "As documented by Nurse [First] [Last], patient [First] [Middle] [Last] was given [medication] at [time].",
            "The referral letter for [First] [Last] has been signed by Dr. [First] [Last] and sent to [facility].",
            "Ward notes indicate that [First] [Last] experienced complications on [date]; Dr. [First] [Last] was notified.",
            "Case file [ID] for [First] [Middle] [Last] has been updated by Dr. [First] [Last] as of [date].",
            "The MRI results for [First] [Last], conducted on [date], have been reviewed by Dr. [First] [Last].",
            "Blood work for [First] [Middle] [Last] (DOB: [date]) was collected by Nurse [First] [Last].",
            "The specialist report for [First] [Last] was submitted by Dr. [First] [Last] on [date].",
            "Per the triage log, [First] [Last] was seen at [time] and assigned to Dr. [First] [Last].",
            "This letter serves as confirmation that [First] [Middle] [Last] attended their appointment on [date].",
            "Pharmacy records show that [First] [Last] collected [medication] on [date] from Pharmacist [First] [Last].",
            "The ultrasound report for [First] [Last], aged [age], was prepared by Dr. [First] [Last].",
            "Clinical observations for [First] [Middle] [Last] (ID: [ID]) were recorded on [date] by Dr. [First] [Last].",
            "The nurse on duty, [First] [Last], flagged patient [First] [Last] for urgent review on [date].",
            "Insurance claim [ID] was filed on behalf of [First] [Middle] [Last] on [date].",
            "These are the post-operative notes for [First] [Last], authored by Dr. [First] [Last].",
            "The anesthesia report for [First] [Last]'s procedure on [date] was completed by Dr. [First] [Last].",
            "Vital signs for [First] [Middle] [Last] were recorded by Nurse [First] [Last] at [time].",
            "The admission form for [First] [Last] (DOB: [date]) was processed by receptionist [First] [Last].",
            "Dietary requirements for patient [First] [Middle] [Last] were noted by Nurse [First] [Last] on [date].",
            "Physical therapy sessions for [First] [Last] are supervised by Dr. [First] [Last] every [day].",
            "The pathology report for [First] [Last], sample collected on [date], is attached.",
            "Emergency contact for [First] [Middle] [Last] is listed as [First] [Last] at [phone].",
            "This notice confirms the transfer of [First] [Last] from Ward [ward] to [facility] on [date].",
            "Dr. [First] [Last] has recommended that [First] [Last] be placed on a [condition] management plan.",
            "The dental records for [First] [Middle] [Last] are filed under case [ID] at [facility].",
            "Immunisation records for [First] [Last] (DOB: [date]) were updated by Nurse [First] [Last].",
            "The second opinion for [First] [Last]'s case was provided by Dr. [First] [Last] of [facility].",
            "Therapy notes for [First] [Middle] [Last] were recorded by counsellor [First] [Last] on [date].",
            "The on-call physician, Dr. [First] [Last], reviewed [First] [Last]'s condition at [time].",
            "Radiology results for [First] [Last] (ID: [ID]) were forwarded to Dr. [First] [Last] on [date].",
            "The gynaecology report for [First] [Last], aged [age], was completed by Dr. [First] [Last].",
            "Nursing hand-over notes mention that [First] [Middle] [Last] had a difficult night on [date].",
            "The paediatric assessment for [First] [Last] was conducted by Dr. [First] [Last] on [date].",
            "Cardiology notes from Dr. [First] [Last] confirm [First] [Middle] [Last] requires ongoing monitoring.",
            "This certificate of fitness for [First] [Last] was issued by Dr. [First] [Last] on [date].",
            "The social worker, [First] [Last], visited [First] [Middle] [Last] in Ward [ward] on [date].",
            "Patient [First] [Last] was reviewed by the multidisciplinary team led by Dr. [First] [Last] on [date].",
            "Nutrition assessment for [First] [Middle] [Last] (ID: [ID]) was carried out by [First] [Last].",
            "Dr. [First] [Last]'s clinical summary for [First] [Last] has been attached to this referral.",
            
            # CATEGORY C — FAMILY / SOCIAL CONTEXT (101-150)
            "[First] [Last]'s daughter, [First] [Middle] [Last], was brought in for a check-up on [date].",
            "The patient's husband, [First] [Last], provided consent on behalf of [First] [Last] on [date].",
            "[First] [Last] accompanied her mother, [First] [Middle] [Last], to the clinic on [date].",
            "The emergency contact, [First] [Last], was notified of [First] [Last]'s condition at [time].",
            "[First] [Last]'s father, [First] [Last], has the same diagnosis of [condition] per family history.",
            "The guardian of [First] [Middle] [Last] is listed as [First] [Last], reachable at [phone].",
            "[First] [Last] is the primary caregiver for her aunt, [First] [Middle] [Last], who has [condition].",
            "The son of the patient, [First] [Last], spoke with Dr. [First] [Last] on [date] regarding care plans.",
            "[First] [Last]'s next of kin, [First] [Middle] [Last], signed the surgical consent on [date].",
            "The patient was brought in by her colleague, [First] [Last], after collapsing at [Street] on [date].",
            "[First] [Last]'s wife, [First] [Last], reported that he had been experiencing [condition] since [date].",
            "The child, [First] [Last], was registered under the parent, [First] [Middle] [Last], on [date].",
            "[First] [Last] disclosed that her sister, [First] [Last], also suffers from [condition].",
            "The patient's brother, [First] [Last], was tested and confirmed negative on [date].",
            "[First] [Middle] [Last] mentioned that her grandmother, [First] [Last], had a history of [condition].",
            "The neighbour, [First] [Last], brought [First] [Last] to the facility after finding him unconscious.",
            "[First] [Last]'s partner, [First] [Last], is listed as the next of kin at [Street].",
            "The mother of the child, [First] [Last], was interviewed by Dr. [First] [Last] on [date].",
            "[First] [Last]'s uncle, [First] [Middle] [Last], serves as legal guardian for medical decisions.",
            "The patient mentioned that her colleague, [First] [Last], had referred her to this facility.",
            "[First] [Last] (ID: [ID]) was accompanied by her teacher, [First] [Last], on [date].",
            "The patient's friend, [First] [Last], was the only contact available on [date].",
            "[First] [Last]'s twin brother, [First] [Last], underwent the same procedure in [date].",
            "The community health worker, [First] [Last], referred [First] [Middle] [Last] on [date].",
            "[First] [Last] is the biological mother of [First] [Last], currently in neonatal care since [date].",
            "The stepfather of the patient, [First] [Last], disputes the treatment plan with Dr. [First] [Last].",
            "[First] [Last]'s employer, [First] [Last] of [facility], submitted the insurance claim on [date].",
            "The midwife, [First] [Last], delivered the baby of [First] [Middle] [Last] on [date].",
            "[First] [Last] is listed as the legal representative for [First] [Last] (ID: [ID]).",
            "The patient's daughter-in-law, [First] [Last], has been managing [First] [Last]'s medication since [date].",
            "[First] [Last] disclosed during intake that her co-wife, [First] [Last], has the same symptoms.",
            "The pastor, [First] [Last], accompanied patient [First] [Middle] [Last] to the appointment on [date].",
            "The foster parent, [First] [Last], submitted medical history for [First] [Last] on [date].",
            "[First] [Last]'s roommate, [First] [Last], at [Street] first noticed the symptoms on [date].",
            "Traditional birth attendant [First] [Last] referred [First] [Middle] [Last] to this facility on [date].",
            "The grandfather of the patient, [First] [Last], is also enrolled at this facility under ID [ID].",
            "[First] [Last]'s cousin, [First] [Middle] [Last], tested positive on [date] and was isolated.",
            "The landlord, [First] [Last], at [Street] contacted emergency services on behalf of [First] [Last].",
            "[First] [Last] reports that her co-worker, [First] [Last], also experienced similar symptoms.",
            "The legal guardian, [First] [Last], collected the prescription for [First] [Middle] [Last] on [date].",
            "[First] [Last] is the biological father of [First] [Last], admitted to the paediatric ward on [date].",
            "The headteacher, [First] [Last], submitted a medical clearance request for [First] [Last] on [date].",
            "[First] [Last]'s sponsor, [First] [Last], has agreed to cover treatment costs as of [date].",
            "The driver, [First] [Last], transported patient [First] [Middle] [Last] to the hospital on [date].",
            "[First] [Last] is the aunt and primary carer of [First] [Last] (DOB: [date]), who has [condition].",
            "The patient's step-mother, [First] [Last], provided her medical history to Dr. [First] [Last].",
            "[First] [Last]'s close friend, [First] [Middle] [Last], accompanied them during the procedure on [date].",
            "The traditional healer, [First] [Last], had previously treated [First] [Last] for [condition].",
            "[First] [Last] reported that her daughter, [First] [Last], who resides at [Street], needs follow-up.",
            "The school nurse, [First] [Last], flagged [First] [Middle] [Last] for urgent medical attention on [date].",
            
            # CATEGORY D — ADMINISTRATIVE / INSTITUTIONAL CONTEXT (151-200)
            "Please update the records for [First] [Last] (ID: [ID]) as per Dr. [First] [Last]'s instructions.",
            "Kindly schedule an appointment for [First] [Middle] [Last] with Dr. [First] [Last] on [date].",
            "The file for [First] [Last], last seen on [date], has been archived by [First] [Last].",
            "Reception has confirmed that [First] [Middle] [Last] checked in at [time] on [date].",
            "The referral for [First] [Last] has been approved and forwarded to Dr. [First] [Last].",
            "Please ensure Dr. [First] [Last] reviews [First] [Last]'s file before the [date] appointment.",
            "The billing statement for [First] [Middle] [Last] (ID: [ID]) has been sent to [phone].",
            "Remind [First] [Last] that her prescription from Dr. [First] [Last] expires on [date].",
            "The medical certificate for [First] [Last] was signed by Dr. [First] [Last] on [date].",
            "Please confirm that [First] [Middle] [Last] received the SMS reminder for [date] at [phone].",
            "The duty roster shows that Nurse [First] [Last] is assigned to [First] [Last] in Ward [ward].",
            "Dr. [First] [Last] has requested imaging for [First] [Last]; please book by [date].",
            "The insurance pre-authorisation for [First] [Middle] [Last] was approved on [date].",
            "[First] [Last]'s appointment with Dr. [First] [Last] has been rescheduled to [date].",
            "The intake form for [First] [Last] (DOB: [date]) was completed by receptionist [First] [Last].",
            "Please note that [First] [Middle] [Last] has outstanding balance [ID] as of [date].",
            "The surgery schedule for [date] lists [First] [Last] under Dr. [First] [Last]'s theatre.",
            "A death certificate for [First] [Last] (DOB: [date]) was issued by Dr. [First] [Last] on [date].",
            "The records department has flagged [First] [Middle] [Last]'s file for update as of [date].",
            "Dr. [First] [Last] has placed a medication hold on [First] [Last]'s account pending review.",
            "The ward transfer form for [First] [Last] was signed by Dr. [First] [Last] on [date].",
            "Please pull the case notes for [First] [Middle] [Last] (ID: [ID]) for the board meeting on [date].",
            "The social welfare assessment for [First] [Last] was completed by [First] [Last] on [date].",
            "Pharmacy has flagged that [First] [Last] has not collected her [medication] since [date].",
            "Kindly inform Dr. [First] [Last] that [First] [Middle] [Last]'s test results are ready.",
            "The occupational health record for [First] [Last] at [facility] was last updated on [date].",
            "This memo confirms that [First] [Last]'s case (ID: [ID]) has been assigned to Dr. [First] [Last].",
            "The feedback form submitted by [First] [Last] on [date] has been forwarded to [First] [Last].",
            "Please dispatch an ambulance to [Street] for [First] [Middle] [Last], DOB [date], at [time].",
            "The NHIF claim for [First] [Last] (ID: [ID]) was submitted by [First] [Last] on [date].",
            "Dr. [First] [Last] will be unavailable on [date]; [First] [Last]'s case has been reassigned.",
            "The antenatal card for [First] [Last], DOB [date], was issued at [facility] on [date].",
            "Please register [First] [Middle] [Last] for the [condition] support group starting [date].",
            "The home visit report for [First] [Last] at [Street] was filed by [First] [Last] on [date].",
            "HR has received the sick leave certificate for [First] [Last] signed by Dr. [First] [Last].",
            "The triage log for [date] shows [First] [Middle] [Last] was assessed by Nurse [First] [Last].",
            "Kindly confirm [First] [Last]'s next of kin details with the contact, [First] [Last], at [phone].",
            "The vaccination card for [First] [Last] (DOB: [date]) was updated by Nurse [First] [Last].",
            "Please ensure [First] [Middle] [Last]'s room in Ward [ward] is prepared before [date].",
            "The outpatient register shows [First] [Last] was attended to by Dr. [First] [Last] on [date].",
            "This invoice is addressed to [First] [Last] for services rendered on [date] at [facility].",
            "The maternity record for [First] [Last] (ID: [ID]) has been filed under Dr. [First] [Last].",
            "Patient satisfaction survey submitted by [First] [Last] on [date] references Dr. [First] [Last].",
            "The health screening results for [First] [Middle] [Last] at [Street] were recorded on [date].",
            "Nurse [First] [Last] reported a medication error involving [First] [Last] on [date] to Dr. [First] [Last].",
            "The post-discharge call for [First] [Middle] [Last] was conducted by [First] [Last] on [date].",
            "Please archive the closed case file for [First] [Last] (ID: [ID]) as authorised by Dr. [First] [Last].",
            "The community outreach log records [First] [Last] as screened by [First] [Last] on [date] at [Street].",
            "Dr. [First] [Last]'s referral letter for [First] [Middle] [Last] has been received and logged on [date].",
            "The end-of-day report by Nurse [First] [Last] lists [First] [Middle] [Last] as stable as of [date]."
        ]
    
    def _generate_random_date(self) -> str:
        """Generate a random date between 2020 and 2026."""
        start_date = datetime(2020, 1, 1)
        end_date = datetime(2026, 3, 5)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        random_date = start_date + timedelta(days=random_days)
        
        # Use various date formats
        formats = [
            "%d/%m/%Y",
            "%Y-%m-%d",
            "%d %B %Y",
            "%B %d, %Y"
        ]
        return random_date.strftime(random.choice(formats))
    
    def _generate_id(self) -> str:
        """Generate a random medical ID."""
        prefixes = ["MRN", "PAT", "REG", "ID", "CASE"]
        numbers = random.randint(100000, 999999)
        return f"{random.choice(prefixes)}{numbers}"
    
    def _generate_phone(self) -> str:
        """Generate a random African phone number."""
        country_codes = ["+254", "+27", "+234", "+233", "+255", "+256", "+250", "+251"]
        number = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        return f"{random.choice(country_codes)} {number[:3]} {number[3:6]} {number[6:]}"
    
    def _fill_template(self, template: str) -> tuple:
        """
        Fill a template with random data and track entity positions.
        Returns (filled_text, entities_list)
        """
        text = template
        entities = []
        names_used = []
        
        # Track offset changes due to replacements
        offset = 0
        
        # Process all placeholders in order of appearance
        placeholders = []
        for match in [
            ("[First]", "first"),
            ("[Middle]", "middle"),
            ("[Last]", "last"),
            ("[age]", "age"),
            ("[date]", "date"),
            ("[time]", "time"),
            ("[ID]", "id"),
            ("[phone]", "phone"),
            ("[condition]", "condition"),
            ("[medication]", "medication"),
            ("[procedure]", "procedure"),
            ("[test]", "test"),
            ("[facility]", "facility"),
            ("[Street]", "street"),
            ("[ward]", "ward"),
            ("[department]", "department"),
            ("[program]", "program"),
            ("[day]", "day"),
            ("[number]", "number"),
            ("[occupation]", "occupation"),
            ("[gender]", "gender")
        ]:
            placeholder, ptype = match
            pos = 0
            while True:
                pos = text.find(placeholder, pos)
                if pos == -1:
                    break
                placeholders.append((pos, placeholder, ptype))
                pos += len(placeholder)
        
        # Sort by position
        placeholders.sort()
        
        # Replace each placeholder
        for original_pos, placeholder, ptype in placeholders:
            # Adjust position for previous replacements
            current_pos = text.find(placeholder)
            if current_pos == -1:
                continue
            
            # Generate replacement value
            if ptype == "first":
                value = random.choice(self.first_names)
                # Track as name entity
                entities.append({
                    "start": current_pos,
                    "end": current_pos + len(value),
                    "label": "PERSON",
                    "value": value
                })
            elif ptype == "middle":
                value = random.choice(self.first_names)
            elif ptype == "last":
                value = random.choice(self.last_names)
            elif ptype == "age":
                value = str(random.choice(self.ages))
            elif ptype == "date":
                value = self._generate_random_date()
            elif ptype == "time":
                value = random.choice(self.times)
            elif ptype == "id":
                value = self._generate_id()
            elif ptype == "phone":
                value = self._generate_phone()
            elif ptype == "condition":
                value = random.choice(self.conditions)
            elif ptype == "medication":
                value = random.choice(self.medications)
            elif ptype == "procedure":
                value = random.choice(self.procedures)
            elif ptype == "test":
                value = random.choice(self.tests)
            elif ptype == "facility":
                value = random.choice(self.facilities)
            elif ptype == "street":
                value = random.choice(self.streets)
            elif ptype == "ward":
                value = random.choice(self.wards)
            elif ptype == "department":
                value = random.choice(self.departments)
            elif ptype == "program":
                value = random.choice(self.programs)
            elif ptype == "day":
                value = random.choice(self.days)
            elif ptype == "number":
                value = str(random.randint(1, 8))
            elif ptype == "occupation":
                value = random.choice(self.occupations)
            elif ptype == "gender":
                value = random.choice(self.genders)
            else:
                value = placeholder
            
            # Replace first occurrence
            text = text.replace(placeholder, value, 1)
            
            # Update positions of subsequent entities
            length_diff = len(value) - len(placeholder)
            for entity in entities:
                if entity["start"] > current_pos:
                    entity["start"] += length_diff
                    entity["end"] += length_diff
        
        # Now find all name entities (combinations of [First] [Last] and [First] [Middle] [Last])
        # We need to reconstruct which parts form complete names
        # This is complex, so let's use a simpler approach: find all person names in the final text
        
        # Actually, let's track names properly during replacement
        # Restart with better tracking
        
        return text, entities
    
    def _find_names_in_text(self, text: str) -> List[Dict]:
        """Find all person names in the text and return entity annotations."""
        entities = []
        
        # Look for patterns like "First Last" or "First Middle Last"
        words = text.split()
        i = 0
        while i < len(words):
            # Clean word (remove punctuation at start/end for checking)
            word = words[i].strip('.,;:()[]{}!?"\'')
            
            # Check if it's a first name
            if word in self.first_names:
                name_parts = [word]
                j = i + 1
                
                # Check for middle name
                if j < len(words):
                    next_word = words[j].strip('.,;:()[]{}!?"\'')
                    if next_word in self.first_names:
                        name_parts.append(next_word)
                        j += 1
                
                # Check for last name
                if j < len(words):
                    next_word = words[j].strip('.,;:()[]{}!?"\'')
                    if next_word in self.last_names:
                        name_parts.append(next_word)
                        j += 1
                        
                        # We found a complete name, now find its position in text
                        full_name = " ".join(name_parts)
                        # Find position accounting for already found entities
                        search_start = 0
                        if entities:
                            search_start = entities[-1]["end"]
                        
                        pos = text.find(full_name, search_start)
                        if pos != -1:
                            entities.append({
                                "start": pos,
                                "end": pos + len(full_name),
                                "label": "PERSON"
                            })
                        
                        i = j
                        continue
            i += 1
        
        return entities
    
    def generate_record(self, template_index: int) -> Dict:
        """Generate a single record using the specified template."""
        template = self.templates[template_index]
        
        # Fill template
        text, _ = self._fill_template(template)
        
        # Find all name entities in the filled text
        entities = self._find_names_in_text(text)
        
        return {
            "text": text,
            "entities": entities,
            "template_id": template_index + 1,
            "template_category": self._get_category(template_index + 1)
        }
    
    def _get_category(self, template_id: int) -> str:
        """Get the category name for a template ID."""
        if 1 <= template_id <= 50:
            return "A_PATIENT_AS_SUBJECT"
        elif 51 <= template_id <= 100:
            return "B_THIRD_PARTY_NARRATOR"
        elif 101 <= template_id <= 150:
            return "C_FAMILY_SOCIAL_CONTEXT"
        elif 151 <= template_id <= 200:
            return "D_ADMINISTRATIVE_INSTITUTIONAL"
        return "UNKNOWN"
    
    def generate_dataset(self, rows_per_template: int = 50, output_path: str = "../generated_data/name_phi_data.jsonl") -> None:
        """Generate the complete dataset with all templates."""
        print(f"Generating {len(self.templates)} templates × {rows_per_template} rows = {len(self.templates) * rows_per_template} total rows")
        
        records = []
        for template_idx in range(len(self.templates)):
            for row_num in range(rows_per_template):
                record = self.generate_record(template_idx)
                records.append(record)
                
                # Progress indicator
                if (template_idx * rows_per_template + row_num + 1) % 500 == 0:
                    print(f"  Generated {template_idx * rows_per_template + row_num + 1} records...")
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            for record in records:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        
        print(f"\n✓ Successfully generated {len(records)} records")
        print(f"✓ Output saved to: {output_path}")
        
        # Statistics
        print(f"\nDataset Statistics:")
        print(f"  Total records: {len(records)}")
        print(f"  Unique templates: {len(self.templates)}")
        print(f"  Rows per template: {rows_per_template}")
        
        # Category breakdown
        categories = {}
        for record in records:
            cat = record['template_category']
            categories[cat] = categories.get(cat, 0) + 1
        
        print(f"\n  Category breakdown:")
        for cat, count in sorted(categories.items()):
            print(f"    {cat}: {count} records")


def main():
    """Main function to generate the dataset."""
    print("=" * 70)
    print("COMPREHENSIVE NAME PHI GENERATOR")
    print("=" * 70)
    print()
    
    generator = ComprehensiveNamePHIGenerator(seed=42)
    generator.generate_dataset(rows_per_template=50)
    
    print()
    print("=" * 70)
    print("GENERATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
