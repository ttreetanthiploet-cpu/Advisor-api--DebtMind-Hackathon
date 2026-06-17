from pydantic import BaseModel, field_validator
from typing import Any, List, Dict
from app.services.HTML.model_HTML import OfferCard
import numpy as np

class AdvisorOutput(BaseModel):
    replyMessage : str = "ระบบประมวลผลขัดข้อง กรุณาถามคำถามใหม่อีกครั้ง"
    type: str = "text"
    newOfferSoln: List[Dict[str, Any]] = []
    newOfferSolnAcc: List[Dict[str, Any]] = []

class AdditionalPref(BaseModel):
    DebtSituation: str
    refPlanID: str = ""
    maxPaymentY2: float = np.inf
    maxPaymentY3: float = np.inf

    @field_validator("maxPaymentY2", "maxPaymentY3", mode="before")
    @classmethod
    def coerce_to_float(cls, v):
        if v is None or v == "" or v == "null":
            return np.inf
        return float(v)


class AgentInput(BaseModel):
    userMessage : str 
    narrative : str 
    maxPayment: float
    maxTerm: int
    userInfo : dict[str, Any]
    eligiblePath: list[str]
    df_offerSoln: List[Dict[str, Any]]
    dfAccConsult: List[Dict[str, Any]]
    dfKTBAcc: List[Dict[str, Any]]
    preference: AdditionalPref

class DebtSolnAcc(BaseModel):
    plan: str
    planId: str
    refAccNo: str
    installment: float
    installment_Y2: float = None
    installment_Y3: float = None
    os: float
    term: int
    intRate: float
    expIntTotal: float
    extraPaymentlastMth: float = None

class DebtSolnSummary(BaseModel):
    solutionDesc: str
    plan: str
    planId: str
    planDesc: str
    refAccNo: str
    installment: float
    installment_Y2: float = None
    installment_Y3: float = None
    term: int
    totalIntPaid: float
    constantPayment: bool
    offerCard: OfferCard
    # LLMofferText: str
    solnAcc: List[Dict[str, Any]]

    


