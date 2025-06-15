def calculate_targetkurs_pe(bolag):
    try:
        vinst = float(bolag.get("vinst_nastaar", 0))
        pe1 = float(bolag.get("pe1", 0))
        pe2 = float(bolag.get("pe2", 0))
        if vinst > 0 and pe1 > 0 and pe2 > 0:
            return vinst * ((pe1 + pe2) / 2)
    except Exception:
        pass
    return 0

def calculate_targetkurs_ps(bolag):
    try:
        ps1 = float(bolag.get("ps1", 0))
        ps2 = float(bolag.get("ps2", 0))
        oms_tillvaxt_i_ar = float(bolag.get("omsattningstillvaxt_i_ar", 0))
        oms_tillvaxt_nastaar = float(bolag.get("omsattningstillvaxt_nastaar", 0))
        oms_tillvaxt = (oms_tillvaxt_i_ar + oms_tillvaxt_nastaar) / 2 / 100  # procentsats till decimal
        if ps1 > 0 and ps2 > 0:
            avg_ps = (ps1 + ps2) / 2
            return avg_ps * (1 + oms_tillvaxt)
    except Exception:
        pass
    return 0

def calculate_undervardering(bolag):
    try:
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        target_pe = calculate_targetkurs_pe(bolag)
        target_ps = calculate_targetkurs_ps(bolag)
        targets = [t for t in [target_pe, target_ps] if t > 0]
        if not targets or nuvarande_kurs <= 0:
            return 0
        max_target = max(targets)
        undervardering = (max_target - nuvarande_kurs) / max_target * 100
        return round(undervardering, 2)
    except Exception:
        return 0
