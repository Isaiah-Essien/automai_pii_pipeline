"""Build the data/lexicons/*.txt files.

Bulk lists are composed deterministically from curated components: real West and
East African given-name and surname stems, WHO-style drug stems (-cillin, -olol,
-pril, ...), and place-name components.  This reaches the Section 15 floor of
2,000 distinct entries per list without inventing an implausible corpus.  The
*ambiguous* sets that actually carry the hard cases are hand-curated instead,
because those depend on real collisions rather than on composition.
"""

import random
import unicodedata
from pathlib import Path

OUT = Path("data/lexicons")
OUT.mkdir(parents=True, exist_ok=True)
rng = random.Random(20260827)

# Name stems grouped by language of origin.  The corpus is English prose, but
# the PHI inside it is drawn from the languages actually spoken by patients, so
# each stem carries a BCP-47 tag.  That tag is what lets a line report
# `code_switched` honestly instead of guessing.
GIVEN_BY_LANG = {
    "ig": """Chioma Amara Ngozi Adaeze Ifeoma Chinyere Uchenna Obiageli Nneka Chidinma
Emeka Obinna Chukwudi Ikechukwu Nnamdi Kelechi Chibueze Ebuka Somto Arinze""".split(),
    "yo": """Adeyemi Bolanle Folake Yetunde Titilayo Omolara Adebisi Kehinde Taiwo Bukola
Oluwaseun Babatunde Olamide Temitope Adewale Ayodeji Olusegun Damilola Tunde Segun""".split(),
    "ha": """Abubakar Fatima Aisha Zainab Hauwa Maryam Halima Amina Rukayya Safiya
Musa Ibrahim Yusuf Sani Usman Bello Aliyu Nasiru Suleiman Kabiru""".split(),
    "ki": """Wanjiru Njeri Wambui Nyokabi Wairimu Muthoni Waithera Nyambura Wangari Gathoni
Kamau Mwangi Kariuki Njoroge Macharia Kimani Githinji Wachira Ndungu Maina""".split(),
    "sw": """Amani Baraka Neema Zawadi Upendo Tumaini Rehema Furaha Imani Subira
Juma Hamisi Rashid Salim Bakari Omari Mwinyi Athumani Shabani Ramadhani""".split(),
    "rw": """Uwase Mukamana Uwimana Nyirahabimana Mukantwari Umutoni Ingabire Uwera Mutesi Keza
Habimana Nsengimana Ndayisenga Bizimana Hakizimana Ntwari Rugema Munyaneza Gasana Rwema""".split(),
    "zu": """Thandiwe Nomsa Zanele Lerato Palesa Refilwe Naledi Boitumelo Kagiso Tshepo
Sipho Themba Mandla Bongani Siyabonga Lwazi Zola Vusi Andile""".split(),
    "en": """Grace Mercy Patience Blessing Precious Faith Joy Peace Comfort Charity
Emmanuel Samuel Daniel Joseph Michael Victor Gabriel Isaac Solomon Benjamin""".split(),
}
SURNAME_BY_LANG = {
    "ig": """Nwankwo Okafor Okonkwo Eze Obi Nwosu Anyanwu Chukwu Ugochukwu Onyeka""".split(),
    "yo": """Adeyemi Adebayo Ogunleye Afolabi Oyelaran Balogun Adegoke Oladipo Ogundele Aluko""".split(),
    "ha": """Bello Musa Ibrahim Suleiman Danjuma Abubakar Yakubu Garba Lawal Shehu""".split(),
    "ki": """Kamau Mwangi Otieno Odhiambo Wekesa Chepkoech Kiptoo Rotich Barasa Wanyama
Mwenda Kilonzo Mutua Ndeti Muthama Kioko Nzioka Musyoka Mailu Katana""".split(),
    "rw": """Uwimana Habimana Niyonzima Mukamana Ndayambaje Nkurunziza Bizimungu Kagame
Rutayisire Munyakazi""".split(),
    "ny": """Banda Phiri Mwale Zulu Tembo Chirwa Nkhoma Mbewe Kalua Kaunda""".split(),
    "zu": """Dlamini Nkosi Mokoena Molefe Sithole Ndlovu Khumalo Zwane Mahlangu Radebe""".split(),
    "ak": """Mensah Owusu Boateng Asante Appiah Osei Agyeman Darko Amoah Frimpong""".split(),
    "ff": """Diallo Traore Keita Camara Sylla Toure Bah Barry Sow Fofana""".split(),
}

