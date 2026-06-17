"""TDR_PL_path.py"""
from __future__ import annotations
import datetime as dt
import numpy as np
import pandas as pd
from app.services.functions.AmortiseCal import findInstallment, findInterestPaid, findRemainOS, findTerm
from app.services.HTML.model_HTML import OfferCard, OfferCardAcc
from app.services.ai_agent.config import TDR_maxPaymentTerm, PossibleTDRLoan, TDRmin_payment_prop
from app.services.model import DebtSolnAcc, DebtSolnSummary

_f0  = lambda n: f"{n:,.0f}"
_f2  = lambda n: f"{n:,.2f}"
_pct = lambda n: f"{100*n:,.2f}"

# ── unchanged calculation helpers ─────────────────────────────────────────

def summarise_first3Y_installment(df):
    df["installment"]    = df["installment"]    * (df["remainTerm"] > 0)
    df["installment_Y2"] = df["installment"]    * (df["remainTerm"] > 12)
    df["installment_Y3"] = df["installment"]    * (df["remainTerm"] > 24)

def current_installment_acc(dfOffer):
    df = dfOffer.copy(); summarise_first3Y_installment(df)
    return df[["installment","installment_Y2","installment_Y3"]].sum()

def cash_flow_analysis_TDRAcc(dfAcc : pd.DataFrame, 
                            dfKTBAcc: pd.DataFrame,
                            preference: dict,
                            maxPayment : float,
                            userInfo : dict):
    df = pd.DataFrame()
    df["NCB"]   = pd.Series({"installment":userInfo.get("InstallmentNCB_Y1",0),
                              "installment_Y2":userInfo.get("InstallmentNCB_Y2",0),
                              "installment_Y3":userInfo.get("InstallmentNCB_Y3",0)})
    df["KTB_notConsider"]   = current_installment_acc(dfKTBAcc[~dfKTBAcc["accNo"].isin(dfAcc["accNo"])])
    df["oth"]   = df["NCB"]+df["KTB_notConsider"]
    return pd.Series({
        "installment":   maxPayment,
        "installment_Y2": np.maximum(0, maxPayment+(df["oth"]["installment"]-df["oth"]["installment_Y2"])),
        "installment_Y3": np.maximum(0, maxPayment+(df["oth"]["installment"]-df["oth"]["installment_Y3"])),
    })

def TDRFlatCal(df: pd.DataFrame):
    df["remainTerm_tdr"] = df.apply(lambda r:findTerm(r["os"], r["intRate"], r["installment_tdr"]), axis=1)
    df["expIntTotal_tdr"] =df.apply(lambda r:findInterestPaid(r["os"], r["intRate"]/12, r["installment_tdr"], r["remainTerm_tdr"]), axis=1)
    for col in ["installment", "remainTerm", "expIntTotal"]:
        df.loc[df["fg_eligible"], col] = df[f"{col}_tdr"]
    df[["installment_Y2", "installment_Y3"]] = np.nan
    return df

def TDROfferGivenTerm(dfAcc: pd.DataFrame,
                      Term = TDR_maxPaymentTerm):
    df = dfAcc.copy()
    df["installment_tmp"] = df.apply(lambda r:findInstallment(r["os"],r["intRate"], Term),axis=1)
    df["installment_tdr"] = np.maximum(df["installment_tmp"], df["min_installment"])
    return TDRFlatCal(df)

def TDR02Offer(maxPayYear : pd.Series,
               dfAcc : pd.DataFrame):
    df = dfAcc.copy()
    df["os_tdr"] = df["os"]*df["fg_eligible"]
    maxPay_TDR = maxPayYear["installment"] - df[~df["fg_eligible"]]["installment"].sum()
    df["installment_tdr"]=df["min_installment"]+(maxPay_TDR-df["min_installment"].sum())*(df["os_tdr"]/df["os_tdr"].sum())
    return TDRFlatCal(df)

