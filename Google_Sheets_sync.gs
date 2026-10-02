// Add this to the Google Sheet Apps Script project after setting Script Property SEC_DATA_URL.
function syncSecDataFromGitHub() {
  const url = PropertiesService.getScriptProperties().getProperty('SEC_DATA_URL');
  if (!url) throw new Error('Set SEC_DATA_URL in Script properties first.');
  const response = UrlFetchApp.fetch(url, {muteHttpExceptions:true});
  if (response.getResponseCode() !== 200) throw new Error('GitHub data request failed: ' + response.getResponseCode());
  const data = JSON.parse(response.getContentText());
  const historyRows={revenue:6,operating_income:7,net_income:9,diluted_eps:10,operating_cash_flow:11,da:12,capex:13,working_capital_change:14,stock_comp:15,interest_expense:16,dividends:17,buybacks:18,diluted_shares:19};
  const latestRows={cash:49,current_securities:50,noncurrent_securities:51,short_debt:52,current_lt_debt:53,noncurrent_debt:54,lease_liabilities:55,pension_underfunding:56,minority_interest:57,preferred_stock:58,total_debt:59,diluted_shares_actual:60,shareholders_equity:38,goodwill:39};
  Object.entries(data.companies).forEach(([ticker,company]) => {
    const sheet=SpreadsheetApp.getActive().getSheetByName(ticker);
    if (!sheet || company.error) return;
    const years=Object.keys(company.history.revenue || {}).sort().slice(-10);
    if (years.length) sheet.getRange(5,3,1,years.length).setValues([years.map(Number)]);
    Object.entries(historyRows).forEach(([field,row]) => {
      const values=years.map(year => company.history[field]?.[year]?.value ?? 'n.a.');
      if (values.length) sheet.getRange(row,3,1,values.length).setValues([values]);
    });
    Object.entries(latestRows).forEach(([field,row]) => {
      const item=company.latest[field];
      sheet.getRange(row,3).setValue(item?.value ?? 'n.a.');
      if (row >= 49 && row <= 60) sheet.getRange(row,4).setValue(item ? 'SEC XBRL' : 'N/R');
    });
    sheet.getRange('B2').setValue(ticker + ' — ' + company.name);
  });
  SpreadsheetApp.getUi().alert('SEC data loaded. Review N/R cells before relying on valuation results.');
}