GIVEN_STEMS = """Chioma Amara Ngozi Adaeze Ifeoma Chinyere Uchenna Obiageli Nneka Chidinma
Emeka Obinna Chukwudi Ikechukwu Nnamdi Kelechi Chibueze Ebuka Somto Arinze
Adeyemi Bolanle Folake Yetunde Titilayo Omolara Adebisi Kehinde Taiwo Bukola
Oluwaseun Babatunde Olamide Temitope Adewale Ayodeji Olusegun Damilola Tunde Segun
Abubakar Fatima Aisha Zainab Hauwa Maryam Halima Amina Rukayya Safiya
Musa Ibrahim Yusuf Sani Usman Bello Aliyu Nasiru Suleiman Kabiru
Wanjiru Njeri Wambui Nyokabi Wairimu Muthoni Waithera Nyambura Wangari Gathoni
Kamau Mwangi Kariuki Njoroge Macharia Kimani Githinji Wachira Ndungu Maina
Amani Baraka Neema Zawadi Upendo Tumaini Rehema Furaha Imani Subira
Juma Hamisi Rashid Salim Bakari Omari Mwinyi Athumani Shabani Ramadhani
Uwase Mukamana Uwimana Nyirahabimana Mukantwari Umutoni Ingabire Uwera Mutesi Keza
Habimana Nsengimana Ndayisenga Bizimana Hakizimana Ntwari Rugema Munyaneza Gasana Rwema
Thandiwe Nomsa Zanele Lerato Palesa Refilwe Naledi Boitumelo Kagiso Tshepo
Sipho Themba Mandla Bongani Siyabonga Lwazi Zola Vusi Andile Musa
Grace Mercy Patience Blessing Precious Faith Joy Peace Comfort Charity
Emmanuel Samuel Daniel Joseph Michael Victor Gabriel Isaac Solomon Benjamin""".split()

SURNAME_STEMS = """Nwankwo Okafor Okonkwo Eze Obi Nwosu Anyanwu Chukwu Ugochukwu Onyeka
Adeyemi Adebayo Ogunleye Afolabi Oyelaran Balogun Adegoke Oladipo Ogundele Aluko
Bello Musa Ibrahim Suleiman Danjuma Abubakar Yakubu Garba Lawal Shehu
Kamau Mwangi Otieno Odhiambo Wekesa Chepkoech Kiptoo Rotich Barasa Wanyama
Mwenda Kilonzo Mutua Ndeti Muthama Kioko Nzioka Musyoka Mailu Katana
Uwimana Habimana Niyonzima Mukamana Ndayambaje Nkurunziza Bizimungu Kagame Rutayisire Munyakazi
Banda Phiri Mwale Zulu Tembo Chirwa Nkhoma Mbewe Kalua Kaunda
Dlamini Nkosi Mokoena Molefe Sithole Ndlovu Khumalo Zwane Mahlangu Radebe
Mensah Owusu Boateng Asante Appiah Osei Agyeman Darko Amoah Frimpong
Diallo Traore Keita Camara Sylla Toure Bah Barry Sow Fofana""".split()

DRUG_STEMS = [
    ("amoxi", "cillin"), ("ampi", "cillin"), ("cloxa", "cillin"), ("flucloxa", "cillin"),
    ("aten", "olol"), ("prop", "olol"), ("bisopr", "olol"), ("metopr", "olol"),
    ("lisino", "pril"), ("enala", "pril"), ("rami", "pril"), ("capto", "pril"),
    ("simva", "statin"), ("atorva", "statin"), ("prava", "statin"), ("rosuva", "statin"),
    ("cipro", "floxacin"), ("levo", "floxacin"), ("moxi", "floxacin"), ("oflox", "acin"),
    ("metro", "nidazole"), ("tini", "dazole"), ("flu", "conazole"), ("keto", "conazole"),
    ("ome", "prazole"), ("panto", "prazole"), ("eso", "prazole"), ("lanso", "prazole"),
    ("cefa", "lexin"), ("ceftri", "axone"), ("cefu", "roxime"), ("cefo", "taxime"),
    ("azithro", "mycin"), ("erythro", "mycin"), ("clarithro", "mycin"), ("genta", "micin"),
    ("halo", "peridol"), ("risper", "idone"), ("olanz", "apine"), ("quet", "iapine"),
    ("lora", "zepam"), ("diaz", "epam"), ("clona", "zepam"), ("mida", "zolam"),
    ("ibu", "profen"), ("keto", "profen"), ("nap", "roxen"), ("diclo", "fenac"),
]
DRUG_PREFIX = ["", "hydro", "levo", "dextro", "des", "nor", "iso", "meta", "para", "di",
               "tri", "chloro", "fluoro", "bromo", "methyl", "ethyl", "amino", "keto",
               "oxy", "deoxy", "cyclo", "benz", "phen", "thio", "sulfa", "acetyl", "carb",
               "dihydro", "tetra", "poly", "mono", "pseudo", "neo", "pro", "anti", "endo",
               "exo", "peri", "sub", "super", "ultra", "micro", "nano", "beta", "alpha"]
