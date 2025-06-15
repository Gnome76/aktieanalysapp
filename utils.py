def calculate_targetkurs_pe(bolag, nästa=False):
    """
    Beräknar targetkurs baserat på P/E för i år (nästa=False) eller nästa år (nästa=True).
    Snittar P/E 1-4 och multiplicerar med vinst i år eller nästa år.
    """
    try:
        pe_values = [float(bolag.get(f"pe{i}", 0)) for i in range(1,5)]
        pe_values = [v for v in pe_values if v > 0]
        if not pe_values:
            return 0
        snitt_pe = sum(pe_values) / len(pe_values)

        if nästa:
            vinst = float(bolag.get("vinst_nastaar", 0))
        else:
            vinst = float(bolag.get("vinst_i_ar", 0))

        if vinst <= 0:
            return 0

        targetkurs_pe = snitt_pe * vinst
        return round(targetkurs_pe, 2)
    except Exception:
        return 0


def calculate_targetkurs_ps(bolag):
    """
    Beräknar targetkurs baserat på P/S:
    - Snitt av P/S 1-4
    - Dividerat med nuvarande P/S
    - Multiplicerat med nuvarande kurs
    - Multiplicerat med (1 + genomsnittlig omsättningstillväxt i år och nästa år)
    """
    try:
        ps_values = [float(bolag.get(f"ps{i}", 0)) for i in range(1,5)]
        ps_values = [v for v in ps_values if v > 0]
        if not ps_values:
            return 0

        snitt_ps = sum(ps_values) / len(ps_values)
        nuvarande_ps = float(bolag.get("nuvarande_ps", 0))
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        oms_tillvaxt_i_ar = float(bolag.get("omsattningstillvaxt_i_ar", 0))
        oms_tillvaxt_nastaar = float(bolag.get("omsattningstillvaxt_nastaar", 0))

        if nuvarande_ps <= 0 or nuvarande_kurs <= 0:
            return 0

        oms_tillvaxt = (oms_tillvaxt_i_ar + oms_tillvaxt_nastaar) / 200  # procentsats till decimal & snitt av två år

        targetkurs_ps = nuvarande_kurs * (snitt_ps / nuvarande_ps) * (1 + oms_tillvaxt)
        return round(targetkurs_ps, 2)
    except Exception:
        return 0


def calculate_undervardering(bolag):
    """
    Beräknar undervärdering i procent baserat på max av targetkurser P/E och P/S.
    """
    try:
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        target_pe_i_ar = calculate_targetkurs_pe(bolag, nästa=False)
        target_pe_nasta_ar = calculate_targetkurs_pe(bolag, nästa=True)
        target_ps = calculate_targetkurs_ps(bolag)

        targets = [v for v in [target_pe_i_ar, target_pe_nasta_ar, target_ps] if v > 0]
        if not targets or nuvarande_kurs <= 0:
            return 0

        max_target = max(targets)
        undervardering = (max_target - nuvarande_kurs) / max_target * 100
        return round(undervardering, 2)
    except Exception:
        return 0
