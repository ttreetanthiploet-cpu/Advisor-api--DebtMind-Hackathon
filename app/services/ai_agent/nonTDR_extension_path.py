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


def create_nonTDR_offer_card(planId, currentStatus, dfOffer) -> OfferCard:
    old_inst = currentStatus["CurrentInstallment"]
    old_int  = currentStatus["expIntTotal"]
    new_int  = dfOffer["expIntTotal"].sum()
    return OfferCard(
        plan_id          = planId,
        plan_desc        = "มาตรการลดค่างวดตามสัญญาคงเหลือ",
        accounts         = ", ".join(sorted(dfOffer["accNo"].tolist())),
        cnt_eligible     = str(int(dfOffer["fg_eligible"].sum())),
        cnt_total        = str(len(dfOffer)),
        total_os         = _f2(currentStatus["TotalOS"]),
        prev_inst        = _f0(old_inst),
        new_inst         = _f0(dfOffer["installment"].sum()),
        term_actual_old  = f"{currentStatus['actualTerm']} งวด",
        term_remain_new  = f"{currentStatus['remainTerm']} งวด",
        int_total_change = f"{_f2(old_int)} → {_f2(new_int)} บาท",
    )


def create_nTDRoffer_cardAcc(solutionAcc, originalAcc, fgEligible) -> OfferCardAcc:
    if fgEligible:
        return OfferCardAcc(
            acc_no           = solutionAcc.get("refAccNo", ""),
            acc_name         = originalAcc.get("port", ""),
            os               = _f2(solutionAcc.get("os", 0)),
            int_rate         = _pct(solutionAcc.get("intRate", 0)),
            term_old         = f"{originalAcc.get('term')} งวด",
            int_total_change = f"{_f2(originalAcc['expIntTotal'])} → {_f2(solutionAcc['expIntTotal'])} บาท",
        )
    else:
        return OfferCardAcc(
            acc_no        = solutionAcc.get("refAccNo", ""),
            acc_name      = originalAcc.get("port", ""),
            os            = _f2(solutionAcc.get("os", 0)),
            int_rate      = _pct(solutionAcc.get("intRate", 0)),
            term_old      = f"{originalAcc.get('term')} งวด",
            inst_old      = f"{_f0(originalAcc['installment'])} บาท/งวด",
            int_total_old = f"{_f2(originalAcc['expIntTotal'])} บาท",
            inelig_note   = "บัญชีนี้ไม่เข้าเกณฑ์เข้าร่วมมาตรการ จึงคงเงื่อนไขการชำระตามเดิม",
        )


def product_nonTDR_Extsummary(planId, currentStatus, dfAccConsult, dfOffer, solutionDesc) -> DebtSolnSummary:
    plan = "NTDREXT"
    dfOfferAcc = (dfOffer[dfOffer["fg_eligible"]]
                  [["accNo","os","installment","intRate","remainTerm","expIntTotal"]]
                  .copy().rename(columns={"accNo":"refAccNo","remainTerm":"term"}))
    dfOfferAcc[["plan","planId"]] = plan, planId
    old_inst = currentStatus["CurrentInstallment"]
    old_int  = currentStatus["expIntTotal"]
    description = (
        f"ข้อเสนอ {planId}: มาตรการลดอัตราการผ่อนชำระตามสัญญาคงเหลือ\n"
        f"บัญชีที่พิจารณา: {', '.join(sorted(dfOffer['accNo'].tolist()))}\n"
        f"บัญชีที่เข้าร่วม: {', '.join(sorted(dfOffer[dfOffer['fg_eligible']]['accNo'].tolist()))}\n"
        f"ค่างวด: {_f2(old_inst)} → {_f2(dfOffer['installment'].sum())} บาท/งวด\n"
        f"ดอกเบี้ยรวม: {_f2(old_int)} → {_f2(dfOffer['expIntTotal'].sum())} บาท\n"
    )
    card     = create_nonTDR_offer_card(planId, currentStatus, dfOffer)
    solnList = [DebtSolnAcc(**a).model_dump() for a in dfOfferAcc.to_dict(orient="records")]
    lookup   = {a["refAccNo"]: a for a in solnList}
    for ori in dfAccConsult.rename(columns={"accNo":"refAccNo","remainTerm":"term"}).to_dict(orient="records"):
        key = ori["refAccNo"]
        card.account_details.append(
            create_nTDRoffer_cardAcc(lookup[key], ori, True) if key in lookup
            else create_nTDRoffer_cardAcc(ori, ori, False))
    return DebtSolnSummary(**{
        "solutionDesc":solutionDesc,"plan":plan,"planId":planId,
        "refAccNo":", ".join(sorted(dfOffer["accNo"].tolist())),
        "planDesc":"ลดค่างวดตามสัญญาคงเหลือ",
        "installment":dfOffer["installment"].sum(),"term":dfOffer["installment"].max(),
        "totalIntPaid":dfOffer["expIntTotal"].sum(),"constantPayment":False,
        "offerText":description,"offerCard":card.model_dump(),"solnAcc":solnList,
    })


def generate_nonTDR_extension_offer(currentStatus, dfAccConsult) -> list[DebtSolnSummary]:
    dfAcc  = dfAccConsult.copy()
    planId = "NTDREXT01" + dt.datetime.now().strftime("%Y%m%d%H%M%S")
    dfAcc["actualTerm"]  = dfAcc.apply(lambda r: findTerm(r["os"], r["intRate"], r["installment"]), axis=1)
    dfAcc["expIntTotal"] = dfAcc.apply(lambda r: findInterestPaid(r["os"], r["intRate"]/12, r["installment"], r["actualTerm"]), axis=1)
    dfElig    = dfAcc[dfAcc["actualTerm"] <  dfAcc["remainTerm"]].copy()
    dfNonElig = dfAcc[dfAcc["actualTerm"] >= dfAcc["remainTerm"]].copy()
    dfNonElig["fg_eligible"] = False
    dfNonElig["expIntTotal"] = dfNonElig.apply(lambda r: findInterestPaid(r["os"], r["intRate"]/12, r["installment"], r["actualTerm"]), axis=1)
    if len(dfElig) == 0:
        return []
    req = ["accNo","currentDPD","os","accruedInt","intRate","remainTerm","expIntTotal"]
    dfElig = dfElig[req].copy()
    dfElig["installment"]  = dfElig.apply(lambda r: findInstallment(r["os"], r["intRate"], r["remainTerm"]), axis=1)
    dfElig["fg_eligible"]  = True
    dfElig["expIntTotal"]  = dfElig.apply(lambda r: findInterestPaid(r["os"], r["intRate"]/12, r["installment"], r["remainTerm"]), axis=1)
    dfOffer = pd.concat([dfElig, dfNonElig[req + ["installment","fg_eligible"]]])
    return [product_nonTDR_Extsummary(planId, currentStatus, dfAcc, dfOffer, "ลดค่างวดตามสัญญาคงเหลือ")]
