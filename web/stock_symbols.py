"""
Stock Symbols Database
Eine umfassende Liste von Ticker-Symbolen mit Firmennamen für die Autocomplete-Funktion
"""

# Häufig gehandelte Aktien (Top 500+)
STOCK_SYMBOLS = [
    # Tech Giants
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corporation"},
    {"symbol": "GOOGL", "name": "Alphabet Inc. Class A"},
    {"symbol": "GOOG", "name": "Alphabet Inc. Class C"},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corporation"},
    {"symbol": "NFLX", "name": "Netflix Inc."},
    {"symbol": "AMD", "name": "Advanced Micro Devices Inc."},
    {"symbol": "INTC", "name": "Intel Corporation"},
    {"symbol": "CSCO", "name": "Cisco Systems Inc."},
    {"symbol": "ORCL", "name": "Oracle Corporation"},
    {"symbol": "CRM", "name": "Salesforce Inc."},
    {"symbol": "ADBE", "name": "Adobe Inc."},
    {"symbol": "AVGO", "name": "Broadcom Inc."},
    {"symbol": "QCOM", "name": "QUALCOMM Inc."},
    {"symbol": "TXN", "name": "Texas Instruments Inc."},
    {"symbol": "IBM", "name": "International Business Machines"},
    {"symbol": "SHOP", "name": "Shopify Inc."},
    {"symbol": "UBER", "name": "Uber Technologies Inc."},
    {"symbol": "LYFT", "name": "Lyft Inc."},
    {"symbol": "SNOW", "name": "Snowflake Inc."},
    {"symbol": "PLTR", "name": "Palantir Technologies Inc."},
    {"symbol": "RBLX", "name": "Roblox Corporation"},
    
    # Financial Services
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
    {"symbol": "BAC", "name": "Bank of America Corporation"},
    {"symbol": "WFC", "name": "Wells Fargo & Company"},
    {"symbol": "GS", "name": "Goldman Sachs Group Inc."},
    {"symbol": "MS", "name": "Morgan Stanley"},
    {"symbol": "C", "name": "Citigroup Inc."},
    {"symbol": "BLK", "name": "BlackRock Inc."},
    {"symbol": "SCHW", "name": "Charles Schwab Corporation"},
    {"symbol": "AXP", "name": "American Express Company"},
    {"symbol": "V", "name": "Visa Inc."},
    {"symbol": "MA", "name": "Mastercard Inc."},
    {"symbol": "PYPL", "name": "PayPal Holdings Inc."},
    {"symbol": "SQ", "name": "Block Inc."},
    {"symbol": "COIN", "name": "Coinbase Global Inc."},
    
    # Healthcare & Pharma
    {"symbol": "JNJ", "name": "Johnson & Johnson"},
    {"symbol": "UNH", "name": "UnitedHealth Group Inc."},
    {"symbol": "PFE", "name": "Pfizer Inc."},
    {"symbol": "ABBV", "name": "AbbVie Inc."},
    {"symbol": "TMO", "name": "Thermo Fisher Scientific"},
    {"symbol": "MRK", "name": "Merck & Co. Inc."},
    {"symbol": "ABT", "name": "Abbott Laboratories"},
    {"symbol": "LLY", "name": "Eli Lilly and Company"},
    {"symbol": "AMGN", "name": "Amgen Inc."},
    {"symbol": "GILD", "name": "Gilead Sciences Inc."},
    {"symbol": "BMY", "name": "Bristol-Myers Squibb"},
    {"symbol": "CVS", "name": "CVS Health Corporation"},
    {"symbol": "BIIB", "name": "Biogen Inc."},
    {"symbol": "MRNA", "name": "Moderna Inc."},
    
    # Consumer & Retail
    {"symbol": "WMT", "name": "Walmart Inc."},
    {"symbol": "HD", "name": "Home Depot Inc."},
    {"symbol": "COST", "name": "Costco Wholesale Corporation"},
    {"symbol": "TGT", "name": "Target Corporation"},
    {"symbol": "LOW", "name": "Lowe's Companies Inc."},
    {"symbol": "NKE", "name": "Nike Inc."},
    {"symbol": "SBUX", "name": "Starbucks Corporation"},
    {"symbol": "MCD", "name": "McDonald's Corporation"},
    {"symbol": "DIS", "name": "Walt Disney Company"},
    {"symbol": "CMCSA", "name": "Comcast Corporation"},
    {"symbol": "PEP", "name": "PepsiCo Inc."},
    {"symbol": "KO", "name": "Coca-Cola Company"},
    {"symbol": "PG", "name": "Procter & Gamble Company"},
    {"symbol": "UL", "name": "Unilever PLC"},
    
    # Energy & Utilities
    {"symbol": "XOM", "name": "Exxon Mobil Corporation"},
    {"symbol": "CVX", "name": "Chevron Corporation"},
    {"symbol": "COP", "name": "ConocoPhillips"},
    {"symbol": "SLB", "name": "Schlumberger Limited"},
    {"symbol": "EOG", "name": "EOG Resources Inc."},
    {"symbol": "NEE", "name": "NextEra Energy Inc."},
    {"symbol": "DUK", "name": "Duke Energy Corporation"},
    
    # Industrial & Manufacturing
    {"symbol": "BA", "name": "Boeing Company"},
    {"symbol": "CAT", "name": "Caterpillar Inc."},
    {"symbol": "GE", "name": "General Electric Company"},
    {"symbol": "MMM", "name": "3M Company"},
    {"symbol": "HON", "name": "Honeywell International"},
    {"symbol": "UPS", "name": "United Parcel Service"},
    {"symbol": "RTX", "name": "Raytheon Technologies"},
    {"symbol": "LMT", "name": "Lockheed Martin Corporation"},
    {"symbol": "DE", "name": "Deere & Company"},
    
    # Automotive
    {"symbol": "F", "name": "Ford Motor Company"},
    {"symbol": "GM", "name": "General Motors Company"},
    {"symbol": "TM", "name": "Toyota Motor Corporation"},
    {"symbol": "NIO", "name": "NIO Inc."},
    {"symbol": "RIVN", "name": "Rivian Automotive Inc."},
    {"symbol": "LCID", "name": "Lucid Group Inc."},
    
    # Telecommunications
    {"symbol": "T", "name": "AT&T Inc."},
    {"symbol": "VZ", "name": "Verizon Communications"},
    {"symbol": "TMUS", "name": "T-Mobile US Inc."},
    
    # Real Estate
    {"symbol": "AMT", "name": "American Tower Corporation"},
    {"symbol": "PLD", "name": "Prologis Inc."},
    {"symbol": "CCI", "name": "Crown Castle Inc."},
    {"symbol": "EQIX", "name": "Equinix Inc."},
    
    # Entertainment & Media
    {"symbol": "NFLX", "name": "Netflix Inc."},
    {"symbol": "DIS", "name": "Walt Disney Company"},
    {"symbol": "PARA", "name": "Paramount Global"},
    {"symbol": "WBD", "name": "Warner Bros. Discovery"},
    {"symbol": "SPOT", "name": "Spotify Technology SA"},
    
    # E-Commerce & Digital
    {"symbol": "BABA", "name": "Alibaba Group Holding"},
    {"symbol": "JD", "name": "JD.com Inc."},
    {"symbol": "PDD", "name": "PDD Holdings Inc."},
    {"symbol": "MELI", "name": "MercadoLibre Inc."},
    {"symbol": "EBAY", "name": "eBay Inc."},
    {"symbol": "ETSY", "name": "Etsy Inc."},
    
    # Semiconductor
    {"symbol": "TSM", "name": "Taiwan Semiconductor"},
    {"symbol": "ASML", "name": "ASML Holding NV"},
    {"symbol": "MU", "name": "Micron Technology Inc."},
    {"symbol": "AMAT", "name": "Applied Materials Inc."},
    {"symbol": "LRCX", "name": "Lam Research Corporation"},
    {"symbol": "KLAC", "name": "KLA Corporation"},
    {"symbol": "MRVL", "name": "Marvell Technology Inc."},
    
    # Biotech & Medical Devices
    {"symbol": "VRTX", "name": "Vertex Pharmaceuticals"},
    {"symbol": "REGN", "name": "Regeneron Pharmaceuticals"},
    {"symbol": "ILMN", "name": "Illumina Inc."},
    {"symbol": "ISRG", "name": "Intuitive Surgical Inc."},
    {"symbol": "DXCM", "name": "DexCom Inc."},
    
    # Airlines & Travel
    {"symbol": "AAL", "name": "American Airlines Group"},
    {"symbol": "UAL", "name": "United Airlines Holdings"},
    {"symbol": "DAL", "name": "Delta Air Lines Inc."},
    {"symbol": "LUV", "name": "Southwest Airlines Co."},
    {"symbol": "ABNB", "name": "Airbnb Inc."},
    {"symbol": "BKNG", "name": "Booking Holdings Inc."},
    {"symbol": "EXPE", "name": "Expedia Group Inc."},
    
    # Food & Beverage
    {"symbol": "MCD", "name": "McDonald's Corporation"},
    {"symbol": "SBUX", "name": "Starbucks Corporation"},
    {"symbol": "KO", "name": "Coca-Cola Company"},
    {"symbol": "PEP", "name": "PepsiCo Inc."},
    {"symbol": "MDLZ", "name": "Mondelez International"},
    {"symbol": "KHC", "name": "Kraft Heinz Company"},
    
    # Insurance
    {"symbol": "BRK.A", "name": "Berkshire Hathaway Inc. Class A"},
    {"symbol": "BRK.B", "name": "Berkshire Hathaway Inc. Class B"},
    {"symbol": "PGR", "name": "Progressive Corporation"},
    {"symbol": "MET", "name": "MetLife Inc."},
    {"symbol": "PRU", "name": "Prudential Financial"},
    {"symbol": "ALL", "name": "Allstate Corporation"},
    
    # Cloud & Software
    {"symbol": "NOW", "name": "ServiceNow Inc."},
    {"symbol": "WDAY", "name": "Workday Inc."},
    {"symbol": "TEAM", "name": "Atlassian Corporation"},
    {"symbol": "ZM", "name": "Zoom Video Communications"},
    {"symbol": "DOCU", "name": "DocuSign Inc."},
    {"symbol": "PANW", "name": "Palo Alto Networks"},
    {"symbol": "CRWD", "name": "CrowdStrike Holdings"},
    {"symbol": "ZS", "name": "Zscaler Inc."},
    {"symbol": "OKTA", "name": "Okta Inc."},
    {"symbol": "DDOG", "name": "Datadog Inc."},
    {"symbol": "NET", "name": "Cloudflare Inc."},
    {"symbol": "MDB", "name": "MongoDB Inc."},
    
    # Gaming
    {"symbol": "EA", "name": "Electronic Arts Inc."},
    {"symbol": "ATVI", "name": "Activision Blizzard"},
    {"symbol": "TTWO", "name": "Take-Two Interactive"},
    {"symbol": "RBLX", "name": "Roblox Corporation"},
    {"symbol": "U", "name": "Unity Software Inc."},
    
    # ETFs (Popular)
    {"symbol": "SPY", "name": "SPDR S&P 500 ETF Trust"},
    {"symbol": "QQQ", "name": "Invesco QQQ Trust"},
    {"symbol": "VOO", "name": "Vanguard S&P 500 ETF"},
    {"symbol": "VTI", "name": "Vanguard Total Stock Market ETF"},
    {"symbol": "IWM", "name": "iShares Russell 2000 ETF"},
    {"symbol": "DIA", "name": "SPDR Dow Jones Industrial Average ETF"},
    
    # Cryptocurrency-Related
    {"symbol": "COIN", "name": "Coinbase Global Inc."},
    {"symbol": "MSTR", "name": "MicroStrategy Inc."},
    {"symbol": "RIOT", "name": "Riot Blockchain Inc."},
    {"symbol": "MARA", "name": "Marathon Digital Holdings"},
    
    # German DAX Companies
    {"symbol": "SAP", "name": "SAP SE"},
    {"symbol": "SIE.DE", "name": "Siemens AG"},
    {"symbol": "VOW3.DE", "name": "Volkswagen AG"},
    {"symbol": "BMW.DE", "name": "BMW AG"},
    {"symbol": "DAI.DE", "name": "Daimler AG"},
    {"symbol": "BAS.DE", "name": "BASF SE"},
    {"symbol": "ALV.DE", "name": "Allianz SE"},
    {"symbol": "DTE.DE", "name": "Deutsche Telekom AG"},
    {"symbol": "DBK.DE", "name": "Deutsche Bank AG"},
    {"symbol": "ADS.DE", "name": "Adidas AG"},
    {"symbol": "RHM.DE", "name": "Rheinmetall AG"},
    
    # London Stock Exchange (FTSE 100)
    {"symbol": "HSBA.L", "name": "HSBC Holdings plc"},
    {"symbol": "BP.L", "name": "BP plc"},
    {"symbol": "SHEL.L", "name": "Shell plc"},
    {"symbol": "AZN.L", "name": "AstraZeneca plc"},
    {"symbol": "ULVR.L", "name": "Unilever plc"},
    {"symbol": "DGE.L", "name": "Diageo plc"},
    {"symbol": "GSK.L", "name": "GSK plc"},
    {"symbol": "RIO.L", "name": "Rio Tinto plc"},
    {"symbol": "LLOY.L", "name": "Lloyds Banking Group"},
    {"symbol": "VOD.L", "name": "Vodafone Group plc"},
    {"symbol": "BARC.L", "name": "Barclays plc"},
    {"symbol": "TSCO.L", "name": "Tesco plc"},
    {"symbol": "NWG.L", "name": "NatWest Group plc"},
    {"symbol": "LSEG.L", "name": "London Stock Exchange Group"},
    {"symbol": "BA.L", "name": "BAE Systems plc"},
    {"symbol": "REL.L", "name": "RELX plc"},
    {"symbol": "PRU.L", "name": "Prudential plc"},
    {"symbol": "NG.L", "name": "National Grid plc"},
    {"symbol": "IMB.L", "name": "Imperial Brands plc"},
    {"symbol": "RR.L", "name": "Rolls-Royce Holdings plc"},
    
    # Additional Popular Stocks
    {"symbol": "ARKK", "name": "ARK Innovation ETF"},
    {"symbol": "SOFI", "name": "SoFi Technologies Inc."},
    {"symbol": "HOOD", "name": "Robinhood Markets Inc."},
    {"symbol": "AFRM", "name": "Affirm Holdings Inc."},
    {"symbol": "ROKU", "name": "Roku Inc."},
    {"symbol": "PINS", "name": "Pinterest Inc."},
    {"symbol": "SNAP", "name": "Snap Inc."},
    {"symbol": "TWTR", "name": "Twitter Inc."},
    {"symbol": "SQ", "name": "Block Inc."},
]


