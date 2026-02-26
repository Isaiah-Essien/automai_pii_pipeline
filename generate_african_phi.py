#!/usr/bin/env python3
"""
African PHI Data Generator
===========================

Generates short, focused medical text with African PHI entities.
Optimized for African healthcare data with country-specific information.
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from collections import defaultdict, Counter

try:
    from faker import Faker
except ImportError:
    raise ImportError("Please install faker: pip install faker")


class AfricanPHIGenerator:
    """
    Generator for African-focused PHI data with short sentences.
    """

    def __init__(
        self,
        config_path: str = "phi_config.json",
        seed: Optional[int] = None
    ):
        """Initialize with configuration file."""
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        if seed:
            random.seed(seed)
            Faker.seed(seed)
        
        # Initialize Faker (use default locale, we have custom African data)
        self.faker = Faker('en_US')
        
        self.african_countries = self.config['african_countries']
        self.entity_config = self.config['entity_types']
        self.output_settings = self.config['output_settings']
        
        # Common African first and last names
        self.african_first_names = [
            # ── NIGERIA ──────────────────────────────────────────────────────────
            "Amara", "Ayo", "Chinwe", "Aisha", "Jabari", "Nia", "Babatunde",
            "Adebayo", "Chidi", "Habib", "Zalika", "Nadira", "Akinyi", "Rashid",
            "Kadijah", "Musa", "Abena", "Jelani", "Nkechi", "Inyene", "Uduak",
            "Idorenyin", "Akin", "Sade", "Chukwu", "Zainab", "Kehinde", "Ayoade",
            "Nneka", "Oluwafemi", "Kelechi", "Chinonso", "Olufemi", "Chibuzo",
            "Efua", "Adaeze", "Nnamdi", "Emeka", "Ngozi", "Obinna", "Amaka",
            "Chukwuemeka", "Uchenna", "Chidinma", "Tunde", "Funmilayo", "Damilola",
            "Folake", "Chizaram", "Adaora", "Uforo",

            # ── GHANA ─────────────────────────────────────────────────────────────
            "Kwame", "Kofi", "Kwesi", "Abena", "Akosua", "Ama", "Kojo", "Yaa",
            "Ekow", "Adwoa", "Nana", "Akua", "Kwabena",

            # ── KENYA ─────────────────────────────────────────────────────────────
            "Kamau", "Wanjiru", "Otieno", "Makena", "Imani", "Nuru", "Njeri",
            "Mwangi", "Achieng", "Ochieng", "Wambui", "Kipchoge", "Zawadi",

            # ── TANZANIA ──────────────────────────────────────────────────────────
            "Zuri", "Tariq", "Zuberi", "Amina", "Omari", "Salim", "Bahati",
            "Tumaini", "Furaha", "Neema", "Juma",

            # ── SOUTH AFRICA ─────────────────────────────────────────────────────
            "Thabo", "Tendai", "Lindiwe", "Mandla", "Bongani", "Nkosi",
            "Zanele", "Sibusiso", "Nokwanda", "Lerato", "Thandeka", "Siyanda",
            "Nompumelelo",

            # ── ETHIOPIA ─────────────────────────────────────────────────────────
            "Fatima", "Sekou", "Abebe", "Tigist", "Biruk", "Selam", "Dawit",
            "Hiwot", "Yonas", "Mekdes", "Tesfaye", "Almaz",

            # ── SENEGAL ───────────────────────────────────────────────────────────
            "Aminata", "Adama", "Mariam", "Oumar", "Fatou", "Moussa", "Rokhaya",
            "Cheikh", "Ndèye", "Ibrahima",

            # ── CÔTE D'IVOIRE ────────────────────────────────────────────────────
            "Adjoua", "Kouadio", "Affoue", "Amenan", "Kouakou", "Adjo", "Amlan",

            # ── CAMEROON ─────────────────────────────────────────────────────────
            "Ngozi", "Eposi", "Bih", "Nkeng", "Fomba", "Mbeki", "Awah", "Tanyi",

            # ── UGANDA ───────────────────────────────────────────────────────────
            "Dembe", "Nambi", "Mukasa", "Nalubega", "Kato", "Nakato", "Wasswa",
            "Babirye", "Ssemakula",

            # ── ZAMBIA ───────────────────────────────────────────────────────────
            "Chisomo", "Mutale", "Mwila", "Mumba", "Chilufya", "Kasonde",
            "Lombe", "Mulenga",

            # ── ZIMBABWE ─────────────────────────────────────────────────────────
            "Rudo", "Chipo", "Tarisai", "Tsitsi", "Tatenda", "Farai",
            "Tafadzwa", "Munashe", "Simbarashe",

            # ── MALAWI ───────────────────────────────────────────────────────────
            "Kondwani", "Pemba", "Azibo", "Tiwonge", "Wongani", "Chikondi",
            "Mphatso",

            # ── MOZAMBIQUE ───────────────────────────────────────────────────────
            "Felicidade", "Ancha", "Epifania", "Celestino", "Ermelinda",
            "Isadora", "Bernardo",

            # ── ANGOLA ───────────────────────────────────────────────────────────
            "Kiluanje", "Nzinga", "Mbaka", "Lulendo", "Tumelo", "Mayamba",
            "Ntangu",

            # ── DEMOCRATIC REPUBLIC OF CONGO (DRC) ───────────────────────────────
            "Ilunga", "Mbuyi", "Kabila", "Lusamba", "Tshala", "Nsimba",
            "Mbuyamba", "Kasongo",

            # ── REPUBLIC OF CONGO ────────────────────────────────────────────────
            "Ngoma", "Likibi", "Mandoumbi", "Bienvenu", "Nsonde", "Kikounga",
            "Banzouzi",

            # ── RWANDA ───────────────────────────────────────────────────────────
            "Uwimana", "Ingabire", "Gasimba", "Mukamusoni", "Habimana",
            "Uwase", "Nkurunziza",

            # ── BURUNDI ──────────────────────────────────────────────────────────
            "Ndayishimiye", "Ntaconayigize", "Nsengiyumva", "Hakizimana",
            "Niyongabo", "Nshimirimana",

            # ── SOMALIA ──────────────────────────────────────────────────────────
            "Aadan", "Ifrah", "Caamir", "Faadumo", "Xasan", "Ubax", "Sahra",
            "Cabdirashid",

            # ── SOUTH SUDAN ──────────────────────────────────────────────────────
            "Deng", "Achol", "Nyakim", "Garang", "Akuien", "Ayen", "Chol",
            "Nyaboth",

            # ── SUDAN ────────────────────────────────────────────────────────────
            "Hind", "Amira", "Khalid", "Nadia", "Sittana", "Yusra", "Kamal",
            "Randa",

            # ── EGYPT ────────────────────────────────────────────────────────────
            "Nour", "Karima", "Hana", "Layla", "Mena", "Amir", "Rana", "Tarek",

            # ── LIBYA ────────────────────────────────────────────────────────────
            "Salma", "Wafa", "Mabrouka", "Fathi", "Khaled", "Reem", "Nawal",

            # ── TUNISIA ──────────────────────────────────────────────────────────
            "Yasmine", "Hajer", "Mouna", "Rania", "Sana", "Ines", "Sofiane",
            "Olfa",

            # ── ALGERIA ──────────────────────────────────────────────────────────
            "Meriem", "Kahina", "Tafat", "Massinissa", "Tinhinan", "Dihya",
            "Yidir",

            # ── MOROCCO ──────────────────────────────────────────────────────────
            "Khadija", "Nadia", "Siham", "Youssef", "Houda", "Nadia", "Zineb",
            "Tafaout",

            # ── MAURITANIA ───────────────────────────────────────────────────────
            "Vatimetou", "Khayra", "Aichetou", "Bilal", "Mamadou", "Rouba",
            "Mariem",

            # ── MALI ─────────────────────────────────────────────────────────────
            "Rokia", "Boubacar", "Aminata", "Modibo", "Djénéba", "Seydou",
            "Sanogo", "Traore",

            # ── BURKINA FASO ─────────────────────────────────────────────────────
            "Safiatou", "Rasmane", "Naomie", "Inoussa", "Roukiatou", "Hamidou",
            "Alimata",

            # ── NIGER ────────────────────────────────────────────────────────────
            "Zeinabou", "Ramatou", "Moussa", "Hadiza", "Almoustapha", "Falmata",
            "Laouali",

            # ── CHAD ─────────────────────────────────────────────────────────────
            "Achta", "Amina", "Mahamat", "Fatime", "Idriss", "Khadidja",
            "Halime",

            # ── GUINEA ───────────────────────────────────────────────────────────
            "Diallo", "Binta", "Mamadou", "Fatoumata", "Alpha", "Mariama",
            "Ibrahima",

            # ── GUINEA-BISSAU ────────────────────────────────────────────────────
            "Umaro", "Iancuba", "Maimuna", "Djenabu", "Braima", "Fatu", "Aua",

            # ── SIERRA LEONE ─────────────────────────────────────────────────────
            "Khadija", "Isata", "Binta", "Aminata", "Foday", "Yankay",
            "Sorie", "Hawa",

            # ── LIBERIA ──────────────────────────────────────────────────────────
            "Garmai", "Korto", "Pewu", "Zaye", "Kula", "Gonpu", "Weamie",
            "Nyenati",

            # ── GAMBIA ───────────────────────────────────────────────────────────
            "Binta", "Fatou", "Lamin", "Ndey", "Ebrima", "Mariama", "Alasana",

            # ── CAPE VERDE ───────────────────────────────────────────────────────
            "Djaimilia", "Benvinda", "Nhanha", "Tchinha", "Celina", "Miriam",
            "Edna",

            # ── SÃO TOMÉ AND PRÍNCIPE ────────────────────────────────────────────
            "Amélia", "Aurélio", "Elsa", "Natércia", "Sebastião", "Fialho",
            "Telma",

            # ── EQUATORIAL GUINEA ────────────────────────────────────────────────
            "Ndong", "Mba", "Nzang", "Esono", "Abeso", "Eyang", "Obiang",

            # ── GABON ────────────────────────────────────────────────────────────
            "Mintsa", "Nkoghe", "Biyoghe", "Ondo", "Nguema", "Ndong", "Mboumba",

            # ── CENTRAL AFRICAN REPUBLIC ─────────────────────────────────────────
            "Baba", "Kossi", "Nzara", "Yangba", "Moise", "Ngaissona", "Bozize",

            # ── CAMEROON (additional) ────────────────────────────────────────────
            "Mbarga", "Atangana", "Mendo", "Owona", "Ngo", "Njoya",

            # ── TOGO ─────────────────────────────────────────────────────────────
            "Afi", "Akpene", "Dzifa", "Kossi", "Mawuli", "Yawa", "Kafui",

            # ── BENIN ────────────────────────────────────────────────────────────
            "Adjoua", "Tola", "Gnon", "Dossa", "Boni", "Fifame", "Vicentia",

            # ── BOTSWANA ─────────────────────────────────────────────────────────
            "Boipelo", "Thato", "Motheo", "Kagiso", "Lorato", "Kgosi",
            "Onthatile", "Goitseone",

            # ── NAMIBIA ──────────────────────────────────────────────────────────
            "Ndinelago", "Ndapanda", "Tulimevava", "Penda", "Nangula",
            "Ndapewa", "Hilya",

            # ── LESOTHO ──────────────────────────────────────────────────────────
            "Lineo", "Palesa", "Mpho", "Kgomotso", "Moipone", "Retselisitsoe",
            "Nthabiseng",

            # ── ESWATINI ─────────────────────────────────────────────────────────
            "Siphiwe", "Nompumelelo", "Buhle", "Lungile", "Sikhumbuzo",
            "Nombuso", "Thulile",

            # ── MADAGASCAR ───────────────────────────────────────────────────────
            "Voahangy", "Tahiry", "Faniry", "Tsiry", "Mirana", "Nirina",
            "Hery", "Nomenjanahary",

            # ── MAURITIUS ────────────────────────────────────────────────────────
            "Yadhav", "Anishta", "Preethi", "Devika", "Roshan", "Kavita",
            "Vikash",

            # ── SEYCHELLES ───────────────────────────────────────────────────────
            "Joseline", "Anel", "Merisia", "Roseline", "Andronic", "Micheline",
            "Reginald",

            # ── COMOROS ──────────────────────────────────────────────────────────
            "Ahamada", "Oumouri", "Nassur", "Fatouma", "Moina", "Said",
            "Mariama",

            # ── DJIBOUTI ─────────────────────────────────────────────────────────
            "Hodan", "Safia", "Deeqa", "Abdillahi", "Houssein", "Fadumo",
            "Asad",

            # ── ERITREA ──────────────────────────────────────────────────────────
            "Miriam", "Selam", "Yordanos", "Haben", "Tesfai", "Fiyori",
            "Kibra", "Ghenet",

            # ── WESTERN SAHARA ───────────────────────────────────────────────────
            "Mbarka", "Haiballa", "Tiyib", "Lakhsas", "Sultana", "Nayem",
            "Brahim",
        ]
        
        self.african_last_names = [
            # 1. ALGERIA
            "Boudiaf", "Amrouche", "Tighilt", "Ait Hamou", "Zitout", "Matoub", "Yidir",

            # 2. ANGOLA
            "Nzinga", "Dos Santos", "Lourenco", "Savimbi", "Kiluanje", "Mayamba", "Luvualu",

            # 3. BENIN
            "Amoussou", "Kerekou", "Boni", "Zinsou", "Glele", "Hounkpe", "Bio",

            # 4. BOTSWANA
            "Molefe", "Khama", "Masisi", "Mogae", "Tshekedi", "Seretse", "Gobuiwang",

            # 5. BURKINA FASO
            "Sawadogo", "Ouedraogo", "Zongo", "Kabore", "Compaore", "Tapsoba", "Sankara",

            # 6. BURUNDI
            "Nshimirimana", "Ndayishimiye", "Hakizimana", "Ntaconayigize", "Niyongabo", "Bigirimana", "Ntibantunganya",

            # 7. CABO VERDE
            "Evora", "Monteiro", "Lopes", "Tavares", "Ramos", "Pires", "Fonseca",

            # 8. CAMEROON
            "Biya", "Atangana", "Mbarga", "Njoya", "Chedjou", "Fomba", "Ngono",

            # 9. CENTRAL AFRICAN REPUBLIC
            "Bozize", "Touadera", "Ngaissona", "Wondo", "Ngakoutou", "Patasse", "Kolingba",

            # 10. CHAD
            "Deby", "Mahamat", "Nassour", "Itno", "Kimto", "Bichara", "Habre",

            # 11. COMOROS
            "Ahamada", "Assoumani", "Djohar", "Bacar", "Oumouri", "Said", "Msaidizi",

            # 12. CÔTE D'IVOIRE
            "Ouattara", "Gbagbo", "Bedie", "Coulibaly", "Diomande", "Koffi", "Bamba",

            # 13. DEMOCRATIC REPUBLIC OF THE CONGO
            "Mutombo", "Kabila", "Ilunga", "Tshisekedi", "Mbuyi", "Kasongo", "Nsimba",

            # 14. DJIBOUTI
            "Guelleh", "Abdillahi", "Houssein", "Robleh", "Ismail", "Omar", "Moussa",

            # 15. EGYPT
            "Nasser", "Sadat", "Mubarak", "El-Sayed", "Mansour", "Farouk", "Khalil",

            # 16. EQUATORIAL GUINEA
            "Nguema", "Obiang", "Oyono", "Mba", "Nnang", "Eneme", "Ngomo",

            # 17. ERITREA
            "Tesfai", "Gebremichael", "Tewolde", "Russom", "Berhane", "Negash", "Haile",

            # 18. ESWATINI
            "Dlamini", "Sukati", "Simelane", "Zwane", "Hleta", "Mswati", "Nkosi",

            # 19. ETHIOPIA
            "Abebe", "Tadesse", "Tesfaye", "Gebre", "Bekele", "Girma", "Desta",

            # 20. GABON
            "Bongo", "Ndong", "Mboumba", "Mintsa", "Ntoutoume", "Obame", "Ping",

            # 21. THE GAMBIA
            "Jammeh", "Barrow", "Jallow", "Ceesay", "Bojang", "Sanneh", "Touray",

            # 22. GHANA
            "Mensah", "Boateng", "Osei", "Asante", "Asare", "Appiah", "Acheampong",

            # 23. GUINEA
            "Diallo", "Bah", "Barry", "Camara", "Toure", "Conde", "Sylla",

            # 24. GUINEA-BISSAU
            "Embalo", "Gomes", "Djata", "Mendes", "Sambu", "Seidi", "Lopes",

            # 25. KENYA
            "Mwangi", "Kariuki", "Otieno", "Kamau", "Kiprono", "Wanjiku", "Njoroge",

            # 26. LESOTHO
            "Mofokeng", "Mohapi", "Molapo", "Thabane", "Lekhanya", "Seeiso", "Mathibeli",

            # 27. LIBERIA
            "Weah", "Johnson", "Kollie", "Gbowee", "Flomo", "Fofana", "Togba",

            # 28. LIBYA
            "Gaddafi", "Warfalli", "Tarhouni", "Senussi", "Ben Ali", "Haftar", "Mneina",

            # 29. MADAGASCAR
            "Rakoto", "Rabemananjara", "Ratsiraka", "Ravalomanana", "Andrianarivo", "Rajaonarimampianina", "Raseta",

            # 30. MALAWI
            "Banda", "Gondwe", "Mkandawire", "Kasinja", "Nyirenda", "Chilemba", "Mpinganjira",

            # 31. MALI
            "Traore", "Keita", "Coulibaly", "Cisse", "Diarra", "Kone", "Sanogo",

            # 32. MAURITANIA
            "Ould", "Bah", "Haïdara", "Vall", "Aziz", "Taya", "Ghazouani",

            # 33. MAURITIUS
            "Ramgoolam", "Jugnauth", "Beeharry", "Anerood", "Hurree", "Lutchmeenaraidoo", "Sookun",

            # 34. MOROCCO
            "Alaoui", "Benali", "Tazi", "El Fassi", "Chraibi", "Lahlou", "Benbrahim",

            # 35. MOZAMBIQUE
            "Mondlane", "Chissano", "Nyusi", "Langa", "Nhantumbo", "Pondja", "Mucavel",

            # 36. NAMIBIA
            "Nujoma", "Geingob", "Nghifindaka", "Katjavivi", "Amupolo", "Nambala", "Pohamba",

            # 37. NIGER
            "Issoufou", "Bazoum", "Mahamadou", "Hamidou", "Seyni", "Abdou", "Maïga",

            # 38. NIGERIA
            "Okonkwo", "Okeke", "Adeyemi", "Nnamdi", "Uwem", "Temitope", "Babatunde",
            "Achebe", "Lawal", "Okafor", "Eze", "Soyinka", "Abimbola", "Mutombo",
            "Oluwaseun",

            # 39. REPUBLIC OF THE CONGO
            "Sassou", "Nguesso", "Likibi", "Ngoma", "Banzouzi", "Mabiala", "Lisouba",

            # 40. RWANDA
            "Iradukunda", "Habyarimana", "Uwimana", "Nshimiyimana", "Bizimana", "Nsengimana", "Munyakazi",

            # 41. SÃO TOMÉ AND PRÍNCIPE
            "Trovoada", "Da Costa", "De Carvalho", "Sousa", "Quaresma", "Pinto", "Neto",

            # 42. SENEGAL
            "Diop", "Ndiaye", "Fall", "Sow", "Mbaye", "Faye", "Gueye",

            # 43. SEYCHELLES
            "Hoareau", "Rene", "Michel", "Lafortune", "Pillay", "Joubert", "Barra",

            # 44. SIERRA LEONE
            "Kamara", "Koroma", "Bangura", "Turay", "Mansaray", "Jalloh", "Sesay",

            # 45. SOMALIA
            "Abdi", "Farah", "Warsame", "Roble", "Hirsi", "Hassan", "Abukar",

            # 46. SOUTH AFRICA
            "Nkosi", "Zulu", "Dlamini", "Mandela", "Khumalo", "Mkhize", "Tshabalala",

            # 47. SOUTH SUDAN
            "Deng", "Garang", "Kiir", "Machar", "Aguer", "Lual", "Kon",

            # 48. SUDAN
            "Bashir", "Siddig", "Abdalla", "Ahmed", "Khalil", "Osman", "Mirghani",

            # 49. TANZANIA
            "Nyerere", "Juma", "Makamba", "Msigwa", "Mhina", "Simba", "Mbita",

            # 50. TOGO
            "Gnassingbe", "Agbo", "Amevor", "Akue", "Dossou", "Olympio", "Eyadema",

            # 51. TUNISIA
            "Trabelsi", "Ben Salah", "Mzali", "Chaabane", "Ouerghi", "Hamdi", "Bourguiba",

            # 52. UGANDA
            "Museveni", "Byarugaba", "Akello", "Ssemakula", "Tumwesigye", "Mutebe", "Oryem",

            # 53. ZAMBIA
            "Phiri", "Tembo", "Mwale", "Mumba", "Sinkala", "Kalumba", "Lungu",

            # 54. ZIMBABWE
            "Moyo", "Ncube", "Ndlovu", "Sibanda", "Mpofu", "Chigumba", "Mugabe",
        ]
        
        # Common African street names
        self.african_streets = [
           # FOUND ACROSS MANY COUNTRIES 
            "Uhuru",            # "Freedom" in Swahili — found in Kenya, Tanzania, Uganda
            "Independence",     # Found in nearly every post-colonial African capital
            "Nelson Mandela",   # Streets in 30+ African countries
            "Haile Selassie",   # Found across East & West Africa
            "Kwame Nkrumah",    # Found across West & Central Africa
            "Julius Nyerere",   # Found across East & Central Africa
            "Market",           # Universal across Africa
            "Station",          
            "Church",           
            "Hospital",         
            "University",        
            "Airport",          
            "Beach",            # Universal in coastal countries
            "Garden",           # Universal across Africa

            # NIGERIA (West Africa) 
            "Ahmadu Bello Way",         # Named after the first Premier of Northern Nigeria
            "Herbert Macaulay",         # Named after the father of Nigerian nationalism
            "Nnamdi Azikiwe",           # Named after Nigeria's first president
            "Obafemi Awolowo",          # Named after a founding father of Nigeria
            "Lagos-Ibadan Expressway",
            "Broad Street",             # Major street in Lagos Island
            "Kingsway",                 # Colonial-era Lagos street name
            "Adeola Odeku",             # Victoria Island, Lagos
            "Bode Thomas",              # Surulere, Lagos

            # ── GHANA (West Africa) ─────────────────────────────────────────────
            "Moi",              # Kept from original — also found in Ghana
            "Kenyatta",         # Kept from original — also found in Ghana
            "Accra-Tema Motorway",
            "Ring Road",
            "Cantonments Road",         # Accra
            "Liberation Road",          # Accra
            "Castle Road",              # Accra
            "Guggisberg Avenue",        # Accra
            "Osu Oxford Street",        # Accra's famous entertainment strip

            # ── KENYA (East Africa) ─────────────────────────────────────────────
            "Tom Mboya Street",         # Named after Kenyan labour leader, Nairobi
            "Kimathi Street",           # Named after independence hero Dedan Kimathi, Nairobi
            "Moi Avenue",               # Nairobi CBD
            "Oginga Odinga Road",       # Named after Kenya's first VP
            "Harry Thuku Road",         # Nairobi
            "Harambee Avenue",          # "Pulling together" in Swahili, Nairobi
            "Koinange Street",          # Nairobi
            "Argwings Kodhek Road",     # Nairobi
            "Waiyaki Way",              # Major Nairobi highway

            # ── TANZANIA (East Africa) ───────────────────────────────────────────
            "Samora Avenue",            # Named after Mozambique's first president, Dar es Salaam
            "Sokoine Drive",            # Named after PM Edward Sokoine, Dar es Salaam
            "Bibi Titi Mohamed Road",   # Named after a key independence activist, Dar es Salaam
            "Lumumba Street",           # Dar es Salaam
            "Msimbazi Street",          # Dar es Salaam
            "Bagamoyo Road",            # Major road in Dar es Salaam

            # ── SOUTH AFRICA (Southern Africa) ──────────────────────────────────
            "Jan Smuts Avenue",         # Johannesburg
            "Vilakazi Street",          # Soweto — only street in the world with 2 Nobel laureates
            "Louis Botha Avenue",       # Johannesburg
            "De Waal Drive",            # Cape Town (also known as Philip Kgosana Drive)
            "Adderley Street",          # Cape Town CBD
            "Long Street",              # Cape Town
            "Voortrekker Road",         # Western Cape
            "Church Street",            # Pretoria (one of the longest straight streets in the world)
            "Paul Kruger Street",       # Pretoria
            "Steve Biko Road",          # Durban

            # ── ETHIOPIA (East Africa) ───────────────────────────────────────────
            "Bole Road",                # Addis Ababa — major commercial road
            "Churchill Avenue",         # Addis Ababa
            "Ras Desta Damtew",         # Addis Ababa
            "Meskel Square",            # Famous square/road, Addis Ababa
            "Africa Avenue",            # Addis Ababa (leads to AU headquarters)
            "Jomo Kenyatta Street",     # Addis Ababa

            # ── EGYPT (North Africa) ─────────────────────────────────────────────
            "Tahrir Square",            # Cairo — famous plaza and surrounding roads
            "Salah Salem Road",         # Cairo
            "Corniche El Nil",          # Cairo — along the Nile
            "26th of July Street",      # Cairo
            "Ramses Street",            # Cairo
            "El Haram Street",          # Giza (Pyramid Road)
            "El Galaa Street",          # Cairo

            # ── SENEGAL (West Africa) ────────────────────────────────────────────
            "Avenue Léopold Sédar Senghor",   # Named after Senegal's first president, Dakar
            "Avenue Cheikh Anta Diop",        # Named after the scholar, Dakar
            "Rue de Thiong",                   # Dakar
            "Avenue Blaise Diagne",           # Named after first Black deputy in French parliament
            "Corniche Ouest",                  # Dakar seafront road

            # ── CÔTE D'IVOIRE (West Africa) ─────────────────────────────────────
            "Boulevard de la République",     # Abidjan
            "Boulevard Latrille",             # Abidjan
            "Avenue Houphouët-Boigny",        # Named after first president, Abidjan
            "Rue des Jardins",                # Abidjan
            "Boulevard du Général de Gaulle", # Abidjan (colonial-era)

            # ── CAMEROON (Central Africa) ───────────────────────────────────────
            "Avenue Kennedy",           # Yaoundé
            "Rue Nachtigal",            # Yaoundé
            "Boulevard de la Liberté",  # Douala
            "Rue Flatters",             # Yaoundé
            "Avenue de l'Indépendance", # Yaoundé

            # ── DRC (Central Africa) ─────────────────────────────────────────────
            "Boulevard du 30 Juin",     # Kinshasa — named after independence day
            "Avenue Patrice Lumumba",   # Kinshasa
            "Avenue de l'Université",   # Kinshasa
            "Boulevard Triomphal",      # Kinshasa
            "Avenue Kasa-Vubu",         # Named after first president of DRC, Kinshasa

            # ── REPUBLIC OF CONGO (Central Africa) ──────────────────────────────
            "Avenue Amilcar Cabral",    # Brazzaville
            "Rue Behagle",              # Brazzaville
            "Avenue des Trois Martyrs", # Brazzaville
            "Boulevard Denis Sassou Nguesso", # Brazzaville

            # ── ANGOLA (Southern Africa) ─────────────────────────────────────────
            "Rua Rainha Ginga",         # Named after Queen Nzinga, Luanda
            "Avenida dos Combatentes",  # Luanda
            "Rua Major Kanhangulo",     # Luanda
            "Avenida 4 de Fevereiro",   # Luanda — independence movement date
            "Avenida Lenine",           # Luanda

            # ── MOZAMBIQUE (Southern Africa) ─────────────────────────────────────
            "Avenida Eduardo Mondlane",  # Named after liberation hero, Maputo
            "Avenida Julius Nyerere",    # Maputo
            "Avenida Samora Machel",     # Named after first president, Maputo
            "Avenida 25 de Setembro",    # Maputo — independence date
            "Rua da Rádio Moçambique",   # Maputo

            # ── ZIMBABWE (Southern Africa) ───────────────────────────────────────
            "Samora Machel Avenue",     # Harare
            "Jason Moyo Avenue",        # Named after ZAPU leader, Harare
            "Herbert Chitepo Avenue",   # Harare
            "Robert Mugabe Road",       # Harare
            "Leopold Takawira Avenue",  # Bulawayo
            "Joshua Nkomo Street",      # Bulawayo

            # ── ZAMBIA (Southern Africa) ─────────────────────────────────────────
            "Freedom Way",              # Lusaka
            "Cairo Road",               # Lusaka CBD — most famous street
            "Independence Avenue",      # Lusaka
            "Nationalist Road",         # Lusaka
            "Great East Road",          # Lusaka
            "Lumumba Road",             # Lusaka

            # ── UGANDA (East Africa) ─────────────────────────────────────────────
            "Kampala Road",             # Kampala CBD
            "Entebbe Road",             # Major Kampala road
            "Bombo Road",               # Kampala
            "Jinja Road",               # Kampala
            "Obote Avenue",             # Named after Milton Obote, Kampala
            "Ben Kiwanuka Street",      # Kampala — first PM of Uganda
            "Lumumba Avenue",           # Kampala

            # ── RWANDA (East Africa) ─────────────────────────────────────────────
            "KN 3 Road",                # Kigali Nyarugenge Road (post-2012 renaming system)
            "Boulevard de l'Umuganda",  # Kigali
            "Rue de l'Akagera",         # Kigali
            "Avenue de la Paix",        # Kigali
            "KG 7 Avenue",              # Kigali Gasabo Avenue
            "Kimironko Road",           # Kigali

            # ── BURUNDI (East Africa) ────────────────────────────────────────────
            "Boulevard de l'Uprona",    # Bujumbura
            "Avenue du Large",          # Bujumbura lakefront
            "Rue du Commerce",          # Bujumbura
            "Avenue de la Mission",     # Bujumbura
            "Boulevard Patrice Lumumba",# Bujumbura

            # ── MALAWI (Southern Africa) ─────────────────────────────────────────
            "Kamuzu Procession Road",   # Lilongwe — named after founding president Hastings Banda
            "Paul Kagame Road",         # Lilongwe
            "Presidential Way",         # Lilongwe
            "Victoria Avenue",          # Blantyre
            "Kidney Crescent",          # Blantyre

            # ── SOMALIA (East Africa) ────────────────────────────────────────────
            "Maka Al Mukarama Road",    # Mogadishu — most famous street
            "Via Roma",                 # Mogadishu (colonial-era Italian name)
            "Afgooye Road",             # Mogadishu
            "Lido Road",                # Mogadishu seafront
            "KM4 Road",                 # Mogadishu landmark road

            # ── SOUTH SUDAN (East Africa) ────────────────────────────────────────
            "Juba-Nimule Road",         # Major highway, Juba
            "Airport Road",             # Juba
            "Ministries Road",          # Juba
            "Kololo Road",              # Juba
            "Tongping Road",            # Juba

            # ── SUDAN (North Africa) ─────────────────────────────────────────────
            "Al Qasr Avenue",           # Khartoum
            "Africa Road",              # Khartoum
            "Al Jamhuriya Street",      # Khartoum — Republic Street
            "El Nil Avenue",            # Khartoum — along the Nile
            "Sharia al-Matar",          # Khartoum — Airport Road

            # ── LIBYA (North Africa) ─────────────────────────────────────────────
            "Sharia Omar Mukhtar",      # Tripoli — named after resistance hero
            "Sharia Rashid",            # Tripoli
            "Corniche Road",            # Tripoli seafront
            "Green Square Road",        # Tripoli (now Martyrs' Square)
            "Airport Road",             # Tripoli

            # ── TUNISIA (North Africa) ───────────────────────────────────────────
            "Avenue Habib Bourguiba",   # Tunis — named after first president, most iconic street
            "Avenue de la Liberté",     # Tunis
            "Rue de la Kasbah",         # Tunis
            "Avenue Mohamed V",         # Tunis
            "Avenue Farhat Hached",     # Tunis

            # ── ALGERIA (North Africa) ───────────────────────────────────────────
            "Rue Didouche Mourad",      # Algiers — named after independence war hero
            "Boulevard Zighoud Youcef", # Algiers
            "Rue Larbi Ben M'hidi",     # Algiers
            "Avenue du 1er Novembre",   # Algiers — independence movement date
            "Rue Hassiba Ben Bouali",   # Algiers — named after a female war hero

            # ── MOROCCO (North Africa) ───────────────────────────────────────────
            "Avenue Mohammed V",        # Rabat — most prominent boulevard
            "Avenue Hassan II",         # Found in most Moroccan cities
            "Rue de la Liberté",        # Tangier
            "Boulevard Mohammed VI",    # Marrakech
            "Avenue des Forces Armées Royales", # Casablanca

            # ── MAURITANIA (West Africa) ─────────────────────────────────────────
            "Avenue Gamal Abdel Nasser",# Nouakchott
            "Avenue du Roi Faisal",     # Nouakchott
            "Rue de l'Ambassade",       # Nouakchott
            "Avenue Kennedy",           # Nouakchott
            "Route de l'Espoir",        # Trans-Mauritania highway (Road of Hope)

            # ── MALI (West Africa) ───────────────────────────────────────────────
            "Avenue de l'Indépendance", # Bamako
            "Avenue Modibo Keïta",      # Named after first president, Bamako
            "Rue Baba Diarra",          # Bamako
            "Boulevard du Peuple",      # Bamako
            "Avenue de la Nation",      # Bamako

            # ── BURKINA FASO (West Africa) ───────────────────────────────────────
            "Avenue Kwame Nkrumah",     # Ouagadougou
            "Avenue de la Résistance",  # Ouagadougou
            "Rue de la Chance",         # Ouagadougou
            "Avenue Thomas Sankara",    # Named after revolutionary president
            "Boulevard Charles de Gaulle", # Ouagadougou

            # ── NIGER (West Africa) ──────────────────────────────────────────────
            "Boulevard de la République", # Niamey
            "Avenue du Fleuve",           # Niamey — along the Niger River
            "Rue des Bâtisseurs",         # Niamey
            "Avenue de l'Afrique",        # Niamey
            "Route de Tillabéri",         # Niamey

            # ── CHAD (Central Africa) ────────────────────────────────────────────
            "Avenue Charles de Gaulle",   # N'Djamena
            "Avenue Félix Éboué",         # N'Djamena — named after Chadian-born governor
            "Rue du Havre",               # N'Djamena
            "Boulevard du 1er Août",      # N'Djamena
            "Avenue Mobutu",              # N'Djamena

            # ── GUINEA (West Africa) ─────────────────────────────────────────────
            "Boulevard Diallo Telli",     # Conakry — first Secretary-General of the OAU
            "Avenue de la République",    # Conakry
            "Rue KA-020",                 # Conakry
            "Corniche Sud",               # Conakry seafront
            "Avenue du Port",             # Conakry

            # ── GUINEA-BISSAU (West Africa) ──────────────────────────────────────
            "Avenida Amílcar Cabral",     # Bissau — named after liberation hero
            "Rua Eduardo Mondlane",       # Bissau
            "Avenida do Brasil",          # Bissau
            "Avenida Domingos Ramos",     # Bissau
            "Rua Justino Lopes",          # Bissau

            # ── SIERRA LEONE (West Africa) ───────────────────────────────────────
            "Siaka Stevens Street",       # Freetown — named after former president
            "Wilberforce Street",         # Freetown
            "Lightfoot Boston Street",    # Freetown
            "Pademba Road",               # Freetown
            "Circular Road",              # Freetown

            # ── LIBERIA (West Africa) ────────────────────────────────────────────
            "Tubman Boulevard",           # Monrovia — named after William Tubman
            "Broad Street",               # Monrovia CBD
            "Randall Street",             # Monrovia
            "Center Street",              # Monrovia
            "United Nations Drive",       # Monrovia

            # ── THE GAMBIA (West Africa) ─────────────────────────────────────────
            "Kairaba Avenue",             # Banjul — most famous commercial street
            "Independence Drive",         # Banjul
            "Nelson Mandela Street",      # Banjul
            "OAU Boulevard",              # Banjul
            "Bertil Harding Highway",     # Coastal Gambia highway

            # ── CABO VERDE (West Africa / Atlantic) ──────────────────────────────
            "Avenida Amílcar Cabral",     # Praia — named after liberation leader
            "Rua de Lisboa",              # Praia
            "Avenida da ONU",             # Praia
            "Rua de Angola",              # Praia
            "Plateau Street",             # Praia

            # ── SÃO TOMÉ AND PRÍNCIPE (Central Africa / Atlantic) ────────────────
            "Avenida Kwame Nkrumah",      # São Tomé city
            "Rua de Moçambique",          # São Tomé city
            "Avenida da Independência",   # São Tomé city
            "Rua do Pelourinho",          # São Tomé city

            # ── EQUATORIAL GUINEA (Central Africa) ───────────────────────────────
            "Carretera del Aeropuerto",   # Malabo
            "Avenida de la Independencia",# Malabo
            "Calle de Argelia",           # Malabo
            "Paseo Marítimo",             # Malabo seafront

            # ── GABON (Central Africa) ───────────────────────────────────────────
            "Boulevard Triomphal Omar Bongo", # Libreville — named after former president
            "Rue des Défricheurs",            # Libreville
            "Avenue du Colonel Parant",       # Libreville
            "Boulevard de la Mer",            # Libreville seafront
            "Rue de la Mairie",               # Libreville

            # ── CENTRAL AFRICAN REPUBLIC (Central Africa) ────────────────────────
            "Avenue Barthélemy Boganda",  # Bangui — named after founding father
            "Rue de la Paix",             # Bangui
            "Avenue David Dacko",         # Bangui
            "Boulevard du Général Leclerc", # Bangui

            # ── NAMIBIA (Southern Africa) ────────────────────────────────────────
            "Sam Nujoma Drive",           # Windhoek — named after first president
            "Robert Mugabe Avenue",       # Windhoek
            "Independence Avenue",        # Windhoek
            "Hosea Kutako Drive",         # Windhoek — named after chief and activist
            "Nelson Mandela Avenue",      # Windhoek

            # ── BOTSWANA (Southern Africa) ───────────────────────────────────────
            "The Mall",                   # Gaborone — most famous road/strip
            "Khama Crescent",             # Gaborone
            "Segoditshane Way",           # Gaborone
            "Queens Road",                # Gaborone
            "Notwane Road",               # Gaborone

            # ── LESOTHO (Southern Africa) ────────────────────────────────────────
            "Kingsway Road",              # Maseru — main road through the capital
            "Pioneer Road",               # Maseru
            "Moshoeshoe Road",            # Maseru — named after founding king
            "Lerotholi Road",             # Maseru
            "United Nations Road",        # Maseru

            # ── ESWATINI (Southern Africa) ───────────────────────────────────────
            "Gwamile Street",             # Mbabane — most famous street
            "Allister Miller Street",     # Mbabane
            "Somhlolo Road",              # Mbabane — named after founding king
            "Dr Sishayi Road",            # Mbabane
            "MR3 Highway",                # Major Eswatini road

            # ── MADAGASCAR (Southern Africa) ─────────────────────────────────────
            "Avenue de l'Indépendance",   # Antananarivo
            "Rue Rainitovo",              # Antananarivo
            "Boulevard de l'Europe",      # Antananarivo
            "Avenue de France",           # Antananarivo
            "Rue du 26 Juin",             # Antananarivo — independence date

            # ── MAURITIUS (East Africa / Indian Ocean) ───────────────────────────
            "Royal Road",                 # Most common road name across Mauritius
            "Sir Seewoosagur Ramgoolam Street", # Port Louis — named after first PM
            "Farquhar Street",            # Port Louis
            "Sir William Newton Street",  # Port Louis
            "Edith Cavell Street",        # Port Louis

            # ── SEYCHELLES (East Africa / Indian Ocean) ──────────────────────────
            "Francis Rachel Street",      # Victoria — named after independence leader
            "Albert Street",              # Victoria
            "Independence Avenue",        # Victoria
            "5th June Avenue",            # Victoria — Liberation Day date
            "Bois de Rose Avenue",        # Victoria

            # ── COMOROS (East Africa / Indian Ocean) ─────────────────────────────
            "Boulevard de Strasbourg",    # Moroni
            "Rue du Gouvernorat",         # Moroni
            "Avenue Said Mohamed Cheikh", # Moroni
            "Route Nationale 1",          # Comoros main road

            # ── DJIBOUTI (East Africa) ───────────────────────────────────────────
            "Boulevard de la République", # Djibouti City
            "Avenue 26 Juin",             # Djibouti City — independence date
            "Rue de Venise",              # Djibouti City
            "Avenue Hassan Gouled Aptidon", # Named after first president, Djibouti City
            "Place Mahmoud Harbi",        # Djibouti City

            # ── ERITREA (East Africa) ────────────────────────────────────────────
            "Harnet Avenue",              # Asmara — "Freedom" in Tigrinya, most famous street
            "Martyrs Avenue",             # Asmara
            "Nakfa Avenue",               # Asmara — named after liberation war battle
            "Sematat Avenue",             # Asmara
            "Liberation Avenue",          # Asmara
        ]

    def get_random_country(self) -> Tuple[str, Dict]:
        """Get random African country with its data."""
        country_name = random.choice(list(self.african_countries.keys()))
        return country_name, self.african_countries[country_name]

    def generate_person(self) -> str:
        """Generate African person name."""
        first = random.choice(self.african_first_names)
        last = random.choice(self.african_last_names)
        return f"{first} {last}"

    def generate_address(self) -> str:
        """Generate African street address."""
        number = random.randint(1, 999)
        street = random.choice(self.african_streets)
        street_type = random.choice(["Road", "Street", "Avenue", "Way", "Drive"])
        return f"{number} {street} {street_type}"

    def generate_city(self) -> str:
        """Generate African city."""
        country_name, country_data = self.get_random_country()
        return random.choice(country_data['cities'])

    def generate_state(self) -> str:
        """Generate African state/province/region."""
        country_name, country_data = self.get_random_country()
        return random.choice(country_data['states'])

    def generate_country(self) -> str:
        """Generate African country."""
        return random.choice(list(self.african_countries.keys()))

    def generate_date_of_birth(self) -> str:
        """Generate date of birth (18-90 years ago)."""
        days_ago = random.randint(18*365, 90*365)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_admission_date(self) -> str:
        """Generate admission date (recent past)."""
        days_ago = random.randint(1, 365)
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def generate_discharge_date(self, admission_date_str: Optional[str] = None) -> str:
        """Generate discharge date (after admission)."""
        if admission_date_str:
            # Parse admission date and add 1-30 days
            try:
                admit_date = datetime.strptime(admission_date_str, "%d/%m/%Y")
                days_stay = random.randint(1, 30)
                discharge_date = admit_date + timedelta(days=days_stay)
            except:
                days_ago = random.randint(1, 335)
                discharge_date = datetime.now() - timedelta(days=days_ago)
        else:
            days_ago = random.randint(1, 335)
            discharge_date = datetime.now() - timedelta(days=days_ago)
        
        return self.format_date(discharge_date)

    def generate_date(self) -> str:
        """Generate general date."""
        days_ago = random.randint(1, 1825)  # Up to 5 years
        date_obj = datetime.now() - timedelta(days=days_ago)
        return self.format_date(date_obj)

    def format_date(self, date_obj: datetime) -> str:
        """Format date in common formats."""
        formats = [
            lambda d: d.strftime("%d/%m/%Y"),      # 15/03/2024
            lambda d: d.strftime("%d-%m-%Y"),      # 15-03-2024
            lambda d: d.strftime("%d %B %Y"),      # 15 March 2024
            lambda d: d.strftime("%d %b %Y"),      # 15 Mar 2024
        ]
        return random.choice(formats)(date_obj)

    def generate_phone(self) -> str:
        """Generate African phone number with country code."""
        country_name, country_data = self.get_random_country()
        phone_code = country_data['phone_code']
        
        # Generate local number (different formats)
        if random.random() < 0.5:
            # Format: +234 803 123 4567
            local = f"{random.randint(700, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        else:
            # Format: +234-803-123-4567
            local = f"{random.randint(700, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        if random.random() < 0.7:
            return f"{phone_code} {local}"
        else:
            return f"{phone_code}{local.replace(' ', '').replace('-', '')}"

    def generate_fax(self) -> str:
        """Generate African fax number with country code."""
        country_name, country_data = self.get_random_country()
        phone_code = country_data['phone_code']
        
        # Generate fax number (similar format to phone)
        if random.random() < 0.5:
            local = f"{random.randint(700, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
        else:
            local = f"{random.randint(700, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        if random.random() < 0.7:
            return f"{phone_code} {local}"
        else:
            return f"{phone_code}{local.replace(' ', '').replace('-', '')}"

    def generate_email(self) -> str:
        """Generate email address."""
        first = random.choice(self.african_first_names).lower()
        last = random.choice(self.african_last_names).lower()
        
        domains = [
            "hospital.ac.za", "clinic.com.ng", "health.org.ke", "medical.eg.com",
            "patient.gh.net", "healthcare.tz.org", "wellness.zm.co.za",
            "afro-health.com", "africa-clinic.org", "pan-african-medical.net"
        ]
        
        separator = random.choice([".", "_", "-"])
        email = f"{first}{separator}{last}@{random.choice(domains)}"
        return email

    def generate_ssn(self) -> str:
        """Generate Social Security Number / National ID."""
        country_name, country_data = self.get_random_country()
        country_code = country_data['code']
        
        # Format: CC-YYYYMMDDNNNNN (country code, date of birth, sequential)
        year = random.randint(1960, 2006)
        month = random.randint(1, 12)
        day = random.randint(1, 28)
        sequential = random.randint(10000, 99999)
        
        ssn = f"{country_code}-{year:04d}{month:02d}{day:02d}{sequential:05d}"
        return ssn

    def generate_medical_record_number(self) -> str:
        """Generate hospital/clinic medical record number."""
        # Format: MR-YYYY-NNNNNN or HHMMR-NNNNNN (hospital code-sequence)
        year = datetime.now().year
        sequence = random.randint(100000, 999999)
        
        formats = [
            f"MR-{year}-{sequence}",
            f"MRN{sequence:06d}",
            f"HR-{random.randint(10, 99)}-{sequence}",
            f"MED{year}{sequence:05d}"
        ]
        return random.choice(formats)

    def generate_health_plan_beneficiary_number(self) -> str:
        """Generate health insurance/plan beneficiary number."""
        country_name, country_data = self.get_random_country()
        country_code = country_data['code']
        
        # Format: CC-HPPPPPPPPPP (country code, health plan ID, beneficiary number)
        hp_id = random.randint(100, 999)
        beneficiary = random.randint(1000000000, 9999999999)
        
        formats = [
            f"HP-{country_code}-{hp_id}-{beneficiary}",
            f"BEN{country_code}{hp_id:03d}{beneficiary:10d}",
            f"{country_code}-HP-{random.randint(10000000, 99999999)}"
        ]
        return random.choice(formats)

    def generate_account_number(self) -> str:
        """Generate bank/payment account number."""
        country_name, country_data = self.get_random_country()
        country_code = country_data['code']
        
        # Format: CC-NNNNNNNNNNNN (country code + account number)
        account = random.randint(100000000000, 999999999999)
        
        formats = [
            f"{country_code}-{account}",
            f"ACC{account:012d}",
            f"{random.randint(100, 999)}-{random.randint(100000000000, 999999999999)}",
            f"AC{country_code}{account:010d}"
        ]
        return random.choice(formats)

    def generate_entities_for_record(self) -> Dict[str, List[str]]:
        """Generate entities based on configuration."""
        entities_dict = defaultdict(list)
        
        # Always include essential entities
        if self.entity_config["PERSON"]["enabled"]:
            entities_dict["PERSON"].append(self.generate_person())
        
        # Generate dates
        admission_date = None
        if self.entity_config["ADMISSION_DATE"]["enabled"] and random.random() < self.entity_config["ADMISSION_DATE"]["probability"]:
            admission_date = self.generate_admission_date()
            entities_dict["ADMISSION_DATE"].append(admission_date)
        
        if self.entity_config["DISCHARGE_DATE"]["enabled"] and random.random() < self.entity_config["DISCHARGE_DATE"]["probability"]:
            discharge_date = self.generate_discharge_date(admission_date)
            entities_dict["DISCHARGE_DATE"].append(discharge_date)
        
        if self.entity_config["DATE_OF_BIRTH"]["enabled"] and random.random() < self.entity_config["DATE_OF_BIRTH"]["probability"]:
            entities_dict["DATE_OF_BIRTH"].append(self.generate_date_of_birth())
        
        if self.entity_config["DATE"]["enabled"] and random.random() < self.entity_config["DATE"]["probability"]:
            entities_dict["DATE"].append(self.generate_date())
        
        # Generate location entities
        if self.entity_config["ADDRESS"]["enabled"] and random.random() < self.entity_config["ADDRESS"]["probability"]:
            entities_dict["ADDRESS"].append(self.generate_address())
        
        if self.entity_config["CITY"]["enabled"] and random.random() < self.entity_config["CITY"]["probability"]:
            entities_dict["CITY"].append(self.generate_city())
        
        if self.entity_config["STATE"]["enabled"] and random.random() < self.entity_config["STATE"]["probability"]:
            entities_dict["STATE"].append(self.generate_state())
        
        if self.entity_config["COUNTRY"]["enabled"] and random.random() < self.entity_config["COUNTRY"]["probability"]:
            entities_dict["COUNTRY"].append(self.generate_country())
        
        # Generate phone
        if self.entity_config["PHONE"]["enabled"] and random.random() < self.entity_config["PHONE"]["probability"]:
            entities_dict["PHONE"].append(self.generate_phone())
        
        # Generate fax
        if self.entity_config["FAX"]["enabled"] and random.random() < self.entity_config["FAX"]["probability"]:
            entities_dict["FAX"].append(self.generate_fax())
        
        # Generate email
        if self.entity_config["EMAIL"]["enabled"] and random.random() < self.entity_config["EMAIL"]["probability"]:
            entities_dict["EMAIL"].append(self.generate_email())
        
        # Generate Social Security Number / National ID
        if self.entity_config["SSN"]["enabled"] and random.random() < self.entity_config["SSN"]["probability"]:
            entities_dict["SSN"].append(self.generate_ssn())
        
        # Generate medical record number
        if self.entity_config["MEDICAL_RECORD_NUMBER"]["enabled"] and random.random() < self.entity_config["MEDICAL_RECORD_NUMBER"]["probability"]:
            entities_dict["MEDICAL_RECORD_NUMBER"].append(self.generate_medical_record_number())
        
        # Generate health plan beneficiary number
        if self.entity_config["HEALTH_PLAN_BENEFICIARY_NUMBER"]["enabled"] and random.random() < self.entity_config["HEALTH_PLAN_BENEFICIARY_NUMBER"]["probability"]:
            entities_dict["HEALTH_PLAN_BENEFICIARY_NUMBER"].append(self.generate_health_plan_beneficiary_number())
        
        # Generate account number
        if self.entity_config["ACCOUNT_NUMBER"]["enabled"] and random.random() < self.entity_config["ACCOUNT_NUMBER"]["probability"]:
            entities_dict["ACCOUNT_NUMBER"].append(self.generate_account_number())
        
        return entities_dict

    def create_short_sentences(self, entities_dict: Dict[str, List[str]]) -> str:
        """Create short, focused sentences with PHI."""
        sentences = []
        
        # Person introduction
        if "PERSON" in entities_dict:
            person = entities_dict["PERSON"][0]
            sentences.append(f"Patient name is {person}.")
            
            # Add DOB if available
            if "DATE_OF_BIRTH" in entities_dict:
                dob = entities_dict["DATE_OF_BIRTH"][0]
                sentences.append(f"Born on {dob}.")
        
        # Address information
        if "ADDRESS" in entities_dict:
            address = entities_dict["ADDRESS"][0]
            city = entities_dict.get("CITY", [self.generate_city()])[0]
            sentences.append(f"Resides at {address}, {city}.")
        elif "CITY" in entities_dict:
            city = entities_dict["CITY"][0]
            sentences.append(f"Lives in {city}.")
        
        # State/Country
        if "STATE" in entities_dict and "COUNTRY" in entities_dict:
            state = entities_dict["STATE"][0]
            country = entities_dict["COUNTRY"][0]
            sentences.append(f"From {state}, {country}.")
        elif "COUNTRY" in entities_dict:
            country = entities_dict["COUNTRY"][0]
            sentences.append(f"Country of residence is {country}.")
        
        # Phone contact
        if "PHONE" in entities_dict:
            phone = entities_dict["PHONE"][0]
            sentences.append(f"Contact number: {phone}.")
        
        # Admission information
        if "ADMISSION_DATE" in entities_dict:
            admit = entities_dict["ADMISSION_DATE"][0]
            sentences.append(f"Admitted on {admit}.")
        
        # Discharge information
        if "DISCHARGE_DATE" in entities_dict:
            discharge = entities_dict["DISCHARGE_DATE"][0]
            sentences.append(f"Discharged on {discharge}.")
        
        # General date if present
        if "DATE" in entities_dict and "ADMISSION_DATE" not in entities_dict:
            date = entities_dict["DATE"][0]
            actions = ["Visited clinic", "Consulted", "Examined", "Treated"]
            sentences.append(f"{random.choice(actions)} on {date}.")
        
        # Fax contact
        if "FAX" in entities_dict:
            fax = entities_dict["FAX"][0]
            sentences.append(f"Fax: {fax}.")
        
        # Email
        if "EMAIL" in entities_dict:
            email = entities_dict["EMAIL"][0]
            sentences.append(f"Email address: {email}.")
        
        # Social Security Number / National ID
        if "SSN" in entities_dict:
            ssn = entities_dict["SSN"][0]
            sentences.append(f"National ID: {ssn}.")
        
        # Medical record number
        if "MEDICAL_RECORD_NUMBER" in entities_dict:
            mrn = entities_dict["MEDICAL_RECORD_NUMBER"][0]
            sentences.append(f"Medical record: {mrn}.")
        
        # Health plan beneficiary number
        if "HEALTH_PLAN_BENEFICIARY_NUMBER" in entities_dict:
            hpbn = entities_dict["HEALTH_PLAN_BENEFICIARY_NUMBER"][0]
            sentences.append(f"Beneficiary ID: {hpbn}.")
        
        # Account number
        if "ACCOUNT_NUMBER" in entities_dict:
            account = entities_dict["ACCOUNT_NUMBER"][0]
            sentences.append(f"Account: {account}.")
        
        # Shuffle for variety
        random.shuffle(sentences)
        
        return " ".join(sentences)

    def add_entity(
        self,
        text: str,
        substring: str,
        label: str,
        entities_list: List[Dict],
        start_offset: int = 0
    ) -> bool:
        """Find substring in text and add entity annotation."""
        idx = text.find(substring, start_offset)
        if idx == -1:
            return False
        
        start = idx
        end = idx + len(substring)
        
        # Check for overlap
        for existing in entities_list:
            if not (end <= existing["start"] or start >= existing["end"]):
                return False
        
        entities_list.append({
            "start": start,
            "end": end,
            "label": label
        })
        
        return True

    def build_record(self, record_id: str) -> Dict:
        """Build a complete annotated record with short sentences."""
        # Generate entities
        entities_dict = self.generate_entities_for_record()
        
        # Create short text
        text = self.create_short_sentences(entities_dict)
        
        # Annotate entities
        entities_list = []
        
        label_map = {
            "PERSON": "PERSON",
            "DATE_OF_BIRTH": "DATE_OF_BIRTH",
            "ADMISSION_DATE": "ADMISSION_DATE",
            "DISCHARGE_DATE": "DISCHARGE_DATE",
            "DATE": "DATE",
            "ADDRESS": "ADDRESS",
            "CITY": "CITY",
            "STATE": "STATE",
            "COUNTRY": "COUNTRY",
            "PHONE": "PHONE",
            "FAX": "FAX",
            "EMAIL": "EMAIL",
            "SSN": "SSN",
            "MEDICAL_RECORD_NUMBER": "MEDICAL_RECORD_NUMBER",
            "HEALTH_PLAN_BENEFICIARY_NUMBER": "HEALTH_PLAN_BENEFICIARY_NUMBER",
            "ACCOUNT_NUMBER": "ACCOUNT_NUMBER"
        }
        
        for entity_type, values in entities_dict.items():
            if entity_type in label_map:
                for value in values:
                    self.add_entity(text, value, label_map[entity_type], entities_list)
        
        # Sort entities by start position
        entities_list.sort(key=lambda x: x["start"])
        
        return {
            "id": record_id,
            "text": text,
            "entities": entities_list,
            "source": "synthetic",
            "region": "africa",
            "lang": "en"
        }

    def generate_dataset(self, n_records: int, verbose: bool = False) -> List[Dict]:
        """Generate complete dataset."""
        dataset = []
        
        for i in range(n_records):
            if verbose and (i + 1) % 100 == 0:
                print(f"Generated {i + 1}/{n_records} records...")
            
            record_id = f"african_phi_{uuid.uuid4().hex[:12]}"
            record = self.build_record(record_id)
            dataset.append(record)
        
        if verbose:
            print(f"✓ Generated {n_records} records")
        
        return dataset

    def write_jsonl(self, dataset: List[Dict], output_path: str) -> None:
        """Write dataset to JSONL file."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for record in dataset:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        print(f"✓ Dataset written to {output_path}")

    def generate_frequency_report(self, dataset: List[Dict]) -> Dict:
        """Generate statistics report."""
        label_counts = Counter()
        total_entities = 0
        
        for record in dataset:
            for ent in record["entities"]:
                label_counts[ent["label"]] += 1
                total_entities += 1
        
        return {
            "total_records": len(dataset),
            "total_entities": total_entities,
            "avg_entities_per_record": total_entities / len(dataset) if dataset else 0,
            "label_distribution": dict(label_counts)
        }


