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

def current_installment_acc(dfAcc):
    df = dfAcc.copy(); summarise_first3Y_installment(df)
    return df[["installment","installment_Y2","installment_Y3"]].sum()

def cash_flow_analysis(dfAccConsult, dfKTBAcc, maxPayment, userInfo):
    df = pd.DataFrame()
    df["NCB"]   = pd.Series({"installment":userInfo.get("InstallmentNCB_Y1",0),
                              "installment_Y2":userInfo.get("InstallmentNCB_Y2",0),
                              "installment_Y3":userInfo.get("InstallmentNCB_Y3",0)})
    df["KTB"]   = current_installment_acc(dfKTBAcc)
    df["oth"]   = df["NCB"]+df["KTB"]
    df["noTDR"] = current_installment_acc(dfAccConsult[~dfAccConsult["fg_eligible"]])
    return pd.Series({
        "installment":   maxPayment-df["noTDR"]["installment"],
        "installment_Y2":maxPayment-df["noTDR"]["installment_Y2"]+(df["oth"]["installment"]-df["oth"]["installment_Y2"]),
        "installment_Y3":maxPayment-df["noTDR"]["installment_Y3"]+(df["oth"]["installment"]-df["oth"]["installment_Y3"]),
    })

def TDRBestFlatOffer(dfElig):
    df=dfElig.copy(); df["remainTerm"]=TDR_maxPaymentTerm
    df["installment"] =df.apply(lambda r:findInstallment(r["os"],r["intRate"],r["remainTerm"]),axis=1)
    df["fg_eligible"] =True
    df["expIntTotal"] =df.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment"],r["remainTerm"]),axis=1)
    df["installment_Y2"]=df["installment_Y3"]=df["installment"]; return df

def TDRFlatOffer(mp,dfElig):
    df=dfElig.copy()
    df["installment"]=df["min_installment"]+(mp["installment"]-df["min_installment"].sum())*df["os"]/df["os"].sum()
    df["remainTerm"] =df.apply(lambda r:findTerm(r["os"],r["intRate"],r["installment"]),axis=1)
    df["expIntTotal"]=df.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment"],r["remainTerm"]),axis=1)
    df["installment_Y2"]=df["installment_Y3"]=df["installment"]; return df

def TDRstepUpOffer(mp,dfElig):
    df=dfElig.copy()
    df["installment"]=df["min_installment"]+(mp["installment"]-df["min_installment"].sum())*df["os"]/df["os"].sum()
    df["term_Y1"]=np.minimum(12,df.apply(lambda r:findTerm(r["os"],r["intRate"],r["installment"]),axis=1))
    df["remainOS_Y1"]=np.maximum(0,df.apply(lambda r:findRemainOS(r["os"],r["intRate"]/12,r["installment"],r["term_Y1"]),axis=1))
    df["expIntTotal_Y1"]=df.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment"],r["term_Y1"]),axis=1)
    df["min_inst_Y2"]=df["remainOS_Y1"]*(df["intRate"]/12)*(1/(1-TDRmin_payment_prop))
    df["installment_Y2"]=df["min_inst_Y2"]+(mp["installment_Y2"]-df["min_inst_Y2"].sum())*df["remainOS_Y1"]/df["remainOS_Y1"].sum()
    df["term_Y2"]=np.minimum(12,df.apply(lambda r:findTerm(r["remainOS_Y1"],r["intRate"],r["installment_Y2"]),axis=1))
    df["remainOS_Y2"]=np.maximum(0,df.apply(lambda r:findRemainOS(r["remainOS_Y1"],r["intRate"]/12,r["installment_Y2"],np.minimum(r["term_Y2"],12)),axis=1))
    df["expIntTotal_Y2"]=df.apply(lambda r:findInterestPaid(r["remainOS_Y1"],r["intRate"]/12,r["installment_Y2"],np.minimum(r["term_Y2"],12)),axis=1)
    df["min_inst_Y3"]=df["remainOS_Y2"]*(df["intRate"]/12)*(1/(1-TDRmin_payment_prop))
    df["installment_Y3"]=df["min_inst_Y3"]+(mp["installment_Y3"]-df["min_inst_Y3"].sum())*df["remainOS_Y2"]/df["remainOS_Y2"].sum()
    df["term_Y3"]=df.apply(lambda r:findTerm(r["remainOS_Y2"],r["intRate"],r["installment_Y3"]),axis=1)
    df["expIntTotal_Y3"]=df.apply(lambda r:findInterestPaid(r["remainOS_Y2"],r["intRate"]/12,r["installment_Y3"],r["term_Y3"]),axis=1)
    df["expIntTotal"]=df["expIntTotal_Y1"]+df["expIntTotal_Y2"]+df["expIntTotal_Y3"]
    df["remainTerm"]=df["term_Y1"]+df["term_Y2"]+df["term_Y3"]; return df

