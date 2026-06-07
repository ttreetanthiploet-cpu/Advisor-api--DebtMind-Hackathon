from pydantic import BaseModel
from typing import Any, List, Dict
from app.services.HTML.model_HTML import OfferCard

class AdvisorOutput(BaseModel):
    replyMessage : str = "ระบบประมวลผลขัดข้อง กรุณาถามคำถามใหม่อีกครั้ง"
    type: str = "text"
    newOfferSoln: List[Dict[str, Any]] = []
    newOfferSolnAcc: List[Dict[str, Any]] = []

class AgentInput(BaseModel):
    userMessage : str 
    narrative : str 
    preference: str
    maxPayment: float
    maxTerm: int
    userInfo : dict[str, Any]
    eligiblePath: list[str]
    df_offerSoln: List[Dict[str, Any]]
    dfAccConsult: List[Dict[str, Any]]
    dfKTBAcc: List[Dict[str, Any]]

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
    offerText: str
    solnAcc: List[Dict[str, Any]]

    


