from app.services.model import AdvisorOutput, AgentInput, DebtSolnSummary, AdditionalPref
from app.services.ai_agent.main_agent import DebtSolution_agent
from app.services.HTML.offer_card_render import render_offer_card
import numpy as np
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

        required_offer_cols = [col for col in DebtSolnSummary.model_fields.keys() if col not in ["solnAcc"]]
        df_offerSoln = (pd.DataFrame(data['conversationDesc']['offerSoln'])
                        .rename(columns={'totalExpInt': 'totalIntPaid'})
                        .reindex(columns=required_offer_cols))
        preference = json.loads(data.get("conversationDesc", {}).get("preference", ""))

        self.agent_input = {"userMessage": data.get("userMessage", ""),
                            'narrative': data.get("conversationDesc", {}).get("narrative", ""),
                            "preference": AdditionalPref(**preference),
                            "maxTerm": np.maximum(data.get("conversationDesc", {}).get("maxTerm", ""), 3),
                            'maxPayment': np.minimum(np.maximum(data.get("conversationDesc", {}).get("maxPayment"), 100), 0.9*dfAccConsult["installment"].sum()),
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
        import webbrowser
        import os

        cards = self.agent_result["OfferCardHTML"]

        output_dir = os.path.abspath("local_offer_cards_pages")
        os.makedirs(output_dir, exist_ok=True)


        def build_html(card, page_idx):
            return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Offer Card - Page {page_idx}</title>

            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background: #f3f4f6;
                    padding: 20px;
                    display: flex;
                    justify-content: center;
                }}

                .card {{
                    max-width: 500px;
                    width: 100%;
                }}
            </style>
        </head>

        <body>
            <div class="card">
                {card["HTML"]}
            </div>
        </body>
        </html>
        """


        def render_pages():
            for page_idx, card in enumerate(cards, start=1):

                html = build_html(card, page_idx)

                file_path = os.path.join(
                    output_dir,
                    f"offer_card_{page_idx}.html"
                )

                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(html)

                print(f"Generated: {file_path}")

                webbrowser.open(f"file://{file_path}")


        render_pages()
        #del self.agent_result["newOfferCard"]


    def produce_reply(self):
        # try:
        if True:
            self._gen_reply()
            self._produceHTML()
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