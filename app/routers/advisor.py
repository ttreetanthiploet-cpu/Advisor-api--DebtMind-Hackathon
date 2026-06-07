import logging
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, ConfigDict, Field

from app.services.model import AdvisorOutput
from app.services.advisor_reply import AdvisorReply

logger = logging.getLogger(__name__)

router = APIRouter()

# --------------------------------------------------------------------------- #
#  Sub-models                                                                  #
# --------------------------------------------------------------------------- #

class OfferSolution(BaseModel):
    solutionDesc: str
    plan: str
    sessionId: str
    planDesc: str
    totalExpInt: float
    term: int
    installment: float
    constantPayment: bool
    planId: str
    refAccNo: str


class ConversationDesc(BaseModel):
    consultAcc: str
    preference: str
    maxPayment: float
    maxTerm: int
    offerSoln: list[OfferSolution]
    narrative: str


class UserInfo(BaseModel):
    cif: str
    mob: int
    CustomerSegment: str
    DebtMindSegment: str
    grpDPD: int
    SumOsNCB: float
    NCBCheckDate: str
    EligibleProgram: str
    IncomeFromSystem: float
    name: str
    age: int
    employment_type: str
    InstallmentNCB_Y1: float
    InstallmentNCB_Y2: float
    InstallmentNCB_Y3: float


class AccInfoItem(BaseModel):
    cif: str
    accNo: str
    port: str
    cntrDate: str
    tdrDate: str
    currentDPD: int
    creditLimit: float
    os: float
    accruedInt: float
    intRate: float
    remainTerm: int
    installment: float


# --------------------------------------------------------------------------- #
#  Request / Response                                                          #
# --------------------------------------------------------------------------- #

class AdvisorQueryRequest(BaseModel):
    sessionId: str
    customerId: str
    userMessage: str
    conversationDesc: ConversationDesc
    userInfo: UserInfo
    accInfo: list[AccInfoItem]
    timestamp: str


class AdvisorQueryResponse(BaseModel):
    sessionId: str
    customerId: str
    userMessage: str
    agentOutput: AdvisorOutput
    timestamp: str

@router.post("/query", response_model=AdvisorQueryResponse)
async def query_advisor(request: AdvisorQueryRequest) -> AdvisorQueryResponse:
    logger.info(
        "session=%s customer=%s message=%s",
        request.sessionId,
        request.customerId,
        request.userMessage[:80],
    )
    reply = AdvisorReply(request.model_dump(by_alias=True))
    #esult = await reply.produce_reply()
    result = reply.produce_reply()
    return AdvisorQueryResponse(**result)
