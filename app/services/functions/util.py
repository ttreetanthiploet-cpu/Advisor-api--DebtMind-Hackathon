import pandas as pd
from app.services.functions.AmortiseCal import findTerm, findInterestPaid


def SummarisePayment(df_acc_consider: pd.DataFrame):
    # Create actualTerm column
    df_acc_consider["actualTerm"] = df_acc_consider.apply( lambda row: findTerm(totalOS=row["os"],
                                                                                 annual_int=row["intRate"],
                                                                                 monthly_payment=row["installment"]), axis=1)
    # Create expIntTotal column
    df_acc_consider["expIntTotal"] = df_acc_consider.apply(lambda row: findInterestPaid(Outstanding=row["os"],
                                                                                        period_int=row["intRate"] / 12,
                                                                                        first_period_payment=row["installment"],
                                                                                        payment_period=row["actualTerm"]),  axis=1 )
    return {"current_debt": df_acc_consider,
            "accNo": ",".join(sorted(df_acc_consider["accNo"].tolist())),
            "expIntTotal": df_acc_consider["expIntTotal"].sum(),
            "MaxDPD": df_acc_consider["currentDPD"].max(),
            "TotalOS": df_acc_consider["os"].sum(),
            "CurrentInstallment": df_acc_consider["installment"].sum(),
            "accruedInt": df_acc_consider["accruedInt"].sum(),
            "MaxIntRate": df_acc_consider["intRate"].max(),
            "remainTerm": df_acc_consider["remainTerm"].max(),
            "actualTerm": df_acc_consider["actualTerm"].max()}

# def fill_placeholders(text: str, 
#                       plan_map: dict) -> str:

#     for plan_id, description in plan_map.items():
#         placeholder = f"FILLINWITHPLANID_{plan_id}"
#         text = text.replace(placeholder, description)
        
#     return text

def DSR_feasibility(ktbInstallment: float,
                    NCBInstallment: float,
                    newInstallment: float,
                    income: float,
                    occ: str,
                    )->float:
    if occ == "ข้าราชการ/เจ้าหน้าที่รัฐ (Public Sector)":
        threshold = 0.9
    else:
        threshold = 0.8

    DSR = (ktbInstallment + NCBInstallment + newInstallment)/income
    return (DSR < threshold)

def DSR_feasibile_payment(ktbInstallment: float,
                          NCBInstallment: float,
                          income: float,
                          occ: str)->float:
    if occ == "ข้าราชการ/เจ้าหน้าที่รัฐ (Public Sector)":
        threshold = 0.9
    else:
        threshold = 0.8
    
    return threshold*income - ktbInstallment - NCBInstallment