def TDRstepUpOffer(maxPayYear: pd.Series,
                   dfAcc: pd.DataFrame):
    df=dfAcc.copy()
    df["os_tdr"] = df["os"]*df["fg_eligible"]
    maxPay_TDR_Y1 = maxPayYear["installment"] - df[~df["fg_eligible"]]["installment"].sum()
    df["installment_tdr"]=df["min_installment"]+(maxPay_TDR_Y1-df["min_installment"].sum())*(df["os_tdr"]/(df["os_tdr"].sum()+ 1e-10))
    df["term_Y1"]=np.minimum(12, df.apply(lambda r:findTerm(r["os"], r["intRate"], r["installment_tdr"]), axis=1))
    df["remainOS_Y1"]=np.maximum(0, df.apply(lambda r:findRemainOS(r["os"],r["intRate"]/12,r["installment_tdr"],r["term_Y1"]),axis=1))*df["fg_eligible"]
    df["expIntTotal_Y1"]=df.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment_tdr"],r["term_Y1"]),axis=1)
    
    df["min_inst_Y2"]=df["remainOS_Y1"]*(df["intRate"]/12)*(1/(1-TDRmin_payment_prop))
    maxPay_TDR_Y2 = maxPayYear["installment_Y2"] - df[~df["fg_eligible"]]["installment_Y2"].sum()
    df["installment_Y2_tdr"]=df["min_inst_Y2"]+(maxPay_TDR_Y2-df["min_inst_Y2"].sum())*(df["remainOS_Y1"]/(df["remainOS_Y1"].sum()+ 1e-10))
    df["term_Y2"]=np.minimum(12,df.apply(lambda r:findTerm(r["remainOS_Y1"],r["intRate"],r["installment_Y2_tdr"]),axis=1))
    df["remainOS_Y2"]=np.maximum(0,df.apply(lambda r:findRemainOS(r["remainOS_Y1"],r["intRate"]/12,r["installment_Y2_tdr"],np.minimum(r["term_Y2"],12)),axis=1))*df["fg_eligible"]
    df["expIntTotal_Y2"]=df.apply(lambda r:findInterestPaid(r["remainOS_Y1"],r["intRate"]/12,r["installment_Y2_tdr"],np.minimum(r["term_Y2"],12)),axis=1)

    df["min_inst_Y3"]=df["remainOS_Y2"]*(df["intRate"]/12)*(1/(1-TDRmin_payment_prop))
    maxPay_TDR_Y3 = maxPayYear["installment_Y3"] - df[~df["fg_eligible"]]["installment_Y3"].sum()
    df["installment_Y3_tdr"]=df["min_inst_Y3"]+(maxPay_TDR_Y3-df["min_inst_Y3"].sum())*df["remainOS_Y2"]/(df["remainOS_Y2"].sum() + 1e-10)
    df["term_Y3"]=df.apply(lambda r:findTerm(r["remainOS_Y2"],r["intRate"],r["installment_Y3_tdr"]),axis=1)
    df["expIntTotal_Y3"]=df.apply(lambda r:findInterestPaid(r["remainOS_Y2"],r["intRate"]/12,r["installment_Y3_tdr"],r["term_Y3"]),axis=1)

    df["expIntTotal_tdr"]=df["expIntTotal_Y1"]+df["expIntTotal_Y2"]+df["expIntTotal_Y3"]
    df["remainTerm_tdr"]=df["term_Y1"]+df["term_Y2"]+df["term_Y3"]

    for col in ["installment", "installment_Y2", "installment_Y3", "remainTerm", "expIntTotal"]:
        df.loc[df["fg_eligible"], col] = df[f"{col}_tdr"]
    return df

