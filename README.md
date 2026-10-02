# Free SEC data refresh for the DCF workbook

1. Create a new private GitHub repository and upload this folder's contents.
2. In GitHub repository settings, create an Actions variable named `SEC_USER_AGENT` with a value such as `Your Name your.email@example.com`.
3. In the Actions tab, run **Refresh SEC fundamentals**. It writes `data/sec_fundamentals.json` to the repository.
4. Copy the file's Raw URL. In Google Sheets Apps Script Project Settings, add Script Property `SEC_DATA_URL` using that Raw URL.
5. Paste `Google_Sheets_sync.gs` below your existing Apps Script. Run `syncSecDataFromGitHub` once and authorize it.

The loader fills available standardized SEC XBRL values for the historical rows and balance-sheet claims. `n.a.` or `N/R` means unavailable or not separately reported; it is never assumed to be zero. Pension, lease, minority-interest, preferred-stock, and non-current-security fields require review because issuer taxonomy varies.
