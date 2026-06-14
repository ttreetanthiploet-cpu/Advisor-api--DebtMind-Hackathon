"""GDR_path.py"""
from __future__ import annotations
import datetime as dt
import pandas as pd
from app.services.ai_agent.config import Min_MOB_to_GDR
from app.services.functions.AmortiseCal import findInterestPaid, findTerm
from app.services.HTML.model_HTML import OfferCard, OfferCardAcc
from app.services.model import DebtSolnAcc, DebtSolnSummary

_f0  = lambda n: f"{n:,.0f}"
_f2  = lambda n: f"{n:,.2f}"
_pct = lambda n: f"{100*n:,.2f}"
_NOTE = "มาตรการนี้สำหรับผู้ที่ไม่เคยมีประวัติค้างชำระกับธนาคารเท่านั้น หากเจ้าหน้าที่ตรวจพบประวัติการค้างชำระอาจมีการเสนอแนวทางมาตรการอื่น"


def create_gdr_offer_card(planId, currentStatus, dfOffer) -> OfferCard:
    old_inst = currentStatus["CurrentInstallment"]
    old_int  = currentStatus["expIntTotal"]
    new_y1   = dfOffer["installment"].sum()
    new_y2   = dfOffer["installment_Y2"].sum()
    new_int  = dfOffer["expIntTotal"].sum()
    return OfferCard(
        plan_id          = planId,
        plan_desc        = "มาตรการพักชำระเงินต้นระยะสั้น",
        accounts         = ", ".join(sorted(dfOffer["accNo"].tolist())),
        cnt_eligible     = str(int(dfOffer["fg_eligible"].sum())),
        cnt_total        = str(len(dfOffer)),
        total_os         = _f2(currentStatus["TotalOS"]),
        prev_inst        = _f0(old_inst),
        new_inst         = _f0(new_y1),
        step_label       = " 3 เดือนแรก",
        inst_after_3m    = f"{_f0(new_y2)} บาท/งวด",
        int_total_change = f"{_f2(old_int)} → {_f2(new_int)} บาท",
        notes            = [_NOTE],
    )


def create_GDRoffer_cardAcc(solutionAcc, originalAcc, fgEligible) -> OfferCardAcc:
    if fgEligible:
        return OfferCardAcc(
            acc_no           = solutionAcc.get("refAccNo", ""),
            acc_name         = originalAcc.get("port", ""),
            os               = _f2(solutionAcc.get("os", 0)),
            int_rate         = _pct(solutionAcc.get("intRate", 0)),
            term_change      = f"{originalAcc.get('term')} → {solutionAcc.get('term', 0) + 3} งวด",
            inst_change      = f"{_f0(originalAcc['installment'])} → {_f0(solutionAcc['installment'])} บาท/งวด",
            inst_after_3m    = f"{_f0(solutionAcc['installment_Y2'])} บาท/งวด",
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


def product_GDR_summary(planId, currentStatus, dfAccConsult, dfOffer) -> DebtSolnSummary:
    plan  = "GDR"
    dfAcc = dfAccConsult.copy()
    dfAcc["actualTerm"]  = dfAcc.apply(lambda r: findTerm(r["os"], r["intRate"], r["installment"]), axis=1)
    dfAcc["expIntTotal"] = dfAcc.apply(lambda r: findInterestPaid(r["os"], r["intRate"]/12, r["installment"], r["actualTerm"]), axis=1)
    dfOfferAcc = (dfOffer[dfOffer["fg_eligible"]]
                  [["accNo","os","installment","installment_Y2","intRate","remainTerm","expIntTotal"]]
                  .copy().rename(columns={"accNo":"refAccNo","remainTerm":"term"}))
    dfOfferAcc[["plan","planId"]] = plan, planId
    old_inst = currentStatus["CurrentInstallment"]
    old_int  = currentStatus["expIntTotal"]
    description = (
        f"ข้อเสนอ {planId}: มาตรการพักชำระเงินต้น 3 เดือน\n"
        f"บัญชีที่พิจารณา: {', '.join(sorted(dfOffer['accNo'].tolist()))}\n"
        f"บัญชีที่เข้าร่วม: {', '.join(sorted(dfOffer[dfOffer['fg_eligible']]['accNo'].tolist()))}\n"
        f"ค่างวด 3 เดือนแรก: {_f2(old_inst)} → {_f2(dfOffer['installment'].sum())} บาท/งวด\n"
        f"ภายหลัง 3 เดือน: {_f2(dfOffer['installment_Y2'].sum())} บาท/งวด\n"
        f"ดอกเบี้ยรวม: {_f2(old_int)} → {_f2(dfOffer['expIntTotal'].sum())} บาท\n"
    )
    card     = create_gdr_offer_card(planId, currentStatus, dfOffer)
    solnList = [DebtSolnAcc(**a).model_dump() for a in dfOfferAcc.to_dict(orient="records")]
    lookup   = {a["refAccNo"]: a for a in solnList}
    for ori in dfAcc.rename(columns={"accNo":"refAccNo","remainTerm":"term"}).to_dict(orient="records"):
        key = ori["refAccNo"]
        card.account_details.append(
            create_GDRoffer_cardAcc(lookup[key], ori, True) if key in lookup
            else create_GDRoffer_cardAcc(ori, ori, False))
    return DebtSolnSummary(**{
        "solutionDesc":"พักชำระเงินต้น","plan":plan,"planId":planId,
        "refAccNo":", ".join(sorted(dfOffer["accNo"].tolist())),
        "planDesc":"พักชำระเงินต้น",
        "installment":dfOffer["installment"].sum(),"term":dfOffer["actualTerm"].max(),
        "installment_Y2":dfOffer["installment_Y2"].sum(),
        "totalIntPaid":dfOffer["expIntTotal"].sum(),"constantPayment":False,
        "offerText":description,"offerCard":card.model_dump(),"solnAcc":solnList,
    })


def generate_GDR_offer(currentStatus, dfAccConsult) -> list[DebtSolnSummary]:
    dfAcc  = dfAccConsult.copy()
    planId = "GDR01" + dt.datetime.now().strftime("%Y%m%d%H%M%S")
    dfAcc["cntrDate"]    = pd.to_datetime(dfAcc["cntrDate"], format='mixed')
    dfAcc["mob"]         = ((pd.Timestamp.today().year - dfAcc["cntrDate"].dt.year)*12
                            + pd.Timestamp.today().month - dfAcc["cntrDate"].dt.month)
    dfAcc["fg_eligible"] = dfAcc["mob"] >= Min_MOB_to_GDR
    dfAcc["actualTerm"]  = dfAcc.apply(lambda r: findTerm(r["os"], r["intRate"], r["installment"]), axis=1)
    dfAcc["expIntTotal"] = dfAcc.apply(lambda r: findInterestPaid(r["os"], r["intRate"]/12, r["installment"], r["actualTerm"]), axis=1)
    if dfAcc["fg_eligible"].sum() == 0:
        return []
    dfAcc["installment_Y2"] = dfAcc["installment"]
    dfAcc.loc[dfAcc["fg_eligible"], "installment"]  = (dfAcc["intRate"]/12)*dfAcc["os"]
    dfAcc.loc[dfAcc["fg_eligible"], "expIntTotal"]  = 3*(dfAcc["intRate"]/12)*dfAcc["os"] + dfAcc["expIntTotal"]
    dfAcc.loc[dfAcc["actualTerm"] <= 3, "installment_Y2"] = 0
    return [product_GDR_summary(planId, currentStatus, dfAccConsult, dfAcc)]