def BalloonPlanAcc(A):
    A["remainTerm"]=A["contractTerm"]
    if A["remainTerm"]<=12:
        ro=findRemainOS(A["os"],A["intRate"]/12,A["installment"],A["remainTerm"])
        A["expIntTotal"]=A["installment"]*A["remainTerm"]+ro-A["os"]; A["extraPaymentlastMth"]=ro
    elif A["remainTerm"]<=24:
        ro1=findRemainOS(A["os"],A["intRate"]/12,A["installment"],12)
        ro2=findRemainOS(ro1,A["intRate"]/12,A["installment_Y2"],A["remainTerm"]-12)
        A["expIntTotal"]=A["installment"]*12+A["installment_Y2"]*(A["remainTerm"]-12)+ro2-A["os"]; A["extraPaymentlastMth"]=ro2
    else:
        ro1=findRemainOS(A["os"],A["intRate"]/12,A["installment"],12)
        ro2=findRemainOS(ro1,A["intRate"]/12,A["installment_Y2"],12)
        ro3=findRemainOS(ro2,A["intRate"]/12,A["installment_Y3"],A["remainTerm"]-24)
        A["expIntTotal"]=A["installment"]*12+A["installment_Y2"]*12+A["installment_Y3"]*(A["remainTerm"]-24)+ro3-A["os"]; A["extraPaymentlastMth"]=ro3
    return A

def BalloonPlan(df): return df.copy().apply(BalloonPlanAcc,axis=1)

def _parts(dfOffer,fgFlat,fgBalloon):
    p=["ด้วยอัตราผ่อนชำระคงที่" if fgFlat else "ด้วยอัตราผ่อนชำระแบบขั้นบันได"]
    if fgBalloon: p.append("และมีค่างวดชำระส่วนสุดท้าย")
    elif (dfOffer["remainTerm"]<=dfOffer["contractTerm"]).all(): p.append("โดยไม่ขยายอายุสัญญา")
    else: p.append("โดยขยายอายุสัญญา")
    return p

def _y2y3_str(y2,y3):
    return f"{_f0(y2)} และ {_f0(y3)} บาท/งวด" if abs(y2-y3)>1 else f"{_f0(y3)} บาท/งวด"

# ── offer-card builders ───────────────────────────────────────────────────

