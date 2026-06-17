"""PL_CSL_path.py"""
from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd
from app.services.functions.AmortiseCal import findInstallment, findInterestPaid, findTerm
from app.services.functions.util import DSR_feasibility, DSR_feasibile_payment
from app.services.HTML.model_HTML import OfferCard, OfferCardAcc
from app.services.model import DebtSolnAcc, DebtSolnSummary

_f0  = lambda n: f"{n:,.0f}"
_f2  = lambda n: f"{n:,.2f}"
_pct = lambda n: f"{100*n:,.2f}"


def create_CSL_offer_card(planId: str,
                        refAcc: str,
                        plan_desc: str,
                        solutionDesc: str,
                        intLabel: str,
                        interest: float,
                        installment: float,
                        totalIntPaid: float,
                        term: int,
                        currentStatus: dict) -> OfferCard:
    return OfferCard(
        plan_id          = planId,
        plan_desc        = plan_desc,
        accounts         = refAcc,
        cnt_eligible     = "-",
        cnt_total        = "-",
        total_os         = _f2(currentStatus["TotalOS"]),
        prev_inst        = _f0(currentStatus["CurrentInstallment"]),
        new_inst         = _f0(installment),
        source_desc      = solutionDesc,
        int_rate_new     = f"{_pct(interest)}% ต่อปี {intLabel}",
        term_change      = f"{currentStatus["remainTerm"]} → {term} งวด",
        int_total_change = f"{_f2(currentStatus["expIntTotal"])} → {_f2(totalIntPaid)} บาท",
        notes            = [
            "มาตรการนี้เป็นคำแนะนำสำหรับการเปิดสินเชื่อใหม่ การพิจารณาอนุมัติจะเป็นไปตามระเบียบการอนุมัติสินเชื่อของธนาคาร",
            "มาตรการนี้สำหรับบุคลากรขององค์กรที่มีการลงนาม MOU กับธนาคารเท่านั้น หากพิจารณาว่าองค์กรของท่านไม่ได้มีการลงนาม ธนาคารอาจมีการปรับเปลี่ยนอัตราดอกเบี้ยและเงื่อนไขการผ่อนชำระ",
        ],
    )


def create_CSLoffer_cardAcc(solutionAcc: dict, 
                            plan_desc: str,
                            prev_total_int: float) -> OfferCardAcc:
    return OfferCardAcc(
        acc_no           = solutionAcc.get("refAccNo", ""),
        acc_name         = plan_desc,
        os               = _f2(solutionAcc.get("os", 0)),
        int_rate         = _pct(solutionAcc.get("intRate", 0)),
        inst_new_loan    = f"{_f0(solutionAcc.get('installment', 0))} บาท",
        term_change      = f"{solutionAcc.get('term')} งวด",
        int_total_change = f"{_f2(prev_total_int)} → {_f2(solutionAcc['expIntTotal'])} บาท",
    )


def product_CSLsummary(plan: str,
                    planId: str,
                    refAcc: str,
                    plan_desc: str,
                    solutionDesc: str,
                    intLabel: str,
                    interest: float,
                    installment: float,
                    totalIntPaid: float,
                    term: int,
                    currentStatus: dict) -> DebtSolnSummary:
    
    card = create_CSL_offer_card(planId=planId,
                                refAcc=refAcc,
                                plan_desc= f"มาตรการเปิด{plan_desc} เพื่อรวมหนี้",
                                solutionDesc=solutionDesc,
                                intLabel=intLabel,
                                interest=interest,
                                installment=installment,
                                totalIntPaid=totalIntPaid,
                                term=term,
                                currentStatus=currentStatus)
    
    solnList = [DebtSolnAcc(**{"plan":plan, "os":currentStatus["TotalOS"], "planId":planId,
                               "refAccNo":refAcc,"installment":installment,
                               "term":term,"intRate":interest,"expIntTotal":totalIntPaid,}).model_dump()]
    
    card.account_details.append(create_CSLoffer_cardAcc(solnList[0], 
                                                        plan_desc = plan_desc,
                                                        prev_total_int=currentStatus["expIntTotal"]))
    return DebtSolnSummary(**{
        "solutionDesc":solutionDesc,
        "plan":plan,
        "planId":planId,
        "refAccNo":refAcc,
        "planDesc":plan_desc,
        "installment":installment,
        "term":term,
        "totalIntPaid":totalIntPaid,
        "constantPayment":True,
        "offerCard":card.model_dump(),
        "solnAcc":solnList})


