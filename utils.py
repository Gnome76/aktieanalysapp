import datetime

def calculate_targetkurs_pe(bolag):
    # targetkurs_pe = vinst_nastaar * ((pe1 + pe2) / 2)
    try:
        vinst_nastaar = float(bolag.get("vinst_nastaar", 0))
        pe1 = float(bolag.get("pe1", 0))
        pe2 = float(bolag.get("pe2", 0))
        return round(vinst_nastaar * ((pe1 + pe2) / 2), 2)
    except Exception:
        return 0.0

def calculate_targetkurs_ps(bolag):
    # targetkurs_ps = medel av ps1 och ps2 * genomsnitt omsättningstillväxt * nuvarande kurs
    try:
        ps1 = float(bolag.get("ps1", 0))
        ps2 = float(bolag.get("ps2", 0))
        omsattningstillvaxt1 = float(bolag.get("omsattningstillvaxt1", 0)) / 100
        omsattningstillvaxt2 = float(bolag.get("omsattningstillvaxt2", 0)) / 100
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        medel_ps = (ps1 + ps2) / 2
        medel_omsattningstillvaxt = (omsattningstillvaxt1 + omsattningstillvaxt2) / 2
        return round(medel_ps * medel_omsattningstillvaxt * nuvarande_kurs, 2)
    except Exception:
        return 0.0

def calculate_undervardering(bolag):
    try:
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        target_pe = calculate_targetkurs_pe(bolag)
        target_ps = calculate_targetkurs_ps(bolag)

        undervarde_pe = 0.0
        undervarde_ps = 0.0
        if target_pe > 0:
            undervarde_pe = (target_pe - nuvarande_kurs) / target_pe
        if target_ps > 0:
            undervarde_ps = (target_ps - nuvarande_kurs) / target_ps

        # Returnera största undervärdering (i procent)
        undervarde = max(undvarde_pe, undervarde_ps) * 100
        return round(undervarde, 2)
    except Exception:
        return 0.0

def get_current_date_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")
