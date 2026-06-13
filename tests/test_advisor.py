from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.services.advisor_reply import AdvisorReply

PAYLOAD: dict[str, Any] ={
    "sessionId": "12345678",
    "customerId": "1210003",
    "userMessage": "สนใจแผนรวมหนี้ ที่ผ่อนเดือนละ 1400 แต่อยากผ่อนให้หมดใน 4 ปี",
    "conversationDesc": {
      "consultAcc": "10000005,10000006",
      "offerSoln": [
        {
          "solutionDesc": "อัตราขั้นต่ำของธนาคาร",
          "plan": "PLMOU01",
          "sessionId": "12345678",
          "planDesc": "สินเชื่อรวมหนี้ MOU แบบไม่มีหลักประกัน",
          "totalExpInt": 25082.59789396898,
          "term": 96,
          "installment": 1400,
          "constantPayment": true,
          "planId": "PLMOU0120260608161328",
          "refAccNo": "10000005,10000006"
        },
        {
          "solutionDesc": "ความสามารถในการชำระ",
          "plan": "PLMOU02",
          "sessionId": "12345678",
          "planDesc": "สินเชื่อรวมหนี้ MOU แบบไม่มีหลักประกัน",
          "totalExpInt": 9388.932980102269,
          "term": 35,
          "installment": 3200,
          "constantPayment": true,
          "planId": "PLMOU0220260608161328",
          "refAccNo": "10000005,10000006"
        }
      ],
      "preference": "{\"DebtSituation\":\"DebtBurden\",\"refPlanID\":\"PLMOU0120260608161328\"}",
      "maxPayment": 1400,
      "maxTerm": 48,
      "narrative": "The user is interested in the previously proposed debt consolidation plan. They have requested a modification to the plan, specifically asking for a repayment term of 4 years. The query is being routed to the advisor to generate a revised recommendation based on this new constraint."
    },
    "userInfo": {
      "cif": "1210003",
      "mob": 60,
      "CustomerSegment": "C1",
      "DebtMindSegment": "Yellow",
      "grpDPD": 12,
      "SumOsNCB": 180000,
      "NCBCheckDate": "4/3/2025",
      "EligibleProgram": "KhunSuu, PL_MOU",
      "IncomeFromSystem": 47000,
      "name": "ซี",
      "age": 52,
      "employment_type": "ข้าราชการ",
      "InstallmentNCB_Y1": 3000,
      "InstallmentNCB_Y2": 5000,
      "InstallmentNCB_Y3": 5000
    },
    "accInfo": [
      {
        "cif": "1210003",
        "accNo": "10000004",
        "port": "สินเชื่อส่วนบุคคล",
        "cntrDate": "11/1/2021",
        "tdrDate": "na",
        "currentDPD": 12,
        "creditLimit": 500000,
        "os": 320000,
        "accruedInt": 5200,
        "intRate": 0.06,
        "remainTerm": 48,
        "installment": 7500
      },
      {
        "cif": "1210003",
        "accNo": "10000006",
        "port": "สินเชื่อดิจิตอลส่วนบุคคล",
        "cntrDate": "8/1/2023",
        "tdrDate": "na",
        "currentDPD": 5,
        "creditLimit": 150000,
        "os": 90000,
        "accruedInt": 1800,
        "intRate": 0.13,
        "remainTerm": 36,
        "installment": 3000
      },
      {
        "cif": "1210003",
        "accNo": "10000005",
        "port": "สินเชื่อบ้าน",
        "cntrDate": "3/15/22",
        "tdrDate": "na",
        "currentDPD": 0,
        "creditLimit": 80000,
        "os": 12000,
        "accruedInt": 450,
        "intRate": 0.2,
        "remainTerm": 6,
        "installment": 2100
      }
    ],
    "timestamp": "2026-06-13T13:26:32.842Z"
  }


@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c


async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_query_response_shape(client):
    response = await client.post("/advisor/query", json=PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == PAYLOAD["session_id"]
    assert data["customer_id"] == PAYLOAD["customer_id"]
    assert data["user_message"] == PAYLOAD["user_message"]
    assert "timestamp" in data
    assert set(data["agent_output"].keys()) == {
        "reply_message",
        "consider_account",
        "confidence",
        "reason",
        "narrative",
    }


async def test_stub_applies_low_confidence_gate(client):
    # gemini.complete returns {} → confidence=0 → gate overrides reply_message
    with patch("app.services.gemini.complete", new=AsyncMock(return_value={})):
        response = await client.post("/advisor/query", json=PAYLOAD)
    data = response.json()
    assert data["agent_output"]["confidence"] == 0
    assert data["agent_output"]["reply_message"] == _LOW_CONFIDENCE_MSG


async def test_produce_reply_high_confidence():
    class HighConfidenceReply(AdvisorReply):
        async def _gen_reply(self) -> None:
            self.agent_result = {
                "reply_message": "แนะนำโปรแกรม PL_MOU ค่ะ",
                "consider_account": "10000004",
                "confidence": 0.9,
                "reason": "C1 segment, eligible for PL_MOU",
                "narrative": "ลูกค้าต้องการลดภาระ",
            }

    result = await HighConfidenceReply(PAYLOAD).produce_reply()
    out = result["agent_output"]
    assert out["confidence"] == 0.9
    assert out["reply_message"] == "แนะนำโปรแกรม PL_MOU ค่ะ"


async def test_produce_reply_exception_returns_system_error():
    class FailingReply(AdvisorReply):
        async def _gen_reply(self) -> None:
            raise RuntimeError("LLM unavailable")

    result = await FailingReply(PAYLOAD).produce_reply()
    out = result["agent_output"]
    # Exception path returns AdvisorMessage() defaults without confidence gate
    assert out["reply_message"] == "ระบบประมวลผลขัดข้อง กรุณาถามคำถามใหม่อีกครั้ง"
    assert out["confidence"] == 0


async def test_df_acc_parsed_from_acc_info():
    reply = AdvisorReply(PAYLOAD)
    assert len(reply.df_acc) == 1
    assert reply.df_acc.iloc[0]["accNo"] == "10000004"


async def test_conversation_desc_extracted():
    reply = AdvisorReply(PAYLOAD)
    assert reply.conversation_data["narrative"] == "ลูกค้าต้องการลดภาระ"
    assert reply.conversation_data["tone_guidance"] == "very_empathetic"
