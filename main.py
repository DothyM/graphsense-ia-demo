from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import random

app = FastAPI()
templates = Jinja2Templates(directory="modelos")

# ---------------------------
# Rotas básicas
# ---------------------------

@app.get("/", response_class=JSONResponse)
async def root():
    return {"ok": True, "mensagem": "🚀 GraphSense IA pronto. Acesse /visualizar"}

@app.get("/visualizar", response_class=HTMLResponse)
async def visualizar(request: Request):
    return templates.TemplateResponse("visualizar.html", {"request": request})

# ---------------------------
# Geração de dados OHLC fake
# ---------------------------

def gen_ohlc(n=200, start=100.0):
    """Gera n candles fake (x, o, h, l, c)."""
    out = []
    last = start
    for i in range(n):
        # caminhada aleatória suave
        drift = (random.random() - 0.5) * 1.2
        open_ = last + (random.random() - 0.5) * 0.8
        close = open_ + drift + (random.random() - 0.5) * 0.8
        high = max(open_, close) + abs(random.random() * 0.9)
        low = min(open_, close) - abs(random.random() * 0.9)
        last = close
        out.append({"x": i + 1, "o": round(open_, 4), "h": round(high, 4), "l": round(low, 4), "c": round(close, 4)})
    return out

@app.get("/ohlc", response_class=JSONResponse)
async def ohlc(n: int = 200):
    n = max(60, min(500, n))
    return {"ok": True, "data": gen_ohlc(n=n)}

# ---------------------------
# IA simplificada (regras)
# ---------------------------

class ClosesIn(BaseModel):
    closes: list[float]

def sma(vals, period):
    if len(vals) < period: 
        return []
    out = []
    s = sum(vals[:period])
    out.append(s/period)
    for i in range(period, len(vals)):
        s += vals[i] - vals[i-period]
        out.append(s/period)
    return out

def rsi(vals, period=14):
    if len(vals) < period + 1:
        return []
    gains, losses = [], []
    for i in range(1, period + 1):
        chg = vals[i] - vals[i-1]
        gains.append(max(chg, 0))
        losses.append(max(-chg, 0))
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    rsis = []
    rs = (avg_gain / avg_loss) if avg_loss != 0 else float('inf')
    rsis.append(100 - (100 / (1 + rs)))
    for i in range(period + 1, len(vals)):
        chg = vals[i] - vals[i-1]
        gain = max(chg, 0)
        loss = max(-chg, 0)
        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        rs = (avg_gain / avg_loss) if avg_loss != 0 else float('inf')
        rsis.append(100 - (100 / (1 + rs)))
    return rsis

def ema(vals, period):
    if len(vals) < period: 
        return []
    k = 2/(period+1)
    out = []
    prev = sum(vals[:period])/period
    out.append(prev)
    for i in range(period, len(vals)):
        prev = vals[i]*k + prev*(1-k)
        out.append(prev)
    return out

def macd(vals, fast=12, slow=26, signal=9):
    if len(vals) < slow + signal:
        return [], []
    ema_fast = ema(vals, fast)
    ema_slow = ema(vals, slow)
    # alinhar pelo final
    macd_line = []
    offset = len(ema_slow) - len(ema_fast)
    for i in range(len(ema_fast) - offset):
        macd_line.append(ema_fast[i + offset] - ema_slow[i])
    sig = ema(macd_line, signal)
    # alinhar
    if len(sig) > 0:
        macd_line = macd_line[-len(sig):]
    return macd_line, sig

@app.post("/ia", response_class=JSONResponse)
async def ia_sinal(inp: ClosesIn):
    closes = inp.closes
    if len(closes) < 60:
        return {"ok": False, "erro": "Poucos dados"}

    sma20 = sma(closes, 20)
    sma50 = sma(closes, 50)
    rsi14 = rsi(closes, 14)
    macd_line, macd_sig = macd(closes)

    # Pega últimos valores
    s20 = sma20[-1] if sma20 else None
    s50 = sma50[-1] if sma50 else None
    r = rsi14[-1] if rsi14 else None
    m = macd_line[-1] if macd_line else None
    ms = macd_sig[-1] if macd_sig else None

    reasons = []
    score = 0

    # Regras simples
    if s20 and s50:
        if s20 > s50:
            score += 1; reasons.append("Tendência de alta (SMA20>SMA50)")
        else:
            score -= 1; reasons.append("Tendência de baixa (SMA20<SMA50)")
    if r is not None:
        if 50 < r < 70:
            score += 1; reasons.append("RSI saudável (50–70)")
        elif r >= 70:
            score -= 0.5; reasons.append("RSI sobrecomprado (>70)")
        elif r <= 30:
            score += 0.5; reasons.append("RSI sobrevendido (<30)")
        else:
            reasons.append("RSI neutro")
    if (m is not None) and (ms is not None):
        if m > ms:
            score += 1; reasons.append("MACD acima do sinal (momentum +)")
        else:
            score -= 1; reasons.append("MACD abaixo do sinal (momentum -)")

    # Conclusão
    if score >= 2:
        sinal = "COMPRA"
    elif score <= -2:
        sinal = "VENDA"
    else:
        sinal = "NEUTRO"

    # confiança 0–100
    conf = int(min(100, max(0, (score + 2) * 25)))  # -2..+2 => 0..100

    return {
        "ok": True,
        "sinal": sinal,
        "confianca": conf,
        "score": score,
        "ultimos": {"sma20": s20, "sma50": s50, "rsi14": r, "macd": m, "signal": ms},
        "motivos": reasons
    }
