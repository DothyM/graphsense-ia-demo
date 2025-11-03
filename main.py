from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import random

# Inicializa o app
app = FastAPI()

# Caminho dos templates HTML
templates = Jinja2Templates(directory="modelos")

# Rota principal para verificar status
@app.get("/", response_class=JSONResponse)
async def root():
    return {"mensagem": "🚀 GraphSense IA Demo ativa! Vá até /visualizar para ver o painel."}

# Rota para gerar dados simulados (pode ser expandida depois)
@app.get("/grafico", response_class=JSONResponse)
async def grafico():
    dados = [{"x": i, "y": round(random.uniform(90, 110), 2)} for i in range(30)]
    return {"dados": dados}

# Rota para exibir a interface
@app.get("/visualizar", response_class=HTMLResponse)
async def visualizar(request: Request):
    return templates.TemplateResponse("visualizar.html", {"request": request})
