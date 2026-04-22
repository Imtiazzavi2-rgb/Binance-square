import os,time,random,requests,logging
CMC_API_KEY=os.environ.get("CMC_API_KEY","")
BINANCE_SQUARE_API_KEY=os.environ.get("BINANCE_SQUARE_API_KEY","")
POSTS_PER_DAY=100
INTERVAL_SECONDS=int(86400/POSTS_PER_DAY)
logging.basicConfig(level=logging.INFO,format="%(asctime)s [%(levelname)s] %(message)s")
log=logging.getLogger(__name__)
def get_trending_coins():
    headers={"X-CMC_PRO_API_KEY":CMC_API_KEY,"Accept":"application/json"}
    try:
        r=requests.get("https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest",headers=headers,params={"limit":20,"sort":"percent_change_24h","sort_dir":"desc"},timeout=10)
        data=r.json().get("data",[])
        log.info(f"✅ Got {len(data)} coins")
        return data
    except Exception as e:
        log.error(f"❌ Fetch failed:{e}")
        return []
def fmt_price(p):
    if p is None:return "N/A"
    if p<0.001:return f"{p:.8f}"
    if p<1:return f"{p:.4f}"
    if p<1000:return f"{p:.2f}"
    return f"{p:,.0f}"
def fmt_mcap(m):
    if m is None:return "N/A"
    if m>=1_000_000_000:return f"${m/1_000_000_000:.2f}B"
    if m>=1_000_000:return f"${m/1_000_000:.1f}M"
    return f"${m:,.0f}"
TEMPLATES=[
    lambda n,s,c,p,m,v:f"🚀 {n} (${s}) IS ON FIRE!\n\n📈 +{c:.1f}% in 24H\n💰 Price: ${p}\n🏦 MCap: {m}\n\n${s} is trending everywhere 🔥 Are you holding?\n\n#{s} #{n.replace(' ','')} #Crypto #Altcoin #BullRun #Binance #Web3",
    lambda n,s,c,p,m,v:f"⚡ BREAKING: ${s} pumped {c:.1f}%!\n\n💎 Price: ${p}\n📊 MCap: {m}\n🔥 Volume: {v}\n\nThe charts don't lie 📈\n\n#{s} #{n.replace(' ','')} #Crypto #Altseason #Binance #DeFi",
    lambda n,s,c,p,m,v:f"🔥 TOP TRENDING: {n}\n\n${s} | +{c:.1f}% | ${p}\n\n→ Massive volume spike 📊\n→ Smart money moving in 🏦\n→ Community going crazy 🌐\n\nMCap: {m}\n\n#{s} #Crypto #Trending #Binance #DYOR",
    lambda n,s,c,p,m,v:f"👁️ DON'T SLEEP ON ${s}!\n\n{n} up {c:.1f}% and still climbing 🚀\n\n📌 Price: ${p}\n📌 MCap: {m}\n📌 Volume: {v}\n\nSet alerts NOW 🔔\n\n#{s} #Crypto #{n.replace(' ','')} #PumpAlert #Binance",
    lambda n,s,c,p,m,v:f"💥 ${s} IS THE TALK OF CRYPTO!\n\n+{c:.1f}% in 24H 📈\n✅ Strong momentum\n✅ Volume surging\n✅ Community exploding\n\nPrice: ${p} | MCap: {m}\n\n#{s} #{n.replace(' ','')} #Crypto #BullMarket #Binance",
]
def generate_post(coin):
    q=coin.get("quote",{}).get("USD",{})
    n=coin.get("name","Unknown")
    s=coin.get("symbol","???")
    c=abs(q.get("percent_change_24h",0))
    p=fmt_price(q.get("price"))
    m=fmt_mcap(q.get("market_cap"))
    v=fmt_mcap(q.get("volume_24h"))
    return random.choice(TEMPLATES)(n,s,c,p,m,v)
def post_to_binance_square(content):
    url="https://www.binance.com/bapi/feed/v1/private/feed/post/create"
    headers={
        "Content-Type":"application/json",
        "apikey":BINANCE_SQUARE_API_KEY,
        "X-Api-Key":BINANCE_SQUARE_API_KEY,
        "api-key":BINANCE_SQUARE_API_KEY,
    }
    payload={"content":content,"contentType":"TEXT","publishType":"PUBLISH"}
    try:
        r=requests.post(url,json=payload,headers=headers,timeout=15)
        log.info(f"Response:{r.status_code} {r.text[:200]}")
        if r.status_code==200:
            resp=r.json()
            if resp.get("success") or resp.get("code")=="000000":
                log.info("✅ Posted!")
                return True
        log.warning(f"⚠️ Failed:{r.status_code}")
        return False
    except Exception as e:
        log.error(f"❌ Error:{e}")
        return False
def main():
    log.info("🚀 Bot STARTED - 100 posts/day")
    coin_pool,coin_index,last_fetch,post_count=[],0,0,0
    while True:
        now=time.time()
        if now-last_fetch>1800 or not coin_pool:
            log.info("🔄 Fetching coins...")
            coin_pool=get_trending_coins()
            if coin_pool:
                random.shuffle(coin_pool)
                coin_index=0
                last_fetch=now
            else:
                time.sleep(60)
                continue
        coin=coin_pool[coin_index%len(coin_pool)]
        coin_index+=1
        if post_to_binance_square(generate_post(coin)):
            post_count+=1
            log.info(f"📊 Posts today:{post_count}")
        log.info(f"⏳ Next in {INTERVAL_SECONDS//60}min...")
        time.sleep(INTERVAL_SECONDS)
if __name__=="__main__":
    main()