DRUG_INFIX = ["", "a", "o", "i", "en", "in", "ox", "az", "ur"]

DISEASE_HEADS = """malaria tuberculosis pneumonia hypertension diabetes asthma anaemia sepsis
meningitis hepatitis cholera typhoid measles tetanus rabies dengue schistosomiasis
filariasis leishmaniasis trypanosomiasis onchocerciasis dysentery gastroenteritis nephritis
cirrhosis pancreatitis appendicitis endocarditis myocarditis pericarditis bronchitis sinusitis
osteomyelitis cellulitis dermatitis conjunctivitis otitis arthritis colitis encephalitis""".split()
DISEASE_MODS = """acute chronic severe mild moderate recurrent persistent latent congenital acquired
cerebral pulmonary hepatic renal cardiac gastric neonatal paediatric maternal drug-resistant
multidrug-resistant uncomplicated complicated disseminated localised systemic febrile afebrile
early-stage late-stage relapsing remitting suspected confirmed presumed occult""".split()

PLACE_HEADS = """Ikeja Yaba Surulere Ikoyi Lekki Ajah Ojota Maryland Gbagada Ketu
Kano Kaduna Zaria Katsina Sokoto Gusau Bauchi Jos Minna Lokoja
Nairobi Kisumu Nakuru Eldoret Thika Machakos Nyeri Meru Embu Kitui
Kigali Huye Musanze Rubavu Muhanga Nyagatare Rwamagana Karongi Gicumbi Kayonza
Kampala Jinja Mbale Gulu Arua Mbarara Masaka Soroti Lira Hoima
Accra Kumasi Tamale Takoradi Cape Tema Koforidua Sunyani Bolgatanga Wa
Dar Mwanza Arusha Dodoma Mbeya Tanga Morogoro Iringa Moshi Songea""".split()
PLACE_TAILS = """Village Town Ward Estate Layout Quarters Junction Market Road Crescent
Close Avenue Street Lane Terrace Gardens Heights Park Valley Hills
North South East West Central Upper Lower New Old Greater""".split()

FACILITY_HEADS = """General Teaching Referral District Regional Provincial Municipal Community
Cottage Mission Faith Mercy Grace Hope Unity Trinity Nightingale Memorial Central Federal
Specialist Diagnostic Maternity Paediatric Orthopaedic Cardiac Renal Eye Dental Chest""".split()
FACILITY_TAILS = """Hospital Clinic Centre Dispensary Infirmary Polyclinic Sanatorium
Health-Post Medical-Centre Health-Centre""".split()



def fill(target, maker, label, max_attempts_factor=200):
    """Draw distinct items until `target` is reached.

    Raises rather than looping forever when the component space cannot supply
    `target` distinct values -- an unreachable floor is a build bug we want to
    see immediately, not a hang.
    """
    seen = set()
    attempts = 0
    limit = target * max_attempts_factor
    while len(seen) < target:
        seen.add(maker())
        attempts += 1
        if attempts > limit:
            raise RuntimeError(
                f"{label}: only {len(seen)} distinct of {target} after "
                f"{attempts} draws; widen the component lists"
            )
    return seen


def nfc(s):
    return unicodedata.normalize("NFC", s)


def write(name, items):
    items = sorted({nfc(i) for i in items if i.strip()})
    (OUT / name).write_text("\n".join(items) + "\n", encoding="utf-8")
    print(f"{name}: {len(items)}")
    return items


# --- names: given x surname combinations, plus singles ---------------------
full_names = fill(
    4000, lambda: f"{rng.choice(GIVEN_STEMS)} {rng.choice(SURNAME_STEMS)}", "names_full"
)
write("names_full.txt", full_names)

