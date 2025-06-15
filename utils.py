def calculate_targetkurs_pe(bolag):
    try:
        vinst_i_ar = float(bolag.get("vinst_i_ar", 0))
        vinst_nastaar = float(bolag.get("vinst_nastaar", 0))
        pe_vals = [float(bolag.get(f"pe{i}", 0)) for i in range(1, 5)]
        if not pe_vals or all(p == 0 for p in pe_vals):
            return 0, 0

        snitt_pe = sum(pe_vals) / len(pe_vals)

        target_pe_i_ar = vinst_i_ar * snitt_pe if vinst_i_ar > 0 else 0
        target_pe_nastaar = vinst_nastaar * snitt_pe if vinst_nastaar > 0 else 0

        return target_pe_i_ar, target_pe_nastaar
    except Exception:
        return 0, 0


def calculate_targetkurs_ps(bolag):
    try:
        ps_vals = [float(bolag.get(f"ps{i}", 0)) for i in range(1, 5)]
        nuvarande_ps = float(bolag.get("nuvarande_ps", 0))
        oms_tillvaxt_i_ar = float(bolag.get("omsattningstillvaxt_i_ar", 0)) / 100
        oms_tillvaxt_nastaar = float(bolag.get("omsattningstillvaxt_nastaar", 0)) / 100

        if not ps_vals or nuvarande_ps <= 0:
            return 0

        snitt_ps = sum(ps_vals) / len(ps_vals)
        genomsnitt_tillvaxt = (oms_tillvaxt_i_ar + oms_tillvaxt_nastaar) / 2

        target_ps = (snitt_ps / nuvarande_ps) * (1 + genomsnitt_tillvaxt)

        return round(target_ps, 2)
    except Exception:
        return 0


def calculate_undervardering(bolag):
    try:
        nuvarande_kurs = float(bolag.get("nuvarande_kurs", 0))
        target_pe_i_ar, target_pe_nastaar = calculate_targetkurs_pe(bolag)
        target_ps = calculate_targetkurs_ps(bolag)

        targets = [val for val in [target_pe_i_ar, target_pe_nastaar, target_ps] if val > 0]
        if not targets or nuvarande_kurs <= 0:
            return 0

        max_target = max(targets)
        undervardering = (max_target - nuvarande_kurs) / max_target * 100
        return round(undervardering, 2)
    except Exception:
        return 0