def BalloonStepPlanAcc(A):
    A["remainTerm"]=A["contractTerm"]
    A["extraPaymentlastMth"] = 0
    if A["fg_eligible"]:
        if A["remainTerm"]<=12:
            ro=findRemainOS(A["os"],A["intRate"]/12,A["installment"],A["remainTerm"])
            A["expIntTotal"]=A["installment"]*A["remainTerm"]+ro-A["os"]
            A["extraPaymentlastMth"]=ro
        elif A["remainTerm"]<=24:
            ro1=findRemainOS(A["os"],A["intRate"]/12,A["installment"],12)
            ro2=findRemainOS(ro1,A["intRate"]/12,A["installment_Y2"],A["remainTerm"]-12)
            A["expIntTotal"]=A["installment"]*12+A["installment_Y2"]*(A["remainTerm"]-12)+ro2-A["os"] 
            A["extraPaymentlastMth"]=ro2
        else:
            ro1=findRemainOS(A["os"],A["intRate"]/12,A["installment"],12)
            ro2=findRemainOS(ro1,A["intRate"]/12,A["installment_Y2"],12)
            ro3=findRemainOS(ro2,A["intRate"]/12,A["installment_Y3"],A["remainTerm"]-24)
            A["expIntTotal"]=A["installment"]*12+A["installment_Y2"]*12+A["installment_Y3"]*(A["remainTerm"]-24)+ro3-A["os"]
            A["extraPaymentlastMth"]=ro3
    return A

def TDRstepUpOfferBalloon(dfStepUp: pd.DataFrame):
    return dfStepUp.copy().apply(BalloonStepPlanAcc,axis=1)

def BalloonPlanFlat(dfAcc: pd.DataFrame):
    df = dfAcc.copy()
    df["remainTerm"] =  df["contractTerm"]
    df["extraPaymentlastMth_tdr"]=np.maximum(0,df.apply(lambda r:findRemainOS(r["os"],r["intRate"]/12,r["installment"], r["remainTerm"]),axis=1))
    df["expIntTotal_tdr"]=df.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment"], r["remainTerm"]),axis=1)
    for col in ["extraPaymentlastMth", "expIntTotal"]:
        df.loc[df["fg_eligible"], col] = df[f"{col}_tdr"]
    df[["installment_Y2", "installment_Y3"]] = np.nan
    return df

def _parts(dfOffer,fgFlat,fgBalloon):
    p=["ด้วยอัตราผ่อนชำระคงที่" if fgFlat else "ด้วยอัตราผ่อนชำระแบบขั้นบันได"]
    if fgBalloon: p.append("และมีค่างวดชำระส่วนสุดท้าย")
    elif (dfOffer["remainTerm"]<=dfOffer["contractTerm"]).all(): p.append("โดยไม่ขยายอายุสัญญา")
    else: p.append("โดยขยายอายุสัญญา")
    return p

def _y2y3_str(y2,y3):
    return f"{_f0(y2)} และ {_f0(y3)} บาท/งวด" if abs(y2-y3)>1 else f"{_f0(y3)} บาท/งวด"

# ── offer-card builders ───────────────────────────────────────────────────

