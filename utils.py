# utils.py

def berakna_targetkurs_pe(vinst_nastaar, pe1, pe2):
    """
    Beräkna targetkurs baserat på P/E.
    Targetkurs = Vinst nästa år * medelvärde av PE1 och PE2
    """
    try:
        pe_medel = (float(pe1) + float(pe2)) / 2
        targetkurs_pe = float(vinst_nastaar) * pe_medel
        return round(targetkurs_pe, 2)
    except (TypeError, ValueError):
        return None


def berakna_targetkurs_ps(nuvarande_ps, ps1, ps2, omsattningstillvaxt1, omsattningstillvaxt2, nuvarande_kurs):
    """
    Beräkna targetkurs baserat på P/S.
    Targetkurs = medelvärde av P/S år 1 och 2 * medelvärde av omsättningstillväxt år 1 och 2 * nuvarande kurs
    """
    try:
        ps_medel = (float(ps1) + float(ps2)) / 2
        oms_tillv_medel = (float(omsattningstillvaxt1) + float(omsattningstillvaxt2)) / 2 / 100
        targetkurs_ps = ps_medel * (1 + oms_tillv_medel) * float(nuvarande_kurs)
        return round(targetkurs_ps, 2)
    except (TypeError, ValueError):
        return None


def berakna_undervardering(nuvarande_kurs, targetkurs_pe, targetkurs_ps):
    """
    Beräkna undervärdering i procent baserat på nuvarande kurs och targetkurser.
    Returnerar den högsta undervärderingen av P/E eller P/S i procent.
    """
    undervarderinger = []

    try:
        if targetkurs_pe and targetkurs_pe > 0:
            undervardering_pe = (targetkurs_pe - float(nuvarande_kurs)) / targetkurs_pe * 100
            undervarderinger.append(undervardering_pe)
    except (TypeError, ValueError):
        pass

    try:
        if targetkurs_ps and targetkurs_ps > 0:
            undervardering_ps = (targetkurs_ps - float(nuvarande_kurs)) / targetkurs_ps * 100
            undervarderinger.append(undervardering_ps)
    except (TypeError, ValueError):
        pass

    if undervarderinger:
        return round(max(undervarderinger), 2)
    else:
        return None
