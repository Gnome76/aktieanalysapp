def calculate_targetkurs_pe(bolag):
    """
    Beräkna targetkurs baserat på snitt av P/E 1-4 multiplicerat med vinst i år och nästa år.
    Returnerar medelvärde av dessa två beräkningar.
    """
    try:
        vinst_i_ar = float(bolag.get("vinst_i_ar", 0))
        vinst_nastaar = float(bolag.get("vinst_nastaar", 0))
        pe1 = float(bolag.get("pe1", 0))
        pe2 = float(bolag.get("pe2", 0))
        pe3 = float(bolag.get("pe3", 0))
        pe4 = float(bolag.get("pe4", 0))
        
        pe_list = [pe for pe in [pe1, pe2, pe3, pe4] if pe > 0]
        if not pe_list:
            return 0
        snitt_pe = sum(pe_list) / len(pe_list)
        
        target_i_ar = vinst_i_ar * snitt_pe if vinst_i_ar > 0 else 0
        target_nastaar = vinst_nastaar * snitt_pe if vinst_nastaar > 0 else 0
        
        targets = [t for t in [target_i_ar, target_nastaar] if t > 0]
        if not targets:
            return 0
        
        return sum(targets) / len(targets)
    except Exception:
        return 0


def calculate_targetkurs_ps(bolag):
    """
    Beräkna targetkurs baserat på snitt av P/S 1-4, dividerat med nuvarande P/S,
    multiplicerat med omsättningstillväxt i år och nästa år (adderat som procentsatser).
    """
    try:
        ps1 = float(bolag.get("ps1", 0))
        ps2 = float(bolag.get("ps2", 0))
        ps3 = float(bolag.get("ps3", 0))
        ps4 = float(bolag.get("ps4", 0))
        nuvarande_ps = float(bolag.get("nuvarande_ps", 0))
        
        oms_tillvaxt_i_ar = float(bolag.get("omsattningstillvaxt_i_ar", 0)) / 100
        oms_tillvaxt_nastaar = float(bolag.get("omsattningstillvaxt_nastaar", 0)) / 100
        
        ps_list = [ps for ps in [ps1, ps2, ps3, ps4] if ps > 0]
        if not ps_list or nuvarande_ps <= 0:
            return 0
        snitt_ps = sum(ps_list) / len(ps_list)
        
        oms_tillvaxt_total = oms_tillvaxt_i_ar + oms_tillvaxt_nastaar
        
        target_ps = (snitt_ps / nuvarande_ps) * (1 + oms_tillvaxt_total)
        
        return target_ps
    except Exception:
        return 0


def calculate_undervardering(bolag):
    """
    Beräknar undervärdering i procent baserat på högsta targetkurs av P/E och P/S jämfört med nuvarande kurs.
    """
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