def create_tdr_offer_card(planId: str,
                        solutionDesc: str,
                        dfAccCurrent: pd.DataFrame,
                        dfOffer: pd.DataFrame,
                        fgFlat: bool,
                        fgBalloon : bool) -> OfferCard:
    
    parts    = _parts(dfOffer,fgFlat,fgBalloon)
    ncb      = ("โดยขยายอายุสัญญา" in parts)
    notes = []
    if fgBalloon: notes.append("มาตรการนี้สำหรับผู้ที่ไม่เคยมีประวัติค้างชำระกับธนาคารเท่านั้น หากเจ้าหน้าที่ตรวจพบประวัติการค้างชำระอาจมีการเสนอแนวทางมาตรการอื่น")
    elif ncb:     notes.append("มาตรการนี้ส่งผลต่อข้อมูลที่ธนาคารมีการจัดส่งไปยังสำนักงานเครดิตแห่งชาติซึ่งอาจมีผลต่อการขอสินเชื่อของลูกค้าในอนาคต")
    balloon_rows = []
    if fgBalloon:
        balloon_rows = [f"{acc['accNo']}|{int(acc['remainTerm'])}|{_f2(acc['extraPaymentlastMth'])}"
                        for _,acc in dfOffer[dfOffer["fg_eligible"]].iterrows() if acc['extraPaymentlastMth'] > 0]
    return OfferCard(
        plan_id          = planId,
        plan_desc        = "มาตรการปรับโครงสร้างหนี้"+"".join(parts),
        ncb_badge        = "มีผลต่อเครดิตบูโร" if ncb else "",
        accounts         = ", ".join(sorted(dfOffer["accNo"].tolist())),
        cnt_eligible     = str(int(dfOffer["fg_eligible"].sum())),
        cnt_total        = str(len(dfOffer)),
        total_os         = _f2(dfAccCurrent["os"].sum()),
        prev_inst        = _f0(dfAccCurrent["installment"].sum()),
        new_inst         = _f0(dfOffer["installment"].sum()),
        step_label       = "" if fgFlat else "ปีแรก",
        source_desc      = solutionDesc,
        inst_y2y3        = _y2y3_str(float(dfOffer["installment_Y2"].sum()),float(dfOffer["installment_Y3"].sum())) if not fgFlat else "",
        term_change      = f"{int(dfAccCurrent['remainTerm'].max())} → {int(dfOffer['remainTerm'].max())} งวด" if ncb else "",
        int_total_change = f"{_f2(dfAccCurrent['expIntTotal'].sum())} → {_f2(dfOffer['expIntTotal'].sum())} บาท",
        balloon_rows     = balloon_rows,
        notes            = notes,
    )


def create_TDRoffer_cardAcc(accOffer : pd.Series, 
                            accOri : pd.Series, 
                            fgFlat : bool,
                            fgBalloon: bool) -> OfferCardAcc:
    same_term = ( (accOffer["remainTerm"]==accOri["remainTerm"]) or fgBalloon )
    fgEligible = accOffer["fg_eligible"]
    return OfferCardAcc(
        acc_no           = accOri["accNo"],
        acc_name         = accOri["port"],
        os               = _f2(accOri["os"]),
        int_rate         = _pct(accOri["intRate"]),
        term_old         = f"{accOri['remainTerm']} งวด" if same_term else "",
        term_change      = "" if same_term else f"{accOri['remainTerm']} → {accOffer['remainTerm']} งวด",
        inst_change      = f"{_f0(accOri['installment'])} → {_f0(accOffer['installment'])} บาท/งวด" if fgFlat else "",
        inst_change_y1   = f"{_f0(accOri['installment'])} → {_f0(accOffer['installment'])} บาท/งวด" if not fgFlat else "",
        inst_y2y3        = _y2y3_str(accOffer["installment_Y2"],accOffer["installment_Y3"]) if not fgFlat else "",
        balloon_payment  = f"{_f2(accOffer['extraPaymentlastMth'])} บาท" if fgBalloon and fgEligible else "",
        int_total_change = f"{_f2(accOri['expIntTotal'])} → {_f2(accOffer['expIntTotal'])} บาท" if fgEligible else "",
        int_total_old    = f"{_f2(accOri['expIntTotal'])} บาท" if not fgEligible else "",
        inelig_note      = "" if fgEligible else "บัญชีนี้ไม่เข้าเกณฑ์เข้าร่วมมาตรการ จึงคงเงื่อนไขการชำระตามเดิม",
    )