def print_sample_record(record: Dict) -> None:
    """Pretty print a sample record."""
    print(f"\n{'='*80}")
    print(f"ID: {record['id']}")
    print(f"{'='*80}")
    print(f"\nTEXT:\n{record['text']}\n")
    print(f"ENTITIES ({len(record['entities'])}):")
    for ent in record['entities']:
        entity_text = record['text'][ent['start']:ent['end']]
        print(f"  [{ent['start']:4d}-{ent['end']:4d}] {ent['label']:20s} → \"{entity_text}\"")


def main():
    """Main execution."""
    print("=" * 80)
    print("AFRICAN PHI DATA GENERATOR")
    print("Short Sentences | African Data")
    print("=" * 80)
    
    # Initialize generator
    generator = AfricanPHIGenerator(
        config_path="phi_config.json",
        seed=42
    )
    
    # Generate sample dataset
    print("\n[1] Generating sample dataset (100 records)...")
    sample_dataset = generator.generate_dataset(n_records=100, verbose=True)
    
    # Write sample
    generator.write_jsonl(sample_dataset, "african_phi_sample.jsonl")
    
    # Show examples
    print("\n[2] Sample records:")
    for i in range(min(3, len(sample_dataset))):
        print_sample_record(sample_dataset[i])
    
    # Statistics
    print("\n[3] Dataset Statistics:")
    report = generator.generate_frequency_report(sample_dataset)
    print(f"  Total Records: {report['total_records']}")
    print(f"  Total Entities: {report['total_entities']}")
    print(f"  Avg Entities/Record: {report['avg_entities_per_record']:.2f}")
    print(f"\n  Label Distribution:")
    for label, count in sorted(report['label_distribution'].items(), key=lambda x: -x[1]):
        pct = 100 * count / report['total_entities']
        print(f"    {label:20s}: {count:4d} ({pct:5.2f}%)")
    
    # Generate larger dataset
    print("\n[4] Generating full dataset (1,000 records)...")
    full_dataset = generator.generate_dataset(n_records=1000, verbose=True)
    generator.write_jsonl(full_dataset, "african_phi_full.jsonl")
    
    # Split dataset
    print("\n[5] Creating train/dev/test splits...")
    random.shuffle(full_dataset)
    
    train_size = int(0.8 * len(full_dataset))
    dev_size = int(0.1 * len(full_dataset))
    
    train = full_dataset[:train_size]
    dev = full_dataset[train_size:train_size+dev_size]
    test = full_dataset[train_size+dev_size:]
    
    generator.write_jsonl(train, "african_phi_train.jsonl")
    generator.write_jsonl(dev, "african_phi_dev.jsonl")
    generator.write_jsonl(test, "african_phi_test.jsonl")
    
    print(f"  Train: {len(train)} records")
    print(f"  Dev:   {len(dev)} records")
    print(f"  Test:  {len(test)} records")
    
    print("\n" + "=" * 80)
    print("✓ GENERATION COMPLETE")
    print("=" * 80)
    print("\nGenerated files:")
    print("  • african_phi_sample.jsonl (100 records)")
    print("  • african_phi_train.jsonl (800 records)")
    print("  • african_phi_dev.jsonl (100 records)")
    print("  • african_phi_test.jsonl (100 records)")
    print("  • african_phi_full.jsonl (1,000 records)")
    print("\nReady for African PHI detection model training!")


if __name__ == "__main__":
    main()
