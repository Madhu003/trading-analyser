"""
Static ticker universes, kept separate from config.py so the list of
symbols (which is long and churns independently of pipeline settings)
doesn't clutter the file you actually edit for strategy/risk tuning.

NIFTY_500 below is a curated snapshot of ~500 large/mid/small-cap NSE-listed
stocks spanning all major sectors (banking, IT, pharma, auto, FMCG, energy,
metals, infra, capital goods, chemicals, realty, PSU, new-age/tech, etc.),
in yfinance's ".NS" ticker format.

This is NOT pulled live from NSE/index data, so it will drift from the
*official* NIFTY 500 index constituents over time (index rebalancing,
delistings, IPOs). For anything beyond local research/backtesting, refresh
it from NSE's official constituent CSV:
https://www.niftyindices.com/indices/equity/broad-based-indices/nifty-500
and regenerate this list (append ".NS" to each `Symbol` column value).
"""

NIFTY_500: list[str] = sorted(set([
    # --- Nifty 50 / large-cap core ---
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "BAJFINANCE.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "NESTLEIND.NS", "WIPRO.NS",
    "HCLTECH.NS", "BAJAJFINSV.NS", "ADANIENT.NS", "ADANIPORTS.NS",
    "POWERGRID.NS", "NTPC.NS", "JSWSTEEL.NS", "TATASTEEL.NS", "TATAMOTORS.NS",
    "TATACONSUM.NS", "TECHM.NS", "GRASIM.NS", "CIPLA.NS", "DRREDDY.NS",
    "DIVISLAB.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS",
    "BRITANNIA.NS", "COALINDIA.NS", "BPCL.NS", "ONGC.NS", "IOC.NS",
    "HINDALCO.NS", "APOLLOHOSP.NS", "SBILIFE.NS", "HDFCLIFE.NS",
    "INDUSINDBK.NS", "UPL.NS", "SHREECEM.NS", "M&M.NS",

    # --- Nifty Next 50 / broader large-cap ---
    "DMART.NS", "PIDILITIND.NS", "GODREJCP.NS", "DABUR.NS", "MARICO.NS",
    "COLPAL.NS", "BERGEPAINT.NS", "HAVELLS.NS", "SIEMENS.NS", "ABB.NS",
    "BOSCHLTD.NS", "CUMMINSIND.NS", "PAGEIND.NS", "MCDOWELL-N.NS", "GAIL.NS",
    "PETRONET.NS", "INDIGO.NS", "VEDL.NS", "JINDALSTEL.NS", "SAIL.NS",
    "NMDC.NS", "HINDPETRO.NS", "AMBUJACEM.NS", "ACC.NS", "RAMCOCEM.NS",
    "DALBHARAT.NS", "JKCEMENT.NS", "BANDHANBNK.NS", "IDFCFIRSTB.NS",
    "FEDERALBNK.NS", "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "UNIONBANK.NS",
    "INDIANB.NS", "RBLBANK.NS", "AUBANK.NS", "YESBANK.NS", "LICHSGFIN.NS",
    "PFC.NS", "RECLTD.NS", "IRFC.NS", "BHEL.NS", "BEL.NS", "HAL.NS",
    "MAZDOCK.NS", "GRSE.NS", "COCHINSHIP.NS", "IRCTC.NS", "CONCOR.NS",
    "GMRINFRA.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "ADANIENSOL.NS",
    "ATGL.NS", "TATAPOWER.NS", "TORNTPOWER.NS", "CESC.NS", "NHPC.NS",
    "SJVN.NS", "THERMAX.NS", "KEC.NS", "KALPATPOWR.NS", "ENGINERSIN.NS",

    # --- Auto & ancillary ---
    "MOTHERSON.NS", "BALKRISIND.NS", "MRF.NS", "APOLLOTYRE.NS", "CEATLTD.NS",
    "EXIDEIND.NS", "AMARAJABAT.NS", "BHARATFORG.NS", "ENDURANCE.NS",
    "SUNDRMFAST.NS", "TIINDIA.NS", "SCHAEFFLER.NS", "SKFINDIA.NS",
    "TIMKEN.NS", "ASHOKLEY.NS", "ESCORTS.NS", "VSTTILLERS.NS", "SONACOMS.NS",

    # --- Pharma & healthcare ---
    "LUPIN.NS", "AUROPHARMA.NS", "ZYDUSLIFE.NS", "TORNTPHARM.NS", "ALKEM.NS",
    "GLENMARK.NS", "IPCALAB.NS", "BIOCON.NS", "LAURUSLABS.NS", "GLAND.NS",
    "ABBOTINDIA.NS", "PFIZER.NS", "SANOFI.NS", "GLAXO.NS", "NATCOPHARM.NS",
    "AJANTPHARM.NS", "JBCHEPHARM.NS", "FDC.NS", "SUVEN.NS", "GRANULES.NS",
    "FORTIS.NS", "MAXHEALTH.NS", "NH.NS", "METROPOLIS.NS", "LALPATHLAB.NS",
    "THYROCARE.NS", "KIMS.NS",

    # --- IT & new-age tech ---
    "LTIM.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "LTTS.NS",
    "OFSS.NS", "NAUKRI.NS", "TATAELXSI.NS", "CYIENT.NS", "KPITTECH.NS",
    "ZENSARTECH.NS", "SONATSOFTW.NS", "NEWGEN.NS", "INTELLECT.NS",
    "RATEGAIN.NS", "HAPPSTMNDS.NS", "ROUTE.NS", "TANLA.NS", "ZOMATO.NS",
    "PAYTM.NS", "NYKAA.NS", "POLICYBZR.NS", "DELHIVERY.NS", "CARTRADE.NS",
    "EASEMYTRIP.NS", "MAPMYINDIA.NS",

    # --- Banking / NBFC / insurance ---
    "CHOLAFIN.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS", "PNBHOUSING.NS",
    "LICI.NS", "ICICIPRULI.NS", "ICICIGI.NS", "SBICARD.NS", "GICRE.NS",
    "NIACL.NS", "STARHEALTH.NS", "BAJAJHLDNG.NS", "SHRIRAMFIN.NS",
    "CREDITACC.NS", "UJJIVANSFB.NS", "EQUITASBNK.NS", "DCBBANK.NS",
    "SOUTHBANK.NS", "KARURVYSYA.NS", "CUB.NS", "PNBHOUSING.NS",

    # --- FMCG / consumer ---
    "EMAMILTD.NS", "VBL.NS", "UBL.NS", "RADICO.NS", "GILLETTE.NS",
    "PGHH.NS", "JYOTHYLAB.NS", "HONAUT.NS", "CCL.NS", "BAJAJCON.NS",
    "KRBL.NS", "GODREJIND.NS", "GODREJPROP.NS",

    # --- Retail / consumer durables ---
    "TRENT.NS", "ABFRL.NS", "SHOPERSTOP.NS", "VMART.NS", "BATAINDIA.NS",
    "RELAXO.NS", "CROMPTON.NS", "VOLTAS.NS", "BLUESTARCO.NS", "WHIRLPOOL.NS",
    "DIXON.NS", "AMBER.NS", "POLYCAB.NS", "KEI.NS", "FINPIPE.NS",
    "FINCABLES.NS", "ORIENTELEC.NS",

    # --- Cement ---
    "JKLAKSHMI.NS", "HEIDELBERG.NS", "PRSMJOHNSN.NS", "STARCEMENT.NS",
    "SAGCEM.NS", "INDIACEM.NS",

    # --- Metals & mining ---
    "JSWENERGY.NS", "NALCO.NS", "HINDZINC.NS", "RATNAMANI.NS", "WELCORP.NS",
    "APLAPOLLO.NS", "JSL.NS", "MOIL.NS", "GRAPHITE.NS", "HEG.NS",
    "HINDCOPPER.NS",

    # --- Oil, gas & energy ---
    "OIL.NS", "MGL.NS", "IGL.NS", "GUJGASLTD.NS", "GSPL.NS", "AEGISCHEM.NS",
    "CASTROLIND.NS",

    # --- Infra & construction ---
    "L&TFH.NS", "IRB.NS", "NCC.NS", "KNRCON.NS", "PNCINFRA.NS", "JKIL.NS",
    "HGINFRA.NS", "ASHOKA.NS", "RVNL.NS", "KALYANKJIL.NS", "RITES.NS",
    "IRCON.NS", "TITAGARH.NS",

    # --- Chemicals ---
    "SRF.NS", "DEEPAKNTR.NS", "AARTIIND.NS", "ATUL.NS", "NAVINFLUOR.NS",
    "VINATIORGA.NS", "PIIND.NS", "TATACHEM.NS", "GNFC.NS", "GSFC.NS",
    "CHAMBLFERT.NS", "COROMANDEL.NS", "RCF.NS", "NFL.NS", "FACT.NS",
    "CLEAN.NS", "FINEORG.NS", "GALAXYSURF.NS", "ALKYLAMINE.NS",
    "BALAMINES.NS",

    # --- Textiles ---
    "RAYMOND.NS", "WELSPUNIND.NS", "TRIDENT.NS", "KPRMILL.NS",
    "VTL.NS", "ARVIND.NS",

    # --- Media & entertainment ---
    "ZEEL.NS", "SUNTV.NS", "PVRINOX.NS", "NETWORK18.NS", "TV18BRDCST.NS",
    "DBCORP.NS", "JAGRAN.NS", "SAREGAMA.NS",

    # --- Realty ---
    "DLF.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "PHOENIXLTD.NS", "BRIGADE.NS",
    "SOBHA.NS", "MAHLIFE.NS", "SUNTECK.NS", "IBREALEST.NS",

    # --- Capital goods & engineering ---
    "CGPOWER.NS", "KIRLOSENG.NS", "LMW.NS", "GRINDWELL.NS", "CARBORUNIV.NS",
    "SUPRAJIT.NS",

    # --- Aviation & logistics ---
    "SPICEJET.NS", "MAHLOG.NS", "TCI.NS", "VRLLOG.NS", "GATI.NS",
    "ALLCARGO.NS",

    # --- Sugar & agri ---
    "BALRAMCHIN.NS", "TRIVENI.NS", "DWARKESH.NS", "DHAMPURSUG.NS",
    "EIDPARRY.NS",

    # --- Paints ---
    "KANSAINER.NS", "AKZOINDIA.NS", "INDIGOPNTS.NS",

    # --- Diversified / PSU / misc ---
    "TATAINVEST.NS", "NBCC.NS", "HUDCO.NS", "MIDHANI.NS", "BEML.NS",
    "ITI.NS", "HFCL.NS", "SCI.NS", "PCJEWELLER.NS", "THANGAMAYL.NS",
    "TBZ.NS", "ASTRAL.NS", "SUPREMEIND.NS", "CERA.NS", "KAJARIACER.NS",
    "SOMANYCERA.NS", "CENTURYPLY.NS", "GREENPANEL.NS",

    # --- Banking / NBFC / capital markets, extended ---
    "IIFL.NS", "IIFLWAM.NS", "JMFINANCIL.NS", "MOTILALOFS.NS", "CDSL.NS",
    "BSE.NS", "MCX.NS", "CAMS.NS", "KFINTECH.NS", "ANGELONE.NS",
    "J&KBANK.NS", "POONAWALLA.NS", "FIVESTAR.NS", "AAVAS.NS", "HOMEFIRST.NS",

    # --- Auto & ancillary, extended ---
    "TVSMOTOR.NS", "FORCEMOT.NS", "ATULAUTO.NS", "OLECTRA.NS", "JBMA.NS",
    "SUBROS.NS", "GABRIEL.NS", "MINDACORP.NS", "JAMNAAUTO.NS", "FIEMIND.NS",

    # --- IT & new-age tech, extended ---
    "BIRLASOFT.NS", "DATAPATTNS.NS", "CMSINFO.NS", "3IINFOLTD.NS",
    "INFIBEAM.NS", "JIOFIN.NS", "HONASA.NS", "IXIGO.NS", "SAGILITY.NS",

    # --- Pharma & healthcare, extended ---
    "MANKIND.NS", "STAR.NS", "SEQUENT.NS", "INDOCO.NS", "CAPLIPOINT.NS",
    "MARKSANS.NS", "WOCKPHARMA.NS", "JUBLPHARMA.NS", "SYNGENE.NS",
    "NEULANDLAB.NS", "RAINBOW.NS", "ASTERDM.NS", "GLOBALHEALTH.NS",

    # --- FMCG / consumer, extended ---
    "PATANJALI.NS", "ZYDUSWELL.NS", "HATSUN.NS", "DIAMONDYD.NS", "BIKAJI.NS",
    "DODLA.NS", "VADILALIND.NS", "HERITGFOOD.NS", "LTFOODS.NS",
    "GODFRYPHLP.NS", "VSTIND.NS",

    # --- Retail / consumer durables, extended ---
    "ARVINDFASN.NS", "METROBRAND.NS", "CAMPUS.NS", "KHADIM.NS",
    "LIBERTSHOE.NS", "PGEL.NS", "IFBIND.NS", "VGUARD.NS", "TTKPRESTIG.NS",
    "HAWKINCOOK.NS", "BAJAJELEC.NS",

    # --- Capital goods & engineering, extended ---
    "TRITURBINE.NS", "ELGIEQUIP.NS", "AIAENG.NS", "KIRLOSPNU.NS", "TIL.NS",
    "ISGEC.NS", "GREAVESCOT.NS", "TIMETECHNO.NS", "WABAG.NS",

    # --- Power / energy, extended ---
    "RELINFRA.NS", "RPOWER.NS", "INDIAGRID.NS", "PGINVIT.NS", "IEX.NS",
    "PTC.NS",

    # --- Metals & mining, extended ---
    "SHYAMMETL.NS", "SARDAEN.NS", "KIOCL.NS", "MAITHANALL.NS",

    # --- Chemicals, extended ---
    "SUDARSCHEM.NS", "ROSSARI.NS", "ANURAS.NS", "FLUOROCHEM.NS",
    "LINDEINDIA.NS", "SOLARINDS.NS", "NOCIL.NS", "DEEPAKFERT.NS",

    # --- Cement, extended ---
    "ORIENTCEM.NS", "KESORAMIND.NS", "MANGLMCEM.NS", "NUVOCO.NS",

    # --- Textiles, extended ---
    "SIYSIL.NS", "GARFIBRES.NS", "INDORAMA.NS", "NAHARSPING.NS",
    "DOLLAR.NS", "RUPA.NS", "LUXIND.NS",

    # --- Realty, extended ---
    "LODHA.NS", "SIGNATURE.NS", "ANANTRAJ.NS", "KOLTEPATIL.NS",
    "PURVA.NS",

    # --- Telecom, extended ---
    "IDEA.NS", "TATACOMM.NS", "RAILTEL.NS", "GTLINFRA.NS",

    # --- Shipping / logistics, extended ---
    "GESHIP.NS",

    # --- Agrichem / seeds, extended ---
    "KAVERISEED.NS", "RALLIS.NS", "BAYERCROP.NS", "SUMICHEM.NS",
    "DHANUKA.NS", "INSECTICID.NS",

    # --- Jewellery, extended ---
    "SENCO.NS", "RAJESHEXPO.NS",

    # --- Sugar, extended ---
    "RENUKA.NS", "DALMIASUG.NS",

    # --- Additional large/mid-cap fill-ins across sectors ---
    "ABCAPITAL.NS", "ABSLAMC.NS", "HDFCAMC.NS", "UTIAMC.NS", "NAM-INDIA.NS",
    "SUNDARMFIN.NS", "REPCO.NS", "SPARC.NS", "GLENMARK.NS", "AARTIDRUGS.NS",
    "GUFICBIO.NS", "MEDPLUS.NS", "APLLTD.NS", "PGHL.NS", "JUBLFOOD.NS",
    "WESTLIFE.NS", "SAPPHIRE.NS", "DEVYANI.NS", "SANOFICONR.NS", "BARBEQUE.NS",
]))
