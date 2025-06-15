def calculate_targetkurs_pe(bolag):
    try:
        vinst_nasta_aar = bolag.get("vinst_nasta_aar", 0)
        pe1 = bolag.get("pe1", 0)
        pe2 = bolag.get("pe2", 0)
        if pe1 > 0 and pe2 > 0:
            return vinst_nasta_aar * ((pe1 + pe2) / 2)
        else:
            return 0
    except Exception:
        return 0


def calculate_targetkurs_ps(bolag):
    try:
        ps1 = bolag.get("ps1", 0)
        ps2 = bolag.get("ps2", 0)
        omsattningstillvxt_i_aar = bolag.get("omsattningstillvxt_i_aar", 0) / 100
        omsattningstillvxt_nasta_aar = bolag.get("omsattningstillvxt_nasta_aar", 0) / 100
        omsattningstillvxt_medel = (omsattningstillvxt_i_aar + omsattningstillvxt_nasta_aar) / 2
        kurs = bolag.get("kurs", 0)
        if ps1 > 0 and ps2 > 0:
            medel_ps = (ps1 + ps2) / 2
            return medel_ps * (1 + omsattningstillvxt_medel) * kurs
        else:
            return 0
    except Exception:
        return 0


def calculate_undervardering(bolag):
    try:
        kurs = bolag.get("kurs", 0)
        target_pe = bolag.get("targetkurs_pe", 0)
        target_ps = bolag.get("targetkurs_ps", 0)
        if target_pe > 0 and target_ps > 0:
            undervardering_pe = max(0, (target_pe - kurs) / target_pe * 100)
            undervardering_ps = max(0, (target_ps - kurs) / target_ps * 100)
            return max(undervardering_pe, undervardering_ps)
        else:
            return 0
    except Exception:
        return 0