# Language-tagged names: "<name>\t<bcp47>".  Written as a separate file so the
# plain lists stay usable on their own.
tagged_given = sorted({(n, lang) for lang, names in GIVEN_BY_LANG.items() for n in names})
tagged_surname = sorted({(n, lang) for lang, names in SURNAME_BY_LANG.items() for n in names})
(OUT / "names_given_lang.tsv").write_text(
    "\n".join(f"{n}\t{lang}" for n, lang in tagged_given) + "\n", encoding="utf-8"
)
(OUT / "names_surname_lang.tsv").write_text(
    "\n".join(f"{n}\t{lang}" for n, lang in tagged_surname) + "\n", encoding="utf-8"
)
print(f"names_given_lang.tsv: {len(tagged_given)}")
print(f"names_surname_lang.tsv: {len(tagged_surname)}")
write("names_given.txt", GIVEN_STEMS)
write("names_surname.txt", SURNAME_STEMS)

# --- drugs -----------------------------------------------------------------
drugs = set()
for pre, suf in DRUG_STEMS:
    drugs.add((pre + suf).capitalize())
# Real generic names, plus the formulation and salt qualifiers that genuinely
# appear on African essential-medicines lists and prescription charts.  We do
# NOT cross-produce stems: "Norciprooxfloxacin" is not a drug, and teaching the
# model that it is would be worse than having a shorter list.
DRUG_BASE = [(pre + suf).capitalize() for pre, suf in DRUG_STEMS] + """Paracetamol
Artemether Lumefantrine Artesunate Quinine Chloroquine Primaquine Praziquantel
Albendazole Mebendazole Ivermectin Rifampicin Isoniazid Pyrazinamide Ethambutol
Streptomycin Dapsone Nevirapine Efavirenz Zidovudine Lamivudine Tenofovir
Dolutegravir Abacavir Ritonavir Cotrimoxazole Nitrofurantoin Furosemide
Spironolactone Hydrochlorothiazide Amlodipine Nifedipine Methyldopa Hydralazine
Digoxin Warfarin Heparin Aspirin Clopidogrel Metformin Glibenclamide Insulin
Salbutamol Beclometasone Prednisolone Dexamethasone Hydrocortisone Adrenaline
Oxytocin Misoprostol Magnesium Ferrous Folic Vitamin Zinc ORS Morphine Tramadol
Pethidine Codeine Phenobarbitone Phenytoin Carbamazepine Valproate Amitriptyline
Fluoxetine Chlorpromazine Ceftazidime Vancomycin Meropenem Fluconazole
Nystatin Acyclovir Tetracycline Doxycycline Chloramphenicol Gentamicin
Benzylpenicillin Procaine Ampicillin Cefixime Azithromycin Clindamycin
Ranitidine Cimetidine Loperamide Metoclopramide Promethazine Chlorpheniramine
Cetirizine Ibuprofen Diclofenac Indomethacin Allopurinol Colchicine Atenolol""".split()
DRUG_FORMS = ["", "", "", "syrup", "tablets", "injection", "suspension", "oral solution",
              "IV", "PO", "IM", "sodium", "hydrochloride", "sulfate", "phosphate",
              "dispersible", "paediatric", "retard", "SR", "combination"]
drugs = set(DRUG_BASE)
drugs |= fill(
    2200 - len(drugs),
    lambda: " ".join(
        w for w in (rng.choice(DRUG_BASE), rng.choice(DRUG_FORMS)) if w
    ),
    "drugs",
)
write("drugs.txt", drugs)

# --- diseases --------------------------------------------------------------
diseases = set(DISEASE_HEADS)
# Modifiers are constrained per head: severity applies to most conditions, but
# an anatomical site does not ("renal measles" is not a diagnosis).  Grouping the
# heads keeps the generated combinations clinically coherent.
SEVERITY = ["acute", "chronic", "severe", "mild", "moderate", "recurrent",
            "persistent", "suspected", "confirmed", "uncomplicated", "complicated"]
COURSE = ["", "", "relapsing", "drug-resistant", "multidrug-resistant", "disseminated"]
POPULATION = ["", "", "", "in pregnancy", "in childhood", "neonatal", "paediatric"]

