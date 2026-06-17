#PL_MOU_maxPaymentTerm = 60 #Maximum Payment Term of a given loan

TDR_maxPaymentTerm = 120
TDRmin_payment_prop = 0.05
PossibleTDRLoan = ["สินเชื่อส่วนบุคคล",
                   "สินเชื่อกรุงไทยใจป้ำ",
                   "สินเชื่ออเนกประสงค์ 5 Plus",
                   "สินเชื่ออเนกประสงค์",
                   "สินเชื่ออเนกประสงค์ Money Prompt",
                   "สินเชื่อ 100K" ]

Min_MOB_to_GDR = 12

PreferenceRANKING = {
    # ── DebtBurden ────────────────────────────────────────────────────────────
    ("DebtBurden", "C1-X"): [
        "CSL01", "CSL03", "CSL02", "EXT",
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR",
    ],
    ("DebtBurden", "Current"): [
        "CSL02", "CSL03", "CSL01", "EXT",
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR",
    ],
    ("DebtBurden", "C2"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("DebtBurden", "C3"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR03", "TDR05", "TDR09", "TDR07", "TDR06", "TDR01",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],

    # ── TemporaryCashflow ─────────────────────────────────────────────────────
    ("TemporaryCashflow", "C1-X"): [
        "EXT", "GDR",
        "TDR02", "TDR10", "TDR04", "TDR06", "TDR08",
        "TDR03", "TDR05", "TDR07", "TDR09", "TDR01",
        "CSL02", "CSL03", "CSL01",
    ],
    ("TemporaryCashflow", "Current"): [
        "EXT",
        "TDR02", "TDR10", "TDR04", "TDR06", "TDR08",
        "TDR01", "GDR",
        "TDR03", "TDR05", "TDR07", "TDR09",
        "CSL02", "CSL03", "CSL01",
    ],
    ("TemporaryCashflow", "C2"): [
        "TDR02", "TDR10", "TDR04", "TDR06", "TDR08",
        "TDR01", "TDR03", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("TemporaryCashflow", "C3"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR03", "TDR05", "TDR09", "TDR07", "TDR06", "TDR01",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],

    # ── PermanentAffordability ────────────────────────────────────────────────
    ("PermanentAffordability", "C1-X"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("PermanentAffordability", "Current"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR06", "TDR03", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("PermanentAffordability", "C2"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR06", "TDR03", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("PermanentAffordability", "C3"): [
        "TDR02", "TDR10",
        "TDR05", "TDR03", "TDR09", "TDR08", "TDR04", "TDR07", "TDR06", "TDR01",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],

    # ── CareerChange ──────────────────────────────────────────────────────────
    ("CareerChange", "C1-X"): [
        "CSL02", "EXT", "CSL03",
        "TDR04", "TDR06", "TDR08",
        "TDR02", "TDR10", "TDR03", "TDR05", "TDR07", "TDR09", "TDR01",
        "CSL01", "GDR",
    ],
    ("CareerChange", "Current"): [
        "CSL02", "CSL03", "CSL01", "EXT",
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR",
    ],
    ("CareerChange", "C2"): [
        "TDR02", "TDR10", "TDR04", "TDR08",
        "TDR01", "TDR03", "TDR06", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("CareerChange", "C3"): [
        "TDR04", "TDR08", "TDR06",
        "TDR05", "TDR09",
        "TDR02", "TDR10", "TDR03", "TDR07", "TDR01",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],

    # ── FinancialShock ────────────────────────────────────────────────────────
    ("FinancialShock", "C1-X"): [
        "GDR",
        "TDR01", "TDR03", "TDR05",
        "TDR02", "TDR10", "TDR04", "TDR07", "TDR09", "TDR08", "TDR06",
        "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("FinancialShock", "Current"): [
        "GDR", "EXT",
        "TDR02", "TDR10", "TDR01", "TDR03",
        "TDR04", "TDR06", "TDR08", "TDR05", "TDR07", "TDR09",
        "CSL02", "CSL03", "CSL01",
    ],
    ("FinancialShock", "C2"): [
        "TDR02", "TDR10", "TDR01", "TDR03",
        "TDR04", "TDR06", "TDR08", "TDR05", "TDR07", "TDR09",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
    ("FinancialShock", "C3"): [
        "TDR01", "TDR05", "TDR03", "TDR09", "TDR07",
        "TDR02", "TDR10", "TDR04", "TDR08", "TDR06",
        "GDR", "EXT",
        "CSL02", "CSL03", "CSL01",
    ],
}