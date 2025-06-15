def calculate_targetkurs_pe(bolag, nästa=False):
    try:
        vinst_key = "vinst_nastaar" if nästa else "vinst_i_ar"
        vinst = float(bolag.get(vinst_key, 0))
        pe_values = [float(bolag.get(f"pe{i}", 0)) for i in range(1, 5)]
        pe_values = [v for v in pe_values if v > 0]
        if vinst > 0 and pe_values:
            return vinst * (sum(pe_values) / len(pe_values))
    except Exception:
        pass
    return 0

def calculate_targetkurs_ps(bolag, nästa=False):
    try:
        tillvaxt_key = "omsattningstillvaxt_nastaar" if nästa else "omsattningstillvaxt_i_ar"
        tillvaxt_procent = float(bolag.get(tillvaxt_key, 0))
        tillvaxt_faktor = 1 + tillvaxt_procent / 100

        nuvarande_ps = float(bolag.get("nuvarande_ps", 0))
        ps_values = [float(bolag.get(f"ps{i}", 0)) for i in range(1, 5)]
        ps_values = [v for v in ps_values if v > 0]

        if ps_values and nuvarande_ps > 0:
            snitt_ps = sum(ps_values) / len(ps_values)
            return (snitt_ps / nuvarande_ps) * tillvaxt_faktor * nuvarande_ps
    except Exception:
        pass
    return 0

def calculate_undervardering(bolag):
    try:
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        target_pe = calculate_targetkurs_pe(bolag, nästa=True)
        target_ps = calculate_targetkurs_ps(bolag, nästa=True)
        targets = [t for t in [target_pe, target_ps] if t > 0]
        if not targets or nuvarande_kurs <= 0:
            return 0
        max_target = max(targets)
        undervardering = (max_target - nuvarande_kurs) / max_target * 100
        return round(undervardering, 2)
    except Exception:
        return 0