# Infections take severity, course, and population, but not an organ site.
INFECTIONS = """malaria tuberculosis pneumonia cholera typhoid measles tetanus rabies
dengue schistosomiasis filariasis leishmaniasis trypanosomiasis onchocerciasis
dysentery gastroenteritis meningitis hepatitis sepsis""".split()
# Inflammatory conditions already name their own site in the "-itis" stem.
INFLAMMATORY = """nephritis pancreatitis appendicitis endocarditis myocarditis
pericarditis bronchitis sinusitis osteomyelitis cellulitis dermatitis
conjunctivitis otitis arthritis colitis encephalitis""".split()
# Chronic conditions take severity and course only.
CHRONIC = """hypertension diabetes asthma anaemia cirrhosis""".split()


# Drug resistance is a property of an organism, so it qualifies only the
# infections where it is actually reported.  Applying it to an inflammatory or
# chronic condition ("drug-resistant conjunctivitis") is not a diagnosis.
RESISTANT_ELIGIBLE = {"malaria", "tuberculosis", "typhoid", "pneumonia", "dysentery"}


def make_disease():
    bucket = rng.random()
    if bucket < 0.45:
        head = rng.choice(INFECTIONS)
        course = rng.choice(COURSE)
        if "resistant" in course and head not in RESISTANT_ELIGIBLE:
            course = ""
        parts = (rng.choice(SEVERITY), head, course, rng.choice(POPULATION))
    elif bucket < 0.78:
        head = rng.choice(INFLAMMATORY)
        # Inflammatory conditions name their own site; severity is the only
        # modifier that reads naturally.
        parts = (rng.choice(SEVERITY), head, "", "")
    else:
        head = rng.choice(CHRONIC)
        parts = (rng.choice(SEVERITY), head, "", rng.choice(POPULATION))
    return " ".join(w for w in parts if w)


diseases = set(DISEASE_HEADS)
diseases |= fill(2200 - len(diseases), make_disease, "diseases")
write("diseases.txt", diseases)

# --- places ----------------------------------------------------------------
places = set()
PLACE_QUALIFIERS = ["", "", "", "Phase 1", "Phase 2", "Phase 3", "Extension",
                    "Annex", "Old", "New", "Upper", "Lower"]
places |= fill(
    2200,
    lambda: " ".join(
        w for w in (rng.choice(PLACE_HEADS), rng.choice(PLACE_TAILS), rng.choice(PLACE_QUALIFIERS)) if w
    ),
    "places",
)
write("places.txt", places)

# --- facilities (identifying, named sites) ---------------------------------
facilities = fill(
    2200,
    lambda: f"{rng.choice(PLACE_HEADS)} {rng.choice(FACILITY_HEADS)} {rng.choice(FACILITY_TAILS)}",
    "facilities",
)
write("facilities.txt", facilities)

# --- generic facility labels (PRESERVE: not identifying) -------------------
generic = set()
for unit in ["ward", "theatre", "unit", "bay", "annex", "block", "wing", "room"]:
    for mod in ["male", "female", "paediatric", "maternity", "surgical", "medical",
                "isolation", "emergency", "observation", "recovery", "intensive care",
                "high dependency", "outpatient", "inpatient", "triage", "admissions",
                "postnatal", "antenatal", "orthopaedic", "burns", "renal", "oncology"]:
        generic.add(f"{mod} {unit}")
for n in range(1, 40):
    generic.add(f"ward {n}")
    generic.add(f"bay {n}")
write("facilities_generic.txt", generic)

# --- anatomy (PRESERVE) ----------------------------------------------------
anatomy = """chest abdomen thorax cranium femur tibia fibula humerus radius ulna clavicle
scapula sternum pelvis sacrum coccyx vertebra mandible maxilla orbit larynx pharynx trachea
bronchus lung pleura diaphragm heart aorta ventricle atrium pericardium liver gallbladder
pancreas spleen kidney ureter bladder urethra stomach duodenum jejunum ileum caecum colon
rectum appendix oesophagus thyroid adrenal ovary uterus cervix placenta prostate testis
retina cornea sclera cochlea tympanum meninges cortex cerebellum brainstem hippocampus
axilla groin popliteal antecubital carotid jugular femoral brachial radial ulnar tibial""".split()
write("anatomy.txt", anatomy)

# --- non-PHI clinical words (PRESERVE) -------------------------------------
non_phi = """triage handover discharge admission referral consent review rounds observation
vitals baseline follow-up compliance adherence dosage titration escalation deterioration
improvement stabilisation resuscitation intubation extubation catheterisation cannulation
transfusion infusion nebulisation physiotherapy counselling immunisation screening prophylaxis
palliation rehabilitation debridement suturing dressing splinting traction mobilisation""".split()
write("non_phi.txt", non_phi)
