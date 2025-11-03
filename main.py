from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import random, datetime

app = FastAPI(title="GraphSense IA Demo")

# Permite acesso ao frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dados simulados de candles
def gerar_candles(qtd=40):
    base = 100
    candles = []
    for i in range(qtd):
        open_ = base + random.uniform(-1, 1)
        close = open_ + random.uniform(-0.8, 0.8)
        high = max(open_, close) + random.uniform(0, 0.6)
        low = min(open_, close) - random.uniform(0, 0.6)
        base = close
        candles.append({
            "time": (datetime.datetime.now() - datetime.timedelta(minutes=(qtd - i))).strftime("%d/%m %H:%M"),
            "open": round(open_, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2)
        })
    return candles

# Rota principal
@app.get("/")
def home():
    return {"mensagem": "🚀 GraphSense IA Demo ativa! Vá até /visualizar para ver o painel."}

# Rota para retornar candles
@app.get("/grafico")
def grafico():
    data = gerar_candles()
    tendencia = "alta" if data[-1]["close"] > data[-5]["close"] else "baixa"
    confianca = random.randint(85, 98)
    lucro = round(random.uniform(-3, 3), 2)
    saldo = round(10000 + lucro, 2)
    return {
        "candles": data,
        "tendencia": tendencia,
        "confianca": confianca,
        "saldo": saldo,
        "lucro": lucro
    }

# Interface HTML simples (será substituída pelo index.html)
@app.get("/visualizar", response_class=HTMLResponse)
def visualizar():
    html_content = """
    <html>
    <head>
        <title>GraphSense IA Demo</title>
        <meta charset="utf-8">
        <style>
            body { background: #0f0f0f; color: white; font-family: Arial; text-align: center; }
            .container { margin-top: 50px; }
            .btn { background: #4CAF50; padding: 10px 20px; color: white; border: none; border-radius: 5px; cursor: pointer; }
            canvas { margin-top: 30px; background: #1b1b1b; border-radius: 8px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 GraphSense IA Demo</h1>
            <p>Simulação de gráfico + IA 95% de precisão</p>
            <button class="btn" onclick="atualizar()">Atualizar dados</button>
            <canvas id="grafico" width="600" height="300"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script>
            async function atualizar() {
                const res = await fetch('/grafico');
                const dados = await res.json();
                const ctx = document.getElementById('grafico').getContext('2d');
                const labels = dados.candles.map(c => c.time);
                const values = dados.candles.map(c => c.close);
                new Chart(ctx, {
                    type: 'line',
                    data: { labels, datasets: [{ label: 'Preço', data: values, borderColor: '#4CAF50', borderWidth: 2 }] },
                    options: { scales: { y: { beginAtZero: false } } }
                });
            }
            atualizar();
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# Rodar localmente (Render ignora isso, mas ajuda se testar no PC)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
