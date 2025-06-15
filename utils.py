def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def calculate_targetkurs_pe(bolag, nästa=False):
    """
    Beräknar targetkurs baserat på P/E snitt och vinst.
    Om nästa=True används vinst nästa år, annars årets vinst.
    P/E tas som snitt av pe1-pe4.
    """
    vinst_key = "vinst_nastaar" if nästa else "vinst_i_ar"
    vinst = safe_float(bolag.get(vinst_key))
    pe_list = [safe_float(bolag.get(f"pe{i}")) for i in range(1, 5)]
    pe_list = [pe for pe in pe_list if pe > 0]

    if vinst > 0 and pe_list:
        pe_avg = sum(pe_list) / len(pe_list)
        return vinst * pe_avg
    return 0.0

def calculate_targetkurs_ps(bolag, nästa=False):
    """
    Beräknar targetkurs baserat på P/S och omsättningstillväxt.
    P/S tas som snitt av ps1-ps4.
    Omsättningstillväxt i år och nästa år tas som decimal (t.ex. 0.19 för 19%).
    Multipliceras med nuvarande p/s och nuvarande kurs.
    Om nästa=True används omsättningstillväxt nästa år, annars i år.
    """
    ps_list = [safe_float(bolag.get(f"ps{i}")) for i in range(1, 5)]
    ps_list = [ps for ps in ps_list if ps > 0]
    nuvarande_ps = safe_float(bolag.get("nuvarande_ps"))

    oms_tillvaxt_i_ar = safe_float(bolag.get("omsattningstillvaxt_i_ar"), 0) / 100
    oms_tillvaxt_nastaar = safe_float(bolag.get("omsattningstillvaxt_nastaar"), 0) / 100

    oms_tillvaxt = oms_tillvaxt_nastaar if nästa else oms_tillvaxt_i_ar

    if nuvarande_ps <= 0 or not ps_list:
        return 0.0

    ps_avg = sum(ps_list) / len(ps_list)

    nuvarande_kurs = safe_float(bolag.get("nuvarande_kurs"))

    target = (ps_avg / nuvarande_ps) * (1 + oms_tillvaxt) * nuvarande_kurs
    return target if target > 0 else 0.0

def calculate_undervardering(bolag):
    """
    Beräknar undervärdering baserat på max av targetkurs P/E och P/S.
    Returnerar procentuell undervärdering.
    """
    nuvarande_kurs = safe_float(bolag.get("nuvarande_kurs"))
    target_pe = calculate_targetkurs_pe(bolag)
    target_ps = calculate_targetkurs_ps(bolag)

    targets = [t for t in [target_pe, target_ps] if t > 0]

    if not targets or nuvarande_kurs <= 0:
        return 0.0

    max_target = max(targets)
    undervardering = (max_target - nuvarande_kurs) / max_target * 100
    return round(undervardering, 2)