def create_tdr_offer_card(planId, new3Y, old3Y, dfOffer, solutionDesc, currentStatus, fgFlat, fgBalloon) -> OfferCard:
    old_int  = currentStatus["expIntTotal"]
    old_term = currentStatus["remainTerm"]
    parts    = _parts(dfOffer,fgFlat,fgBalloon)
    ncb      = "โดยขยายอายุสัญญา" in parts
    notes = []
    if fgBalloon: notes.append("มาตรการนี้สำหรับผู้ที่ไม่เคยมีประวัติค้างชำระกับธนาคารเท่านั้น หากเจ้าหน้าที่ตรวจพบประวัติการค้างชำระอาจมีการเสนอแนวทางมาตรการอื่น")
    elif ncb:     notes.append("มาตรการนี้ส่งผลต่อข้อมูลที่ธนาคารมีการจัดส่งไปยังสำนักงานเครดิตแห่งชาติซึ่งอาจมีผลต่อการขอสินเชื่อของลูกค้าในอนาคต")
    balloon_rows = []
    if fgBalloon:
        balloon_rows = [f"{acc['accNo']}|{int(acc['remainTerm'])}|{_f2(acc['extraPaymentlastMth'])}"
                        for _,acc in dfOffer[dfOffer["fg_eligible"]].iterrows()]
    return OfferCard(
        plan_id          = planId,
        plan_desc        = "มาตรการปรับโครงสร้างหนี้"+"".join(parts),
        ncb_badge        = "มีผลต่อเครดิตบูโร" if ncb else "",
        accounts         = ", ".join(sorted(dfOffer["accNo"].tolist())),
        cnt_eligible     = str(int(dfOffer["fg_eligible"].sum())),
        cnt_total        = str(len(dfOffer)),
        total_os         = _f2(currentStatus["TotalOS"]),
        prev_inst        = _f0(old3Y["installment"]),
        new_inst         = _f0(new3Y["installment"]),
        step_label       = "" if fgFlat else "ปีแรก",
        source_desc      = solutionDesc,
        inst_y2y3        = _y2y3_str(float(new3Y["installment_Y2"]),float(new3Y["installment_Y3"])) if not fgFlat else "",
        term_change      = f"{old_term} → {int(dfOffer['remainTerm'].max())} งวด" if ncb else "",
        int_total_change = f"{_f2(old_int)} → {_f2(dfOffer['expIntTotal'].sum())} บาท",
        balloon_rows     = balloon_rows,
        notes            = notes,
    )


def create_TDRoffer_cardAcc(solutionAcc, originalAcc, fgEligible, fgFlat, fgBalloon) -> OfferCardAcc:
    same_term = (originalAcc.get("term")==solutionAcc.get("term")) or fgBalloon
    return OfferCardAcc(
        acc_no           = solutionAcc.get("refAccNo",""),
        acc_name         = originalAcc.get("port",""),
        os               = _f2(solutionAcc.get("os",0)),
        int_rate         = _pct(solutionAcc.get("intRate",0)),
        term_old         = f"{originalAcc.get('term')} งวด" if same_term else "",
        term_change      = "" if same_term else f"{originalAcc.get('term')} → {solutionAcc.get('term')} งวด",
        inst_change      = f"{_f0(originalAcc['installment'])} → {_f0(solutionAcc['installment'])} บาท/งวด" if fgFlat else "",
        inst_change_y1   = f"{_f0(originalAcc['installment'])} → {_f0(solutionAcc['installment'])} บาท/งวด" if not fgFlat else "",
        inst_y2y3        = _y2y3_str(solutionAcc["installment_Y2"],solutionAcc["installment_Y3"]) if not fgFlat else "",
        balloon_payment  = f"{_f2(solutionAcc['extraPaymentlastMth'])} บาท" if fgBalloon and fgEligible else "",
        int_total_change = f"{_f2(originalAcc['expIntTotal'])} → {_f2(solutionAcc['expIntTotal'])} บาท" if fgEligible else "",
        int_total_old    = f"{_f2(originalAcc['expIntTotal'])} บาท" if not fgEligible else "",
        inelig_note      = "" if fgEligible else "บัญชีนี้ไม่เข้าเกณฑ์เข้าร่วมมาตรการ จึงคงเงื่อนไขการชำระตามเดิม",
    )