def generate_CSL_offer(currentStatus: dict, 
                         userInfo: dict, 
                         dfKTBAcc: pd.DataFrame, 
                         maxPayment: float, 
                         maxTerm: int) -> list[DebtSolnSummary]:
    
    totalOs      = currentStatus["TotalOS"]
    accNoConcat  = currentStatus["accNo"]
    KTBinst      = dfKTBAcc["installment"].sum()
    employment_type = userInfo.get("employment_type", "")
    eligible_programs = [x.strip() for x in userInfo.get("EligibleProgram", "").split(",")]
    print(employment_type, eligible_programs)
    CSL_program = "สินเชื่ออเนกประสงค์ MOU"
    if employment_type == "ข้าราชการ/เจ้าหน้าที่รัฐ (Public Sector)" and CSL_program in eligible_programs:
        interest = 0.07
        maxTerm_bank = int(12 * np.minimum((60 - userInfo.get("age", 60)), 20))
        plan_desc = CSL_program
        intLabel = "(อัตราข้าราชการ)"
    elif employment_type == "พนักงานประจำ (Salaried)" and CSL_program in eligible_programs:
        interest = 0.09
        maxTerm_bank = int(12 * np.minimum((60 - userInfo.get("age", 60)), 20))
        plan_desc = CSL_program
        intLabel = "(อัตราพนักงานประจำ)"
    else:
        interest = 0.2
        maxTerm_bank = int(12 * np.minimum((60 - userInfo.get("age", 60)), 10))
        intLabel = ""
        plan_desc = "สินเชื่อกรุงไทย SMART MONEY"

    def dsr_ok(pmt): return DSR_feasibility(ktbInstallment = KTBinst,
                                            NCBInstallment = userInfo.get("InstallmentNCB_Y1"),
                                            newInstallment = pmt,
                                            income = userInfo.get("IncomeFromSystem"),
                                            occ = employment_type)
    output   = []
    inst1 = findInstallment(totalOs, interest, maxTerm_bank)
    ok = dsr_ok(inst1)
    if ok:
        output.append(product_CSLsummary(plan = "CSL01", 
                                           planId = "CSL01" + dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                           refAcc = accNoConcat,
                                           plan_desc = plan_desc,
                                           solutionDesc = "ด้วยอัตราขั้นต่ำที่ธนาคารเสนอได้",
                                           intLabel = intLabel,
                                           interest = interest,
                                           installment = inst1,
                                           totalIntPaid = findInterestPaid(totalOs, interest/12, inst1, maxTerm_bank),
                                           term = maxTerm_bank,
                                           currentStatus = currentStatus))

    if (inst1 < maxPayment) and ok:
        inst2 = maxPayment if dsr_ok(maxPayment) else DSR_feasibile_payment(KTBinst,userInfo.get("InstallmentNCB_Y1"),userInfo.get("IncomeFromSystem"),occ)
        trm2 = findTerm(totalOs,interest,inst2)
        output.append(product_CSLsummary(plan = "CSL02", 
                                           planId = "CSL02" + dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                           refAcc = accNoConcat,
                                           plan_desc = plan_desc,
                                           solutionDesc = "ด้วยอัตรากำลังผ่อนชำระของลูกค้า",
                                           intLabel = intLabel,
                                           interest = interest,
                                           installment = inst2,
                                           totalIntPaid = findInterestPaid(totalOs,interest/12,inst2,trm2),
                                           term = trm2,
                                           currentStatus = currentStatus))
        
    if (maxTerm < maxTerm_bank) and ok:
        inst3 = findInstallment(totalOs,interest,maxTerm)
        if dsr_ok(inst3):
            output.append(product_CSLsummary(plan = "CSL03", 
                                           planId = "CSL03" + dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                           refAcc = accNoConcat,
                                           plan_desc = plan_desc,
                                           solutionDesc = "ด้วยความต้องการชำระหนี้เบ็ดเสร็จของลูกค้า",
                                           intLabel = intLabel,
                                           interest = interest,
                                           installment = inst3,
                                           totalIntPaid = findInterestPaid(totalOs,interest/12,inst3,maxTerm),
                                           term = maxTerm,
                                           currentStatus = currentStatus))
    return output
