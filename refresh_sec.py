import json, os, time, urllib.request
from datetime import datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parent
HEADERS = {'User-Agent': os.getenv('SEC_USER_AGENT', 'DCF workbook contact@example.com')}
FLOW = {'revenue':['RevenueFromContractWithCustomerExcludingAssessedTax','SalesRevenueNet','Revenues'],'operating_income':['OperatingIncomeLoss'],'net_income':['NetIncomeLoss'],'diluted_eps':['EarningsPerShareDiluted'],'operating_cash_flow':['NetCashProvidedByUsedInOperatingActivities'],'da':['DepreciationDepletionAndAmortization','DepreciationDepletionAndAmortizationPropertyPlantAndEquipment'],'capex':['PaymentsToAcquirePropertyPlantAndEquipment'],'working_capital_change':['IncreaseDecreaseInOperatingAssetsAndLiabilities'],'stock_comp':['ShareBasedCompensation'],'interest_expense':['InterestExpenseNonoperating','InterestExpense'],'dividends':['PaymentsOfDividendsCommonStock'],'buybacks':['PaymentsForRepurchaseOfCommonStock'],'diluted_shares':['WeightedAverageNumberOfDilutedSharesOutstanding']}
INSTANT = {'cash':['CashAndCashEquivalentsAtCarryingValue'],'current_securities':['MarketableSecuritiesCurrent','ShortTermInvestments'],'noncurrent_securities':['MarketableSecuritiesNoncurrent','AvailableForSaleSecuritiesNoncurrent'],'short_debt':['ShortTermBorrowings'],'current_lt_debt':['LongTermDebtCurrent'],'noncurrent_debt':['LongTermDebtNoncurrent'],'lease_liabilities':['OperatingLeaseLiability','FinanceLeaseLiability'],'pension_underfunding':['DefinedBenefitPlanLiabilitiesNoncurrent'],'minority_interest':['MinorityInterest'],'preferred_stock':['PreferredStocksIncludingAdditionalPaidInCapital'],'shareholders_equity':['StockholdersEquity'],'goodwill':['Goodwill'],'intangibles':['FiniteLivedIntangibleAssetsNet'],'diluted_shares_actual':['EntityCommonStockSharesOutstanding']}
def units(f, tag):
 for ns in ('us-gaap','dei'):
  x=f.get('facts',{}).get(ns,{}).get(tag)
  if x: return x.get('units',{})
 return {}
def annual(f, tags, field):
 unit='USD/shares' if field=='diluted_eps' else ('shares' if field=='diluted_shares' else 'USD'); out={}
 for tag in tags:
  for x in units(f,tag).get(unit,[]):
   if x.get('form')!='10-K' or not x.get('start') or not x.get('end'): continue
   if not 300 <= (datetime.fromisoformat(x['end'])-datetime.fromisoformat(x['start'])).days <= 430: continue
   v=x.get('val'); v=v if field=='diluted_eps' else (v/1e6 if v is not None else None)
   out[x['end'][:4]]={'value':abs(v) if v is not None else None,'tag':tag}
 return dict(sorted(out.items())[-10:])
def latest(f,tags,field):
 unit='shares' if field=='diluted_shares_actual' else 'USD'; a=[]
 for tag in tags: a += [{**x,'tag':tag} for x in units(f,tag).get(unit,[]) if x.get('form')=='10-K' and x.get('end')]
 if not a:return None
 x=max(a,key=lambda z:(z.get('end',''),z.get('filed',''))); v=x.get('val')
 return {'value':v if field=='diluted_shares_actual' else (abs(v)/1e6 if v is not None else None),'tag':x['tag']}
def main():
 cs=json.loads((ROOT/'companies.json').read_text()); out={'generated_at':datetime.utcnow().isoformat()+'Z','units':'USD millions except EPS','companies':{}}
 for c in cs:
  try:
   cik=str(c['cik']).zfill(10); r=urllib.request.Request(f'https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json',headers=HEADERS); f=json.load(urllib.request.urlopen(r,timeout=45)); h={k:annual(f,v,k) for k,v in FLOW.items()}; l={k:latest(f,v,k) for k,v in INSTANT.items()}; l['total_debt']={'value':sum((l[k]or{}).get('value',0)or 0 for k in ['short_debt','current_lt_debt','noncurrent_debt'])}; out['companies'][c['ticker']]={'name':c['name'],'history':h,'latest':l}
  except Exception as e: out['companies'][c['ticker']]={'name':c['name'],'error':str(e)}
  time.sleep(.15)
 (ROOT/'data').mkdir(exist_ok=True); (ROOT/'data'/'sec_fundamentals.json').write_text(json.dumps(out,indent=2))
if __name__=='__main__': main()