def TDR_summary(plan, planId, dfOffer, dfAccConsult, solutionDesc, currentStatus, fgFlat, fgBalloon) -> DebtSolnSummary:
    old3Y  = current_installment_acc(dfAccConsult)
    new3Y  = dfOffer[["installment","installment_Y2","installment_Y3"]].sum()
    old_int= currentStatus["expIntTotal"]
    parts  = _parts(dfOffer,fgFlat,fgBalloon)
    planDesc="".join(parts)
    col_base=["accNo","os","installment","installment_Y2","installment_Y3","intRate","remainTerm","expIntTotal"]
    col_ext =col_base+(["extraPaymentlastMth"] if "extraPaymentlastMth" in dfOffer.columns else [])
    dfOfferAcc=(dfOffer[dfOffer["fg_eligible"]][col_ext].copy()
                .rename(columns={"accNo":"refAccNo","remainTerm":"term"}))
    dfOfferAcc[["plan","planId"]]=plan,planId
    desc=[f"ข้อเสนอ {planId}: TDR {planDesc}\n",
          f"บัญชีที่พิจารณา: {', '.join(sorted(dfOffer['accNo'].tolist()))}\n",
          f"บัญชีที่ปรับโครงสร้าง: {', '.join(sorted(dfOffer[dfOffer['fg_eligible']]['accNo'].tolist()))}\n"]
    if fgFlat: desc.append(f"ค่างวด: {_f0(old3Y['installment'])} → {_f0(new3Y['installment'])} บาท/งวด\n")
    else: desc+=[f"ปีที่ 1: {_f0(old3Y['installment'])} → {_f0(new3Y['installment'])} บาท/งวด\n",
                 f"ปีที่ 2: {_f0(old3Y['installment_Y2'])} → {_f0(new3Y['installment_Y2'])} บาท/งวด\n",
                 f"ปีที่ 3: {_f0(old3Y['installment_Y3'])} → {_f0(new3Y['installment_Y3'])} บาท/งวด\n"]
    desc.append(f"ดอกเบี้ยรวม: {_f2(old_int)} → {_f2(dfOffer['expIntTotal'].sum())} บาท\n")
    card     = create_tdr_offer_card(planId,new3Y,old3Y,dfOffer,solutionDesc,currentStatus,fgFlat,fgBalloon)
    solnList = [DebtSolnAcc(**a).model_dump() for a in dfOfferAcc.to_dict(orient="records")]
    lookup   = {a["refAccNo"]:a for a in solnList}
    for ori in dfAccConsult.rename(columns={"accNo":"refAccNo","remainTerm":"term"}).to_dict(orient="records"):
        key=ori["refAccNo"]
        card.account_details.append(
            create_TDRoffer_cardAcc(lookup[key],ori,True,fgFlat,fgBalloon) if key in lookup
            else create_TDRoffer_cardAcc(ori,ori,False,fgFlat,fgBalloon))
    return DebtSolnSummary(**{
        "solutionDesc":solutionDesc,"plan":plan,"planId":planId,
        "refAccNo":", ".join(sorted(dfOffer["accNo"].tolist())),
        "planDesc":f"TDR {planDesc}",
        "installment":float(dfOffer["installment"].sum()),
        "installment_Y2":float(dfOffer["installment_Y2"].sum()),
        "installment_Y3":float(dfOffer["installment_Y3"].sum()),
        "term":int(dfOffer["remainTerm"].max()),
        "totalIntPaid":float(dfOffer["expIntTotal"].sum()),
        "constantPayment":False,"offerText":"".join(desc),
        "offerCard":card.model_dump(),"solnAcc":solnList,
    })


