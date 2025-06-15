def berakna_targetkurs_pe(bolag):
    # Targetkurs baserat på genomsnitt av pe_1 och pe_2 * vinst nästa år
    pe1 = bolag.get("pe_1", 0)
    pe2 = bolag.get("pe_2", 0)
    vinst_nastaar = bolag.get("vinst_nastaar", 0)
    if pe1 and pe2 and vinst_nastaar:
        target_pe = vinst_nastaar * ((pe1 + pe2) / 2)
        return round(target_pe, 2)
    return None

def berakna_targetkurs_ps(bolag):
    # Targetkurs baserat på genomsnitt P/S 1 och 2 * genomsnitt omsättningstillväxt * nuvarande kurs
    ps1 = bolag.get("ps_1", 0)
    ps2 = bolag.get("ps_2", 0)
    omsattningstillvaxt_aret = bolag.get("omsattningstillvaxt_aret", 0)
    omsattningstillvaxt_nastaar = bolag.get("omsattningstillvaxt_nastaar", 0)
    nuvarande_kurs = bolag.get("nuvarande_kurs", 0)
    if ps1 and ps2 and nuvarande_kurs:
        oms_tillvaxt_genomsnitt = (omsattningstillvaxt_aret + omsattningstillvaxt_nastaar) / 2 / 100  # från % till decimal
        target_ps = ((ps1 + ps2) / 2) * (1 + oms_tillvaxt_genomsnitt) * nuvarande_kurs
        return round(target_ps, 2)
    return None

def berakna_undervardering(bolag):
    nuvarande_kurs = bolag.get("nuvarande_kurs", 0)
    target_pe = berakna_targetkurs_pe(bolag)
    target_ps = berakna_targetkurs_ps(bolag)

    undervardering_pe = ((target_pe - nuvarande_kurs) / target_pe) * 100 if target_pe else None
    undervardering_ps = ((target_ps - nuvarande_kurs) / target_ps) * 100 if target_ps else None

    # Returnera största undervärdering
    undervarderingar = [u for u in [undervardering_pe, undervardering_ps] if u is not None]
    if undervarderingar:
        return round(max(undervarderingar), 2)
    return None