def TDR_summary(plan: str, 
                planId: str, 
                solutionDesc: str,
                dfAccCurrent: pd.DataFrame,
                dfOffer: pd.DataFrame,
                fgFlat: bool,
                fgBalloon: bool) -> DebtSolnSummary:

    card  = create_tdr_offer_card(planId = planId,
                                solutionDesc = solutionDesc,
                                dfAccCurrent = dfAccCurrent,
                                dfOffer = dfOffer,
                                fgFlat = fgFlat,
                                fgBalloon = fgBalloon)
    
    valid_keys = list(DebtSolnAcc.model_fields.keys())

    solnList = [DebtSolnAcc(**{**{k: v for k, v in a.items() if k in valid_keys}, 
                            'planId': planId, 
                            'plan': plan}).model_dump() for a in dfOffer.rename(columns={"accNo": "refAccNo", 
                                                                                         "remainTerm": "term"}).to_dict(orient="records")]
    for i in range(len(dfOffer)):
        accOffer = dfOffer.iloc[i]
        accOri = dfAccCurrent.iloc[i]
        card.account_details.append(create_TDRoffer_cardAcc(accOffer = accOffer, 
                                                            accOri = accOri,
                                                            fgFlat = fgFlat, 
                                                            fgBalloon = fgBalloon))
    return DebtSolnSummary(**{
        "solutionDesc":solutionDesc,
        "plan":plan,
        "planId":planId,
        "refAccNo":", ".join(sorted(dfOffer["accNo"].tolist())),
        "planDesc":f"TDR {solutionDesc}",
        "installment":float(dfOffer["installment"].sum()),
        "installment_Y2":float(dfOffer["installment_Y2"].sum()),
        "installment_Y3":float(dfOffer["installment_Y3"].sum()),
        "term":int(dfOffer["remainTerm"].max()),
        "totalIntPaid":float(dfOffer["expIntTotal"].sum()),
        "constantPayment":False,
        "offerCard":card.model_dump(),
        "solnAcc":solnList})


def NewStepOffer(planStep: str,
                 planStepBalloon: str,
                 solutionDesc: str,
                 maxPayYear: pd.Series, 
                 dfAcc: pd.DataFrame,
                 dfAccCurrent: pd.DataFrame):
    out=[]
    dfSt=TDRstepUpOffer(maxPayYear = maxPayYear,
                        dfAcc = dfAcc)
    
    if dfSt["remainTerm"].max()<=TDR_maxPaymentTerm:
        out.append(TDR_summary(plan = planStep,
                                planId = planStep+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                solutionDesc = solutionDesc,
                                dfAccCurrent = dfAccCurrent, 
                                dfOffer =dfSt,
                                fgFlat =False,
                                fgBalloon = False))
        
    if (dfSt["remainTerm"]>dfSt["contractTerm"]).any():
        dfSB=TDRstepUpOfferBalloon(dfSt)
        out.append(TDR_summary(plan = planStepBalloon,
                                planId = planStepBalloon+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                solutionDesc = solutionDesc,
                                dfAccCurrent = dfAccCurrent, 
                                dfOffer =dfSB,
                                fgFlat =False,
                                fgBalloon = True))
    return out


