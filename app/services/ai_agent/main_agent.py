
from app.services.model import AgentInput, AdditionalPref
from app.services.ai_agent.CSL_path import generate_CSL_offer
from app.services.ai_agent.TDR_PL_path import generate_TDR_offer
from app.services.ai_agent.GDR_path import generate_GDR_offer
from app.services.ai_agent.nonTDR_extension_path import generate_nonTDR_extension_offer
from app.services.ai_agent.config import PreferenceRANKING
from app.services.functions.util import SummarisePayment
from app.services.functions.AmortiseCal import findInterestPaid
from typing import Any, List, Dict
import pandas as pd
import json


def DebtSolution_agent(Input: AgentInput) -> dict[str, any]:
    DebtSoln = DebtSolutionObject(**(Input.model_dump()))
    result = DebtSoln.get_solution()
    return result

class DebtSolutionObject:
    def __init__(self, 
                userMessage : str,
                narrative : str,
                preference: AdditionalPref,
                maxPayment: float,
                maxTerm: int,
                userInfo : dict[str, any],
                eligiblePath: list[str],
                df_offerSoln: List[Dict[str, Any]],
                dfKTBAcc: List[Dict[str, Any]], #บัญชีสินเชื่อธนาคารกรุงไทยทั้งหมด
                dfAccConsult: List[Dict[str, Any]]): #เฉพาะบัญชีที่ลูกค้าเลือกให้พิจารณา

        self.userMessage = userMessage
        self.narrative = narrative
        self.preference = preference
        self.maxPayment = maxPayment
        self.maxTerm = maxTerm
        self.userInfo = userInfo
        self.eligiblePath = eligiblePath
        self.df_offerSoln = pd.DataFrame(df_offerSoln)
        self.dfAccConsult = pd.DataFrame(dfAccConsult)
        self.dfKTBAcc = pd.DataFrame(dfKTBAcc)

        self.prefRanking = PreferenceRANKING[(self.preference["DebtSituation"], self.userInfo.get("CustomerSegment", ""))]
        self.currentPaymentSummary = SummarisePayment(df_acc_consider = self.dfAccConsult)
        self.OriginalPayDesc = (f"สถานะของสินเชื่อในปัจจุบัน \n"
                                f"เลขที่บัญชีสินเชื่อที่พิจารณา {",".join(sorted(list(self.dfAccConsult["accNo"])))} \n"
                                f"เงินต้นคงเหลือรวม {self.currentPaymentSummary["TotalOS"]:,.2f} บาท\n")
             
    def generate_offers(self):
        offer_lst = []
        if self.userInfo.get("CustomerSegment", "") in ["Current", "C1", "C1-X"]:
            offer_lst = offer_lst + generate_CSL_offer(currentStatus = self.currentPaymentSummary,
                                                         userInfo = self.userInfo,
                                                         dfKTBAcc = self.dfKTBAcc,
                                                         maxPayment = self.maxPayment,
                                                         maxTerm = self.maxTerm)
            
        if self.userInfo.get("CustomerSegment", "") in ["Current", "C1", "C1-X"]: #Reduce installment based on remaining terms
            offer_lst = offer_lst + generate_nonTDR_extension_offer(currentStatus = self.currentPaymentSummary)

        if self.userInfo.get("CustomerSegment", "") in ["Current", "C1", "C1-X"]: #stop principal payment for 3 month
            offer_lst = offer_lst + generate_GDR_offer(currentStatus = self.currentPaymentSummary)
            
        if True:
            offer_lst = offer_lst +  generate_TDR_offer(currentStatus = self.currentPaymentSummary,
                                                        preference = self.preference,
                                                        dfKTBAcc = self.dfKTBAcc,
                                                        maxPayment = self.maxPayment,
                                                        userInfo = self.userInfo,
                                                        maxTerm = self.maxTerm)
        
            
        new_offer_lst = [offer.model_dump() for offer in offer_lst if self.check_repeat(offer)]
        self.shortlisted_offer = self.shortlist_offer(new_offer_lst = new_offer_lst)
            
    def check_repeat(self, offer):
        if len(self.df_offerSoln) > 0:
            df_match = self.df_offerSoln.loc[(self.df_offerSoln['plan']==offer.plan)
                                            & (self.df_offerSoln['refAccNo']==offer.refAccNo)
                                            & (self.df_offerSoln['term']==offer.term)
                                            & ((self.df_offerSoln['installment']-offer.installment).abs()<100)
                                            & ((self.df_offerSoln['installment_Y2'].fillna(-100) - (offer.installment_Y2 if pd.notna(offer.installment_Y2) else -100)).abs() < 100)
                                            & ((self.df_offerSoln['installment_Y3'].fillna(-100) - (offer.installment_Y3 if pd.notna(offer.installment_Y3) else -100)).abs() < 100)]
            return (len(df_match)==0)
        else:
            return True
    
    def shortlist_offer(self, new_offer_lst)->list:
        PlanList = [offer["plan"] for offer in new_offer_lst]
        print(PlanList)
        if self.preference["refPlanID"] != "":
            ref_plan = [p for p in self.prefRanking if self.preference["refPlanID"].startswith(p)][0]
            if ref_plan in ["CSL01", "CSL03", "CSL02"]:
                shortlistplan = [plan for plan in ["CSL03", "CSL02"] if plan in PlanList][:2]
            elif ref_plan in ["TDR01", "TDR02", "TDR10"]:
                shortlistplan = [plan for plan in ["TDR02", "TDR10"] if plan in PlanList][:2]
            elif ref_plan in ["TDR03"]:
                shortlistplan = [plan for plan in ["TDR03"] if plan in PlanList][:2]
            elif ref_plan in ["TDR04", "TDR05", "TDR06", "TDR07", "TDR08", "TDR09"]:
                shortlistplan = [plan for plan in ["TDR04", "TDR05"] if plan in PlanList][:2]
            else:
                shortlistplan = [plan for plan in self.prefRanking if plan in PlanList][:2]
        else:
            shortlistplan = [plan for plan in self.prefRanking if plan in PlanList][:2]
        offer_map = {offer["plan"]: offer for offer in new_offer_lst}
        return [offer_map[plan] for plan in shortlistplan]

    def get_solution(self)->dict[str, any]:
        self.generate_offers()
        agent_result = {"newOfferSoln": [{key: offer[key] for key in offer.keys() if key not in ["solnAcc", "offerText", "offerCard"]} for offer in self.shortlisted_offer],
                        "newOfferSolnAcc": [acc for offer in self.shortlisted_offer for acc in offer["solnAcc"]],
                        "newOfferCard": [{key: offer[key] for key in offer if key in ["planId", "offerCard"]} for offer in self.shortlisted_offer]}
        if len(self.shortlisted_offer)>0:
            agent_result["replyMessage"] = json.dumps([{"jsonType": "offerCard",
                                                         **{key: offer[key] for key in offer if key in ["planId", "offerCard"]}
                                                        } for offer in self.shortlisted_offer], ensure_ascii=False)
            agent_result["type"] = "json"
        elif len(self.df_offerSoln)>0:
            agent_result["replyMessage"] = "ขออภัยด้วยค่ะ จากเงื่อนไขของท่านระบบไม่พบมาตรการช่วยเหลือเพิ่มเติม กรุณาระบุข้อมูลเงื่อนไขในการชำระ (อาทิ ความสามารถในการชำระต่อเดือน/ จำนวนงวดที่ต้องการชำระสินเชื่อ หรือหากท่านต้องการปรึกษากับเจ้าหน้าที่ระบบจะดำเนินการส่งเรื่องให้เจ้าหน้าที่ติดต่อท่านกลับไป"
            agent_result["type"] = "text"
        else:
            agent_result["replyMessage"] = """ขออภัยด้วยค่ะ จากข้อมูลและสถานะบัญชีของท่าน ระบบไม่พบมาตรการช่วยเหลือในการแก้ปัญหาหนี้หากท่านต้องการปรึกษากับเจ้าหน้าที่ ระบบจะดำเนินการส่งเรื่องให้เจ้าหน้าที่ติดต่อท่านกลับไป"""
            agent_result["type"] = "text"
        return agent_result

    
    



    


    

    
    








            

    
        
    
        
    



    









    

    
    





    

