"""nonTDR_extension_path.py"""
from __future__ import annotations
import datetime as dt
import pandas as pd
from app.services.functions.AmortiseCal import findInstallment, findInterestPaid, findTerm
from app.services.HTML.model_HTML import OfferCard, OfferCardAcc
from app.services.model import DebtSolnAcc, DebtSolnSummary

_f0  = lambda n: f"{n:,.0f}"
_f2  = lambda n: f"{n:,.2f}"
_pct = lambda n: f"{100*n:,.2f}"


def create_nonTDR_offer_card(planId : str, 
                             dfAccCurrent : pd.DataFrame, 
                             dfOffer : pd.DataFrame) -> OfferCard:
    return OfferCard(
        plan_id          = planId,
        plan_desc        = "มาตรการลดค่างวดตามสัญญาคงเหลือ",
        step_label       = "โดยคงสัญญาการผ่อนชำระเดิม",
        accounts         = ", ".join(sorted(dfOffer["accNo"].tolist())),
        cnt_eligible     = str(int(dfOffer["fg_eligible"].sum())),
        cnt_total        = str(len(dfOffer)),
        total_os         = _f2(dfAccCurrent["os"].sum()),
        prev_inst        = _f0(dfAccCurrent["installment"].sum()),
        new_inst         = _f0(dfOffer["installment"].sum()),
        term_change  = f"อ้างอิงตามอัตราผ่อนชำระในสัญญาเดิม",
        int_total_change = f"{_f2(dfAccCurrent["expIntTotal"].sum())} → {_f2(dfOffer["expIntTotal"].sum())} บาท",
    )


def create_nTDRoffer_cardAcc(accOffer: pd.Series, 
                             accOri: pd.Series) -> OfferCardAcc:
    fgEligible = accOffer["fg_eligible"]
    if fgEligible:
        return OfferCardAcc(
            acc_no           = accOri["accNo"],
            acc_name         = accOri["port"],
            os               = _f2(accOri["os"]),
            int_rate         = _pct(accOri["intRate"]),
            term_old         = f"{accOri['remainTerm']} งวด",
            inst_change     = f"{_f2(accOri['installment'])} → {_f2(accOffer['installment'])} บาท/งวด",
            int_total_change = f"{_f2(accOri['expIntTotal'])} → {_f2(accOffer['expIntTotal'])} บาท",
        )
    else:
        return OfferCardAcc(
            acc_no        = accOri["accNo"],
            acc_name      = accOri["port"],
            os            = _f2(accOri["os"]),
            int_rate      = _pct(accOri["intRate"]),
            term_old      = f"{accOri['remainTerm']} งวด",
            inst_old      = f"{_f0(accOri['installment'])} บาท/งวด",
            int_total_old = f"{_f2(accOri['expIntTotal'])} บาท",
            inelig_note   = "บัญชีนี้ไม่เข้าเกณฑ์เข้าร่วมมาตรการ จึงคงเงื่อนไขการชำระตามเดิม",
        )


def product_nonTDR_Extsummary(planId: str, 
                            dfAccCurrent: pd.DataFrame,
                            dfOffer: pd.DataFrame) -> DebtSolnSummary:
    plan  = "EXT"
    card = create_nonTDR_offer_card(planId = planId, 
                                    dfAccCurrent = dfAccCurrent, 
                                    dfOffer = dfOffer)
    solnList = [DebtSolnAcc(**{**a, 'planId': planId, 
                               'plan': plan}).model_dump() for a in dfOffer.rename(columns={"accNo":"refAccNo", 
                                                                                            "remainTerm":"term"}).to_dict(orient="records")]
    
    for i in range(len(dfOffer)):
        accOffer = dfOffer.iloc[i]
        accOri = dfAccCurrent.iloc[i]
        card.account_details.append(create_nTDRoffer_cardAcc(accOffer = accOffer, 
                                                             accOri = accOri))
    return DebtSolnSummary(**{
        "solutionDesc":"พักชำระเงินต้น",
        "plan":plan,
        "planId":planId,
        "refAccNo":", ".join(sorted(dfOffer["accNo"].tolist())),
        "planDesc":"พักชำระเงินต้น",
        "installment":dfOffer["installment"].sum(),
        "term":dfOffer["actualTerm"].max(),
        "totalIntPaid":dfOffer["expIntTotal"].sum(),
        "constantPayment":False,
        "offerCard":card.model_dump(),
        "solnAcc":solnList,})


def generate_nonTDR_extension_offer(currentStatus: dict) -> list[DebtSolnSummary]:
    dfOffer  = currentStatus["current_debt"].copy()
    planId = "EXT01" + dt.datetime.now().strftime("%Y%m%d%H%M%S")
    dfOffer["fg_eligible"] = (dfOffer["actualTerm"] <  dfOffer["remainTerm"])
    if dfOffer["fg_eligible"].sum() == 0:
        return []
    dfOffer["installment_ext"]  = dfOffer.apply(lambda r: findInstallment(r["os"], r["intRate"], r["remainTerm"]), axis=1)
    dfOffer["expIntTotal_ext"] = dfOffer.apply(lambda r: findInterestPaid(r["os"], r["intRate"]/12, r["installment_ext"], r["remainTerm"]), axis=1)
    dfOffer.loc[dfOffer["fg_eligible"], "installment"]  = dfOffer["installment_ext"]
    dfOffer.loc[dfOffer["fg_eligible"], "expIntTotal"]  = dfOffer["expIntTotal_ext"]
    return [product_nonTDR_Extsummary(planId = planId, 
                                      dfAccCurrent = currentStatus["current_debt"],
                                      dfOffer = dfOffer)]