def generate_TDR_offer(currentStatus: dict, 
                         userInfo: dict, 
                         preference: dict,
                         dfKTBAcc: pd.DataFrame, 
                         maxPayment: float, 
                         maxTerm: int)-> list[DebtSolnSummary]:
    
    dfAcc=currentStatus["current_debt"].copy()
    dfAcc["contractTerm"]  = dfAcc["remainTerm"] 
    dfAcc["fg_eligible"]    =dfAcc["port"].isin(PossibleTDRLoan)
    dfAcc["min_installment"]=dfAcc["os"]*(dfAcc["intRate"]/12)*(1/(1-TDRmin_payment_prop))
    dfAcc.loc[~dfAcc["fg_eligible"], "min_installment"] = dfAcc["installment"]
    summarise_first3Y_installment(dfAcc)
    cashFlow = cash_flow_analysis_TDRAcc(dfAcc = dfAcc, 
                                        dfKTBAcc = dfKTBAcc,
                                        maxPayment = maxPayment,
                                        preference = preference,
                                        userInfo = userInfo)
    maxPayYear = cashFlow.copy()
    maxPayYear["installment_Y2"] = min(maxPayYear["installment_Y2"], preference["maxPaymentY2"])
    maxPayYear["installment_Y3"] = min(maxPayYear["installment_Y3"], preference["maxPaymentY3"])

    output=[]
    if dfAcc["fg_eligible"].sum()==0: 
        return output

    df01=TDROfferGivenTerm(dfAcc = dfAcc,
                             Term = TDR_maxPaymentTerm)
    output.append(TDR_summary(plan = "TDR01",
                              planId = "TDR01"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                              solutionDesc = "ด้วยอัตราขั้นต่ำที่ธนาคารเสนอได้",
                              dfAccCurrent = currentStatus["current_debt"], 
                              dfOffer =df01,
                              fgFlat = True,
                              fgBalloon = False))

    if maxPayYear["installment"]<=dfAcc["min_installment"].sum(): 
        return output
    
    if maxPayYear["installment"] > df01["installment"].sum():
        df02=TDR02Offer(maxPayYear = maxPayYear,
                        dfAcc = dfAcc)
        output.append(TDR_summary(plan = "TDR02",
                                planId = "TDR02"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                solutionDesc = "ด้วยอัตรากำลังผ่อนชำระของลูกค้า",
                                dfAccCurrent = currentStatus["current_debt"], 
                                dfOffer =df02,
                                fgFlat = True,
                                fgBalloon = False))
        
        df03=BalloonPlanFlat(df02)
        output.append(TDR_summary(plan = "TDR03",
                                planId = "TDR03"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                solutionDesc = "ด้วยอัตรากำลังผ่อนชำระของลูกค้า",
                                dfAccCurrent = currentStatus["current_debt"], 
                                dfOffer =df03,
                                fgFlat = True,
                                fgBalloon = True))

    output+=NewStepOffer(planStep = "TDR04",
                         planStepBalloon = "TDR05",
                         solutionDesc = "ด้วยอัตรากำลังผ่อนชำระของลูกค้าและกระแสเงินสด",
                         maxPayYear = maxPayYear, 
                         dfAcc = dfAcc,
                         dfAccCurrent = currentStatus["current_debt"])


    maxPayYear2 = cashFlow.copy()
    maxPayYear2["installment_Y2"] = min(0.9*maxPayYear["installment_Y2"], preference["maxPaymentY2"])
    maxPayYear2["installment_Y3"] = min(0.9*maxPayYear["installment_Y3"], preference["maxPaymentY3"])

    if (maxPayYear2 - maxPayYear).abs().sum() > 100:
        output+=NewStepOffer(planStep = "TDR06",
                            planStepBalloon = "TDR07",
                            solutionDesc = "ด้วยอัตรากำลังผ่อนชำระของลูกค้าและกระแสเงินสด",
                            maxPayYear = maxPayYear, 
                            dfAcc = dfAcc,
                            dfAccCurrent = currentStatus["current_debt"])

    if (maxPayYear2["installment_Y2"]>dfAcc["installment"].sum()) or (maxPayYear2["installment_Y3"]>dfAcc["installment"].sum()):
        mpC=maxPayYear2.copy()
        mpC["installment_Y2"]=min(mpC["installment_Y2"],dfAcc["installment"].sum(), preference["maxPaymentY2"])
        mpC["installment_Y3"]=min(mpC["installment_Y3"],dfAcc["installment"].sum(), preference["maxPaymentY3"])
        output+=NewStepOffer(planStep = "TDR08",
                            planStepBalloon = "TDR09",
                            solutionDesc = "ด้วยอัตรากำลังผ่อนชำระของลูกค้าไม่เกินอัตราชำระเดิม",
                            maxPayYear = maxPayYear, 
                            dfAcc = dfAcc,
                            dfAccCurrent = currentStatus["current_debt"])

    if maxTerm < TDR_maxPaymentTerm:
        df10=TDROfferGivenTerm(dfAcc = dfAcc,
                               Term = maxTerm)
        output.append(TDR_summary(plan = "TDR10",
                                planId = "TDR10"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                                solutionDesc = "ด้วยความต้องการชำระหนี้เบ็ดเสร็จของลูกค้า",
                                dfAccCurrent = currentStatus["current_debt"], 
                                dfOffer =df10,
                                fgFlat = True,
                                fgBalloon = False))
    return output
