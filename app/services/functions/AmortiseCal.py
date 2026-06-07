import math
import numpy as np

def findInstallment(totalOS: float,
                    annual_int: float,
                    terms: int):
    
    monthly_rate = annual_int / 12
    monthly_payment = totalOS*(monthly_rate*(1+monthly_rate)**terms)/((1+monthly_rate)**terms - 1)
    return math.ceil(monthly_payment / 100) * 100

def AmortisationTerm(Outstanding: float,
                     period_int: float,
                     first_period_payment: float,
                     period_payment_increase: float = 0):
             
    if (period_payment_increase != period_int):
        term = np.log(1 - Outstanding*(period_int-period_payment_increase)/first_period_payment ) / np.log( (1 + period_payment_increase)/(1 + period_int))
    else:
        term = Outstanding*(1+period_int)/first_period_payment
    return math.ceil(term)

def findRemainOS(Outstanding: float,
                 period_int: float,
                 first_period_payment: float,
                 payment_period: int,
                 period_payment_increase: float = 0):
    
    if (period_payment_increase != period_int):
        remainOS = ( Outstanding*(1+period_int)**payment_period  
                    - first_period_payment*( (1+period_int)**payment_period - (1+period_payment_increase)**payment_period )/(period_int - period_payment_increase) )
    else:
        remainOS = Outstanding*(1+period_int)**payment_period - first_period_payment*payment_period*(1+period_int)**(payment_period-1)
    return remainOS

def findInterestPaid(Outstanding: float,
                     period_int: float,
                     first_period_payment: float,
                     payment_period: int,
                     period_payment_increase: float = 0):
    
    if period_payment_increase == 0:
        remainOS = findRemainOS(Outstanding = Outstanding,
                                period_int = period_int,
                                first_period_payment = first_period_payment,
                                payment_period = payment_period,
                                period_payment_increase = period_payment_increase)
        total_payment = payment_period*first_period_payment
    else:
        monthly_rate = period_int
        year_int = (1+monthly_rate)**12 - 1
        year_amor = first_period_payment*( (1+monthly_rate)**12 - 1)/monthly_rate
        num_payment_year = int(payment_period/12)
        
        RemainOsLastYear = findRemainOS(Outstanding = Outstanding,
                                        period_int = year_int,
                                        first_period_payment = year_amor,
                                        payment_period = num_payment_year,
                                        period_payment_increase = period_payment_increase)
        lastyearInstallment = first_period_payment*(1+period_payment_increase)**num_payment_year
        remainOS = findRemainOS(Outstanding = RemainOsLastYear,
                                period_int = period_int,
                                first_period_payment = lastyearInstallment,
                                payment_period = payment_period - 12*num_payment_year,
                                period_payment_increase = 0)
        total_payment = (12*first_period_payment)*((1+period_payment_increase)**num_payment_year - 1)/period_payment_increase + lastyearInstallment*(payment_period - 12*num_payment_year)
    return (total_payment+remainOS) - Outstanding


def findTerm(totalOS: float,
             annual_int: float,
             monthly_payment: float,
             yearly_increase: float = 0):
    
    if (totalOS > 0):
        if yearly_increase == 0:
            return  AmortisationTerm(Outstanding = totalOS,
                                    period_int = annual_int/12,
                                    first_period_payment = monthly_payment,
                                    period_payment_increase = 0)
        else:
            monthly_rate = annual_int / 12
            year_int = (1+monthly_rate)**12 - 1
            year_amor = monthly_payment*( (1+monthly_rate)**12 - 1)/monthly_rate

            NumYear = AmortisationTerm(Outstanding = totalOS,
                                    period_int = year_int,
                                    first_period_payment = year_amor,
                                    period_payment_increase = yearly_increase)
            
            RemainOs = findRemainOS(Outstanding = totalOS,
                                    period_int = year_int,
                                    first_period_payment = year_amor,
                                    payment_period = NumYear-1,
                                    period_payment_increase = yearly_increase)
            
            NumMth = AmortisationTerm(Outstanding = RemainOs,
                                    period_int = annual_int/12,
                                    first_period_payment = monthly_payment*(1+yearly_increase)**(NumYear-1),
                                    period_payment_increase = 0)
            
            return 12*(NumYear-1) + NumMth
    else:
        return 0


            
    
    
    
    