def search_symbols(query: str, limit: int = 10):
    """
    Sucht nach Ticker-Symbolen basierend auf Symbol oder Firmennamen
    
    Args:
        query: Suchbegriff (Symbol oder Name)
        limit: Maximale Anzahl der Ergebnisse
        
    Returns:
        Liste von passenden Symbolen
    """
    if not query:
        return []
    
    query = query.upper().strip()
    results = []
    
    # Exakte Symbol-Treffer zuerst
    exact_matches = [s for s in STOCK_SYMBOLS if s["symbol"] == query]
    results.extend(exact_matches)
    
    # Symbol beginnt mit Query
    starts_with_symbol = [s for s in STOCK_SYMBOLS 
                         if s["symbol"].startswith(query) and s not in results]
    results.extend(starts_with_symbol)
    
    # Name beginnt mit Query
    starts_with_name = [s for s in STOCK_SYMBOLS 
                       if s["name"].upper().startswith(query) and s not in results]
    results.extend(starts_with_name)
    
    # Symbol enthält Query
    contains_symbol = [s for s in STOCK_SYMBOLS 
                      if query in s["symbol"] and s not in results]
    results.extend(contains_symbol)
    
    # Name enthält Query
    contains_name = [s for s in STOCK_SYMBOLS 
                    if query in s["name"].upper() and s not in results]
    results.extend(contains_name)
    
    return results[:limit]
