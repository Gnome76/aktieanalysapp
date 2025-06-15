def calculate_targetkurs_pe(bolag):
    """
    Beräkna targetkurs baserat på snitt av P/E 1-4 multiplicerat med förväntad vinst i år och nästa år.
    Returnerar medelvärdet av dessa två beräkningar.
    """
    try:
        pe_vals = [
            float(bolag.get(f"pe{i}", 0)) 
            for i in range(1, 5)
            if bolag.get(f"pe{i}", None) is not None
        ]
        vinst_i_ar = float(bolag.get("vinst_i_ar", 0))
        vinst_nastaar = float(bolag.get("vinst_nastaar", 0))

        if not pe_vals or vinst_i_ar <= 0 or vinst_nastaar <= 0:
            return 0

        snitt_pe = sum(pe_vals) / len(pe_vals)
        
        target_i_ar = snitt_pe * vinst_i_ar
        target_nastaar = snitt_pe * vinst_nastaar

        return (target_i_ar + target_nastaar) / 2
    except Exception:
        return 0


def calculate_targetkurs_ps(bolag):
    """
    Beräkna targetkurs baserat på snitt av P/S 1-4 delat med nuvarande P/S multiplicerat med
    (1 + genomsnittlig omsättningstillväxt i år och nästa år).
    """
    try:
        ps_vals = [
            float(bolag.get(f"ps{i}", 0)) 
            for i in range(1, 5)
            if bolag.get(f"ps{i}", None) is not None
        ]
        nuvarande_ps = float(bolag.get("nuvarande_ps", 0))
        oms_tillvaxt_i_ar = float(bolag.get("omsattningstillvaxt_i_ar", 0)) / 100
        oms_tillvaxt_nastaar = float(bolag.get("omsattningstillvaxt_nastaar", 0)) / 100

        if not ps_vals or nuvarande_ps <= 0:
            return 0
        
        snitt_ps = sum(ps_vals) / len(ps_vals)
        genomsnitt_tillvaxt = (oms_tillvaxt_i_ar + oms_tillvaxt_nastaar) / 2

        target_ps = (snitt_ps / nuvarande_ps) * (1 + genomsnitt_tillvaxt)
        return target_ps
    except Exception:
        return 0


def calculate_undervardering(bolag):
    """
    Beräkna undervärdering i procent baserat på nuvarande kurs och targetkurser.
    Tar det högsta värdet av target P/E och target P/S och räknar ut hur mycket kursen är undervärderad.
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
