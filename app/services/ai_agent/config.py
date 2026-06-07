PL_MOU_interest_map = {'ข้าราชการ' : 0.06,
                       'พนักงานเงินเดือน' : 0.0875}

#PL_MOU_maxPaymentTerm = 60 #Maximum Payment Term of a given loan

TDR_maxPaymentTerm = 60
TDRmin_payment_prop = 0.05
PossibleTDRLoan = ["สินเชื่อดิจิตอลส่วนบุคคล",
                   "สินเชื่อส่วนบุคคล"]

Min_MOB_to_GDR = 12

PreferenceRANKING = {
    # ── DebtBurden ────────────────────────────────────────────────────────────
    ("DebtBurden", "C1"): [
        "PLMOU01", "PLMOU03", "PLMOU02", "NTDREXT",
        "TDR02", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR",
    ],
    ("DebtBurden", "C2"): [
        "TDR02", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("DebtBurden", "C3"): [
        "TDR02", "TDR04", "TDR08",
        "TDR05", "TDR03", "TDR09", "TDR07", "TDR06", "TDR01",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],

    # ── TemporaryCashflow ─────────────────────────────────────────────────────
    ("TemporaryCashflow", "C1"): [
        "NTDREXT", "GDR",
        "TDR02", "TDR04", "TDR06", "TDR08",
        "TDR03", "TDR05", "TDR07", "TDR09", "TDR01",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("TemporaryCashflow", "C2"): [
        "TDR02", "GDR",
        "TDR04", "TDR06", "TDR08",
        "TDR03", "TDR05", "TDR07", "TDR09", "TDR01",
        "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("TemporaryCashflow", "C3"): [
        "GDR", "TDR02",
        "TDR05", "TDR03", "TDR07", "TDR09",
        "TDR04", "TDR06", "TDR08", "TDR01",
        "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],

    # ── PermanentAffordability ────────────────────────────────────────────────
    ("PermanentAffordability", "C1"): [
        "TDR02", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("PermanentAffordability", "C2"): [
        "TDR02", "TDR04", "TDR08",
        "TDR03", "TDR05", "TDR06", "TDR09", "TDR07", "TDR01",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("PermanentAffordability", "C3"): [
        "TDR02",
        "TDR05", "TDR03", "TDR09", "TDR08", "TDR04", "TDR07", "TDR06", "TDR01",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],

    # ── CareerChange ──────────────────────────────────────────────────────────
    ("CareerChange", "C1"): [
        "PLMOU02", "NTDREXT", "PLMOU03",
        "TDR04", "TDR06", "TDR08",
        "TDR02", "TDR03", "TDR05", "TDR07", "TDR09", "TDR01",
        "PLMOU01", "GDR",
    ],
    ("CareerChange", "C2"): [
        "TDR04", "TDR06", "TDR08",
        "TDR02", "TDR03", "TDR05", "TDR07", "TDR09", "TDR01",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("CareerChange", "C3"): [
        "TDR04", "TDR08", "TDR06",
        "TDR05", "TDR09",
        "TDR02", "TDR03", "TDR07", "TDR01",
        "GDR", "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],

    # ── FinancialShock ────────────────────────────────────────────────────────
    ("FinancialShock", "C1"): [
        "GDR",
        "TDR01", "TDR03", "TDR05",
        "TDR02", "TDR04", "TDR07", "TDR09", "TDR08", "TDR06",
        "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("FinancialShock", "C2"): [
        "TDR01", "TDR03", "TDR05", "GDR",
        "TDR02", "TDR04", "TDR07", "TDR09", "TDR08", "TDR06",
        "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
    ("FinancialShock", "C3"): [
        "TDR01", "TDR05", "TDR03", "TDR09", "TDR07", "GDR",
        "TDR02", "TDR04", "TDR08", "TDR06",
        "NTDREXT",
        "PLMOU02", "PLMOU03", "PLMOU01",
    ],
}