def NewStepOffer(planStep,planStepBalloon,mp,dfElig,dfNon,dfAcc,currentStatus):
    out=[]
    dfSt=TDRstepUpOffer(mp,dfElig)
    if dfSt["remainTerm"].max()<=TDR_maxPaymentTerm:
        out.append(TDR_summary(planStep,planStep+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                               pd.concat([dfSt,dfNon]),dfAcc,"ตามความสามารถในการจ่ายของลูกค้า",currentStatus,False,False))
    if (dfSt["remainTerm"]>dfSt["contractTerm"]).any():
        dfSB=BalloonPlan(dfSt)
        out.append(TDR_summary(planStepBalloon,planStepBalloon+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                               pd.concat([dfSB,dfNon]),dfAcc,"ตามความสามารถในการจ่ายของลูกค้า",currentStatus,False,True))
    return out


def generate_TDR_offer(dfAccConsult,dfKTBAcc,maxPayment,userInfo,currentStatus):
    dfAcc=dfAccConsult.copy()
    dfAcc["actualTerm"]     =dfAcc.apply(lambda r:findTerm(r["os"],r["intRate"],r["installment"]),axis=1)
    dfAcc["expIntTotal"]    =dfAcc.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment"],r["actualTerm"]),axis=1)
    dfAcc["contractTerm"]   =dfAcc["remainTerm"]
    dfAcc["min_installment"]=dfAcc["os"]*(dfAcc["intRate"]/12)*(1/(1-TDRmin_payment_prop))
    dfAcc["fg_eligible"]    =dfAcc["port"].isin(PossibleTDRLoan)
    dfNon=dfAcc[~dfAcc["fg_eligible"]].copy()
    dfNon["expIntTotal"]=dfNon.apply(lambda r:findInterestPaid(r["os"],r["intRate"]/12,r["installment"],r["remainTerm"]),axis=1)
    summarise_first3Y_installment(dfNon)
    dfElig=dfAcc[dfAcc["fg_eligible"]].copy()
    out=[]
    if len(dfElig)==0: return out
    dfBest=TDRBestFlatOffer(dfElig)
    out.append(TDR_summary("TDR01","TDR01"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                           pd.concat([dfBest,dfNon]),dfAcc,"ขั้นต่ำที่สุดตามเงื่อนไขธนาคาร",currentStatus,True,False))
    mp=cash_flow_analysis(dfAcc,dfKTBAcc,maxPayment,userInfo)
    if mp["installment"]<=dfElig["min_installment"].sum(): return out
    FlatDesc="ขั้นต่ำที่สุดตามเงื่อนไขธนาคาร"
    if mp["installment"]>dfBest["installment"].sum():
        dfFlat=TDRFlatOffer(mp,dfElig)
        out.append(TDR_summary("TDR02","TDR02"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                               pd.concat([dfFlat,dfNon]),dfAcc,"ตามความสามารถในการจ่ายของลูกค้า",currentStatus,True,False))
        FlatDesc="ตามความสามารถในการจ่ายของลูกค้า"
    else:
        dfFlat=dfBest.copy()
    dfFB=BalloonPlan(dfFlat)
    out.append(TDR_summary("TDR03","TDR03"+dt.datetime.now().strftime("%Y%m%d%H%M%S"),
                           pd.concat([dfFB,dfNon]),dfAcc,FlatDesc,currentStatus,True,True))
    out+=NewStepOffer("TDR04","TDR05",mp,dfElig,dfNon,dfAcc,currentStatus)
    mpR=mp.copy(); mpR["installment_Y2"]*=0.9; mpR["installment_Y3"]*=0.9
    out+=NewStepOffer("TDR06","TDR07",mpR,dfElig,dfNon,dfAcc,currentStatus)
    if (mpR["installment_Y2"]>dfElig["installment"].sum()) or (mpR["installment_Y3"]>dfElig["installment"].sum()):
        mpC=mpR.copy()
        mpC["installment_Y2"]=np.minimum(mpC["installment_Y2"],dfElig["installment"].sum())
        mpC["installment_Y3"]=np.minimum(mpC["installment_Y3"],dfElig["installment"].sum())
        out+=NewStepOffer("TDR08","TDR09",mpC,dfElig,dfNon,dfAcc,currentStatus)
    return out
