"""
model_HTML.py

One OfferCard + one OfferCardAcc shared by all plan types.
All fields are pre-formatted strings.
- No register_link
- No icon_url (hardcoded in template)
- cnt_total pre-computed by path functions
- Empty string "" = do not render that row
"""
from __future__ import annotations
from typing import List
from pydantic import BaseModel


class OfferCardAcc(BaseModel):
    acc_no:           str
    acc_name:         str
    os:               str   # "1,234,567.89"
    int_rate:         str   # "5.25"  (no % sign)

    term_old:         str = ""  # "48 งวด"
    term_change:      str = ""  # "36 → 48 งวด"

    inst_old:         str = ""  # "12,345 บาท/งวด"
    inst_change:      str = ""  # "12,345 → 9,876 บาท/งวด"
    inst_change_y1:   str = ""  # "12,345 → 9,876 บาท/งวด"
    inst_y2y3:        str = ""  # "9,876 และ 10,500 บาท/งวด"
    inst_after_3m:    str = ""  # "12,345 บาท/งวด"
    inst_new_loan:    str = ""  # "12,345 บาท"

    balloon_payment:  str = ""  # "23,456.78 บาท"

    int_total_old:    str = ""  # "234,567.89 บาท"
    int_total_change: str = ""  # "234,567.89 → 198,000.00 บาท"

    inelig_note:      str = ""


class OfferCard(BaseModel):
    plan_id:          str
    plan_desc:        str
    ncb_badge:        str = ""

    accounts:         str
    cnt_eligible:     str
    cnt_total:        str
    total_os:         str
    prev_inst:        str
    new_inst:         str
    step_label:       str = ""

    source_desc:      str = ""
    int_rate_new:     str = ""
    term_actual_old:  str = ""
    term_remain_new:  str = ""
    term_change:      str = ""
    inst_y2y3:        str = ""
    inst_after_3m:    str = ""
    int_total_change: str = ""

    balloon_rows:     List[str] = []  # "ACC_NO|TERM|PAYMENT"
    notes:            List[str] = []
    account_details:  List[OfferCardAcc] = []
