import time
import requests
import pandas as pd
import yfinance as yf
import ta

# --- YAPILANDIRMA ---
TOKEN = "7864817757:AAFTxT7Lq9eWvXw-M15FvEwUjU_Jj3Z8K80"
CHAT_ID = "123456789"

BIST_30 = [
    "THYAO.IS",
    "GARAN.IS",
    "AKBNK.IS",
    "EREGL.IS",
    "BIMAS.IS",
    "KCHOL.IS",
    "SAHOL.IS",
    "SISE.IS",
    "ASELS.IS",
    "TUPRS.IS",
]


def telegram_gonder(mesaj):
  url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
  payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Telegram hatası: {e}")


def piyasa_analizi_yap():
  print("BIST 30 taranıyor ve analiz yapılıyor...")

  try:
    bist100 = yf.download(
        "XU100.IS", period="5d", interval="1d", progress=False
    )
    if not bist100.empty:
      son_fiyat = float(bist100["Close"].iloc[-1])
      onceki_fiyat = float(bist100["Close"].iloc[-2])
      if son_fiyat < onceki_fiyat * 0.985:
        telegram_gonder(
            "⚠️ **PİYASA UYARISI:** BIST 100 genel trendi negatif! Riskten"
            " kaçınmak için nakitte kalıyoruz."
        )
        return
  except Exception as e:
    print(f"Endeks okuma hatası: {e}")

  sinyaller = []

  for hisse in BIST_30:
    try:
      df = yf.download(hisse, period="3mo", interval="1d", progress=False)
      if df.empty or len(df) < 20:
        continue

      df["RSI"] = ta.momentum.rsi(df["Close"], window=14)
      df["EMA20"] = ta.trend.ema_indicator(df["Close"], window=20)

      son_kapanis = float(df["Close"].iloc[-1])
      son_rsi = float(df["RSI"].iloc[-1])
      son_ema = float(df["EMA20"].iloc[-1])
      son_hacim = float(df["Volume"].iloc[-1])
      ort_hacim = float(df["Volume"].rolling(window=20).mean().iloc[-1])

      if (
          son_rsi < 55
          and son_kapanis > son_ema
          and son_hacim > (ort_hacim * 1.1)
      ):
        hedef = round(son_kapanis * 1.12, 2)
        stop = round(son_kapanis * 0.96, 2)
        
        mesaj_parcasi = (
            f"📈 **{hisse.replace('.IS', '')}**\n"
            f"• Fiyat: {son_kapanis:.2f} TL\n"
            f"• RSI: {son_rsi:.1f}\n"
            f"• Hedef: {hedef} TL\n"
            f"• Stop: {stop} TL\n"
            f"⏳ **Tahmini Vade:** 1-3 Hafta\n"
        )
        sinyaller.append(mesaj_parcasi)
    except Exception as ex:
      print(f"{hisse} analiz hatası: {ex}")

  if sinyaller:
    rapor = (
        "🚀 **BIST 30 UZMAN AJAN - GÜNLÜK RAPOR** 🚀\n\n"
        + "\n".join(sinyaller[:3])
        + "\n💼 *Portföy Önerisi: Bütçe eşit olarak paylaştırılmıştır.*"
    )
    telegram_gonder(rapor)
  else:
    telegram_gonder(
        "🔍 **BIST 30 Raporu:** Bugün filtrelerimize tam uyan güçlü hacimli"
        " kırılım görülmedi. Nakitte bekliyoruz."
    )


if __name__ == "__main__":
  piyasa_analizi_yap()
