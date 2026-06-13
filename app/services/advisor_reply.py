from app.services.model import AdvisorOutput, AgentInput, DebtSolnSummary, AdditionalPref
from app.services.ai_agent.main_agent import DebtSolution_agent
from app.services.HTML.offer_card_render import render_offer_card
import datetime as dt
import pandas as pd
import json

class AdvisorReply:
    def __init__(self, data: dict[str, any]):

        self.input_data = data

        consultedAccList = [x.strip() for x in data.get("conversationDesc", {}).get("consultAcc", "").split(",")]
        df_acc = pd.DataFrame(data['accInfo'])
        dfAccConsult = df_acc[df_acc['accNo'].isin(consultedAccList)]
        eligiblePath = [x.strip() for x in self.input_data['userInfo']["EligibleProgram"].split(",")]

        required_offer_cols = [col for col in DebtSolnSummary.model_fields.keys() if col not in ["offerText", "solnAcc"]]
        df_offerSoln = pd.DataFrame(data['conversationDesc']['offerSoln']).reindex(columns=required_offer_cols)

        preference = json.loads(data.get("conversationDesc", {}).get("preference", ""))

        self.agent_input = {"userMessage": data.get("userMessage", ""),
                            'narrative': data.get("conversationDesc", {}).get("narrative", ""),
                            "preference": AdditionalPref(**preference),
                            "maxTerm": data.get("conversationDesc", {}).get("maxTerm", ""),
                            'maxPayment': data.get("conversationDesc", {}).get("maxPayment", ""),
                            "userInfo": data.get("userInfo", {}),
                            "eligiblePath": eligiblePath,
                            "df_offerSoln": df_offerSoln.to_dict(orient="records"),
                            "dfAccConsult": dfAccConsult.to_dict(orient="records"),
                            "dfKTBAcc": df_acc.to_dict(orient="records")}

    def _gen_reply(self):
        self.agent_result = DebtSolution_agent(AgentInput(**self.agent_input))
        
    
    def _produceHTML(self):
        self.agent_result["OfferCardHTML"] = [{"planID": offer_card["planId"],
                                               "HTML": render_offer_card(offer_card["offerCard"])} 
                                               for offer_card in self.agent_result["newOfferCard"]]
        #del self.agent_result["newOfferCard"]


    def produce_reply(self):
        # try:
        if True:
            self._gen_reply()
            # self._produceHTML()
            agentOutput = AdvisorOutput(**self.agent_result)
        # except:
        #     agentOutput = AdvisorOutput()
        
        Reply = {"sessionId": self.input_data.get("sessionId"),
                 "customerId": self.input_data.get("customerId"),
                 "userMessage": self.input_data.get("userMessage"),
                 "agentOutput": agentOutput.model_dump(),
                 "timestamp": dt.datetime.now().isoformat(timespec="milliseconds")
                 }

        return Reply