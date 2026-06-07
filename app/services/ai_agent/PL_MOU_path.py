"""PL_MOU_path.py"""
from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd
from app.services.ai_agent.config import PL_MOU_interest_map
from app.services.functions.AmortiseCal import findInstallment, findInterestPaid, findTerm
from app.services.functions.util import DSR_feasibility, DSR_feasibile_payment
from app.services.HTML.model_HTML import OfferCard, OfferCardAcc
from app.services.model import DebtSolnAcc, DebtSolnSummary

_f0  = lambda n: f"{n:,.0f}"
_f2  = lambda n: f"{n:,.2f}"
_pct = lambda n: f"{100*n:,.2f}"


def create_plmou_offer_card(planId, accNoConcat, occ, solutionDesc,
                             interest, installment, totalIntPaid, term, currentStatus) -> OfferCard:
    old_inst = currentStatus["CurrentInstallment"]
    old_term = currentStatus["remainTerm"]
    old_int  = currentStatus["expIntTotal"]
    accs     = sorted(accNoConcat.split(","))
    return OfferCard(
        plan_id          = planId,
        plan_desc        = "รวมหนี้ผ่านสินเชื่อ MOU แบบไม่มีหลักประกัน",
        accounts         = ", ".join(accs),
        cnt_eligible     = str(len(accs)),
        cnt_total        = str(len(accs)),
        total_os         = _f2(currentStatus["TotalOS"]),
        prev_inst        = _f0(old_inst),
        new_inst         = _f0(installment),
        source_desc      = solutionDesc,
        int_rate_new     = f"{_pct(interest)}% ต่อปี ({occ})",
        term_change      = f"{old_term} → {term} งวด",
        int_total_change = f"{_f2(old_int)} → {_f2(totalIntPaid)} บาท",
        notes            = [
            "มาตรการนี้เป็นคำแนะนำสำหรับการเปิดสินเชื่อใหม่ การพิจารณาจะเป็นไปตามระเบียบการอนุมัติสินเชื่อของธนาคาร",
            "มาตรการนี้สำหรับบุคลากรขององค์กรที่มีการลงนาม MOU กับธนาคารเท่านั้น",
        ],
    )


def create_MOUoffer_cardAcc(solutionAcc, prev_total_int) -> OfferCardAcc:
    return OfferCardAcc(
        acc_no           = solutionAcc.get("refAccNo", ""),
        acc_name         = "สินเชื่อส่วนบุคคลอเนกประสงค์ภายใต้ MOU สำหรับรวมสินเชื่อ",
        os               = _f2(solutionAcc.get("os", 0)),
        int_rate         = _pct(solutionAcc.get("intRate", 0)),
        inst_new_loan    = f"{_f0(solutionAcc.get('installment', 0))} บาท",
        term_change      = f"{solutionAcc.get('term')} งวด",
        int_total_change = f"{_f2(prev_total_int)} → {_f2(solutionAcc['expIntTotal'])} บาท",
    )


def product_PLMOUsummary(plan, planId, accNoConcat, solutionDesc, occ,
                          interest, installment, totalIntPaid, term, currentStatus) -> DebtSolnSummary:
    old_inst = currentStatus["CurrentInstallment"]
    old_term = currentStatus["actualTerm"]
    old_int  = currentStatus["expIntTotal"]
    description = (
        f"ข้อเสนอ {planId}: รวมสินเชื่อ MOU ไม่มีหลักประกัน\n"
        f"อัตราดอกเบี้ย{occ}: {_pct(interest)}% ต่อปี\n"
        f"บัญชีที่พิจารณา: {accNoConcat}\n"
        f"ค่างวด ({solutionDesc}): {_f2(old_inst)} → {_f2(installment)} บาท/งวด\n"
        f"ระยะเวลา: {old_term} → {term} งวด\n"
        f"ดอกเบี้ยรวม: {_f2(old_int)} → {_f2(totalIntPaid)} บาท\n"
    )
    card = create_plmou_offer_card(planId, accNoConcat, occ, solutionDesc,
                                   interest, installment, totalIntPaid, term, currentStatus)
    solnList = [DebtSolnAcc(**{
        "plan":plan,"os":currentStatus["TotalOS"],"planId":planId,
        "refAccNo":accNoConcat,"installment":installment,
        "term":term,"intRate":interest,"expIntTotal":totalIntPaid,
    }).model_dump()]
    card.account_details.append(create_MOUoffer_cardAcc(solnList[0], prev_total_int=old_int))
    return DebtSolnSummary(**{
        "solutionDesc":solutionDesc,"plan":plan,"planId":planId,
        "refAccNo":accNoConcat,"planDesc":"สินเชื่อรวมหนี้ MOU แบบไม่มีหลักประกัน",
        "installment":installment,"term":term,"totalIntPaid":totalIntPaid,
        "constantPayment":True,"offerText":description,
        "offerCard":card.model_dump(),"solnAcc":solnList,
    })


def generate_PLMOU_offer(currentStatus, userInfo, dfKTBAcc, dfAccConsult, maxPayment, maxTerm) -> list[DebtSolnSummary]:
    totalOs      = currentStatus["TotalOS"]
    accNoConcat  = ",".join(sorted(dfAccConsult["accNo"].tolist()))
    KTBinst      = dfKTBAcc["installment"].sum()
    interest     = PL_MOU_interest_map[userInfo.get("employment_type", "")]
    maxTerm_bank = int(12*np.minimum((60-userInfo.get("age",60)),20))
    occ          = userInfo.get("employment_type")
    def dsr_ok(pmt): return DSR_feasibility(KTBinst, userInfo.get("InstallmentNCB_Y1"), pmt, userInfo.get("IncomeFromSystem"), occ)
    def make(plan, pid, desc, inst, trm, intpd):
        return product_PLMOUsummary(plan, pid, accNoConcat, desc, occ, interest, inst, intpd, trm, currentStatus)
    out   = []
    inst1 = findInstallment(totalOs, interest, maxTerm_bank)
    int1  = findInterestPaid(totalOs, interest/12, inst1, maxTerm_bank)
    ok    = dsr_ok(inst1)
    if ok:
        out.append(make("PLMOU01","PLMOU01"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),"อัตราขั้นต่ำของธนาคาร",inst1,maxTerm_bank,int1))
    if (inst1 < maxPayment) and ok:
        pmt2 = maxPayment if dsr_ok(maxPayment) else DSR_feasibile_payment(KTBinst,userInfo.get("InstallmentNCB_Y1"),userInfo.get("IncomeFromSystem"),occ)
        trm2 = findTerm(totalOs,interest,pmt2)
        int2 = findInterestPaid(totalOs,interest/12,pmt2,trm2)
        out.append(make("PLMOU02","PLMOU02"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),"ความสามารถในการชำระ",pmt2,trm2,int2))
    if (maxTerm < maxTerm_bank) and ok:
        inst3 = findInstallment(totalOs,interest,maxTerm)
        int3  = findInterestPaid(totalOs,interest/12,inst3,maxTerm)
        if dsr_ok(inst3):
            out.append(make("PLMOU03","PLMOU03"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),"ระยะเวลาในการชำระเบ็ดเสร็จ",inst3,maxTerm,int3))
    return out
