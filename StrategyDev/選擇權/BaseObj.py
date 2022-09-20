# -*- encoding: UTF-8 -*-
# CopyRight© : Kevin Cheng 鄭圳宏
# 選擇權底層
# Author: Kevin Cheng 鄭圳宏
# Create: 2021.02.09
# Update: add log write into cmd
# Version: 1

from abc import ABCMeta, abstractmethod
from scipy import log, sqrt, stats
from datetime import datetime
from enum import Enum
from numpy import isnan, exp, log

def NormCDF(x):
    return stats.norm.cdf(x)

def NormPDF(x):
    return stats.norm.pdf(x)

class OptionType(Enum):

    CALL = '買權'
    PUT = '賣權'

class BaseOption(metaclass=ABCMeta):
    
    optionType: OptionType = None
        
    def __init__(self, Underlying:float, Strike:float, Volatility:float=0.5, 
                 TimeToMaturity:[float, str, datetime]=1, RiskFreeRate:float=0.01, 
                 Premium:float=None, Dividend:float=0.0, TradingDate:[str, datetime]=None,
                 UnderType:str="SPOT", Ticker:str=None):
        """[summary]

        Args:
            Underlying (float): Underlying Price of Option
            Strike (float): Strike Price of Option
            Volatility (float, optional): Volatility (Sigma) of Option. Defaults to 0.5.
            TimeToMaturity ([float, string, datetime], optional): Time to Maturity of Option. It could be time(days over year), Maturity Date(string, dateime Obj.). Defaults to 1.
            RiskFreeRate (float, optional): Risk free rate. Defaults to 0.01.
            Premium (float, optional): The Value that Market Made. Defaults to None.
            Dividend (float, optional): Yearly Dividend if it happends. Defaults to 0.0.
            TradingDate ([string, datetime], optional): Which Date the Option Trade in the Marketon the mar. Defaults to None.
            UnderType (string, optional): Use different formula With different underlying type 
        """    
        self.S = Underlying
        self.K = Strike
        self.Sigma = Volatility
        self.Tau = TimeToMaturity / 250
        self.RF = log(1+RiskFreeRate/365)
        self.Premium = Premium
        self.Q = Dividend
        self.TradingDate = TradingDate
        self.UnderType = UnderType
        self.Ticker = Ticker
        self.UpdatePremium()
        
    def D1(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None) -> float:
        if all([S, K, Sigma, Tau, RF]):
            return (log(S / K)+(RF + (Sigma ** 2)/2.) * Tau)/(Sigma * sqrt(Tau))
        return (log(self.S / self.K)+(self.RF + (self.Sigma ** 2)/2.) * self.Tau)/(self.Sigma * sqrt(self.Tau))
    
    def D2(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None) -> float:
        if all([S, K, Sigma, Tau, RF]):
            d1 = self.D1(S, K, Sigma, Tau, RF)
            return d1 - Sigma * sqrt(Tau)
        return self.d1 - self.Sigma * sqrt(self.Tau)
    
    @abstractmethod
    def Delta(self) -> float:
        raise NotImplementedError('Should Implement Delta for different Options')
    
    def Gamma(self) -> float:
        return exp(-self.Q * self.Tau) * NormPDF(self.d1) / self.S / self.Sigma / sqrt(self.Tau)
    
    def Vega(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None, Q:float=None) -> float:
        if all([S, K, Sigma, Tau, RF, isinstance(Q, float)]):
            d1 = self.D1(S, K, Sigma, Tau, RF)
            return S * exp(Tau) * NormPDF(d1) * sqrt(Tau) # -Q 
        return self.S * exp(-self.Q * self.Tau) * NormPDF(self.d1) * sqrt(self.Tau)
    
    @abstractmethod
    def Theta(self) -> float:
        raise NotImplementedError('Should Implement Theta for different Options')
    
    @abstractmethod
    def Rho(self) -> float:
        raise NotImplementedError('Should Implement Rho for different Options')
        
    def ImpliedVolatility(self, MAX_ITERATIONS:float = 500, PRECISION:float = 1.0e-5) -> float:
        sigma = 0.5
        for i in range(1, MAX_ITERATIONS+1):
            price = self.TheoryPrice(self.S, self.K, sigma, self.Tau, self.RF)
            vega = self.Vega(self.S, self.K, sigma, self.Tau, self.RF, self.Q)
            diff = self.Premium - round(price, 1)  # our root
            if isnan(price) or isnan(sigma):
                return float('nan')
            if (abs(diff) < PRECISION):
                return sigma
            sigma = sigma + diff / vega # f(x) / f'(x)
        return sigma
    
    
    def TheoryPrice(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        return self.TheoryPriceSPOT(S, K, Sigma, Tau, RF) if self.UnderType == "SPOT" else self.TheoryPriceFUTURE(S, K, Sigma, Tau, RF)
    
    @abstractmethod
    def TheoryPriceSPOT(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        raise NotImplementedError('Should Implement TheoryPrice for different Options')
    
    @abstractmethod
    def TheoryPriceFUTURE(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        raise NotImplementedError('Should Implement TheoryPrice for different Options')
    
    @property
    def IntrinsicValue(self) -> float:
        raise NotImplementedError('Should Implement Intrinsic Value property for different Options')
    
    @property
    def TimeValue(self) -> float:
        if self.Premium:
            return self.Premium - self.IntrinsicValue()
        return 0
    
    def UpdatePremium(self, Underlying:float=None, Premium:float=None) -> float:
        if Underlying:
            self.S = Underlying
        if Premium:
            self.Premium = Premium
        if self.Premium:
            self.Sigma = self.ImpliedVolatility()
        if isinstance(self.Tau, str):
            if isinstance(self.TradingDate, str):
                pass
                
        self.d1 = self.D1()
        self.d2 = self.D2()
        self.delta = self.Delta()
        self.vega = self.Vega()
        self.gamma = self.Gamma()
        self.rho = self.Rho()
        self.theta = self.Theta()
    
class CallOption(BaseOption):
    
    optionType: OptionType= OptionType.CALL
    
    def __init__(self, Underlying:float, Strike:float, Volatility:float=0.5, 
                 TimeToMaturity:[float, str, datetime]=1, RiskFreeRate:float=0.01, 
                 Premium:float=None, Dividend:float=0.0, TradingDate:[str, datetime]=None,
                 UnderType:str="SPOT"):
        super(CallOption, self).__init__(Underlying, Strike, Volatility, TimeToMaturity, RiskFreeRate, Premium, Dividend, TradingDate, UnderType)
        
    def Delta(self):
        return exp(-self.Q * self.Tau) * NormCDF(self.d1)
    
    def Theta(self):
        first_component = -exp(self.Q * self.Tau) * self.S * NormPDF(self.d1) * self.Sigma / 2 / sqrt(self.Tau)
        second_component = -self.RF * self.K * exp(-self.RF * self.Tau) * NormCDF(self.d2)
        third_component = self.Q * self.S * exp(-self.Q * self.Tau) * NormCDF(self.d1)
        return sum([first_component, second_component, third_component])
    
    def Rho(self):
        return self.K * self.Tau * exp(-self.RF * self.Tau) * NormCDF(self.d2)
    
    def TheoryPriceSPOT(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        if all([S, K, Sigma, Tau, RF]):
            d1 = self.D1(S, K, Sigma, Tau, RF)
            d2 = self.D2(S, K, Sigma, Tau, RF)
            return S * NormCDF(d1) - K * exp(-RF * Tau) * NormCDF(d2)
        return self.S * NormCDF(self.d1) - self.K * exp(-self.RF * self.Tau) * NormCDF(self.d2)
    
    def TheoryPriceFUTURE(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        if all([S, K, Sigma, Tau, RF]):
            d1 = self.D1(S, K, Sigma, Tau, RF)
            d2 = self.D2(S, K, Sigma, Tau, RF)
            return exp(-RF * Tau) * (S * NormCDF(d1) - K * NormCDF(d2))
        return exp(-self.RF * self.Tau) * (self.S * NormCDF(self.d1) - self.K * NormCDF(self.d2))
    
    def IntrinsicValue(self):
        return max(self.S - self.K, 0)
        
class PutOption(BaseOption):
    
    optionType: OptionType= OptionType.PUT
    
    def __init__(self, Underlying:float, Strike:float, Volatility:float=0.5, 
                 TimeToMaturity:[float, str, datetime]=1, RiskFreeRate:float=0.01, 
                 Premium:float=None, Dividend:float=0.0, TradingDate:[str, datetime]=None,
                 UnderType:str="SPOT"):
        super(PutOption, self).__init__(Underlying, Strike, Volatility, TimeToMaturity, RiskFreeRate, Premium, Dividend, TradingDate, UnderType)
        
    def Delta(self):
        return -exp(-self.Q * self.Tau) * NormCDF(-self.d1)
    
    def Theta(self):
        first_component = -exp(self.Q * self.Tau) * self.S * NormPDF(-self.d1) * self.Sigma / 2 / sqrt(self.Tau)
        second_component = self.RF * self.K * exp(-self.RF * self.Tau) * NormCDF(-self.d2)
        third_component = -self.Q * self.S * exp(-self.Q * self.Tau) * NormCDF(-self.d1)
        return sum([first_component, second_component, third_component])
    
    def Rho(self):
        return -self.K * self.Tau * exp(-self.RF * self.Tau) * NormCDF(-self.d2)
    
    def TheoryPriceSPOT(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        if all([S, K, Sigma, Tau, RF]):
            d1 = self.D1(S, K, Sigma, Tau, RF)
            d2 = self.D2(S, K, Sigma, Tau, RF)
            return K * exp(-RF * Tau) * NormCDF(-d2) - S * NormCDF(-d1)
        return self.K * exp(-self.RF * self.Tau) * NormCDF(-self.d2) - self.S * NormCDF(-self.d1)
    
    def TheoryPriceFUTURE(self, S:[float, int]=None, K:[float, int]=None, Sigma:float=None, Tau:float=None, RF:float=None):
        if all([S, K, Sigma, Tau, RF]):
            d1 = self.D1(S, K, Sigma, Tau, RF)
            d2 = self.D2(S, K, Sigma, Tau, RF)
            return exp(-RF * Tau) * (K * NormCDF(-d2) - S * NormCDF(-d1))
        return exp(-self.RF * self.Tau) * (self.K * NormCDF(-self.d2) - self.S * NormCDF(-self.d1))
    
    def IntrinsicValue(self):
        return max(self.K - self.S, 0)