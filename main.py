from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()

# --- Configuração de templates ---
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

modelos = Jinja2Templates(directory="modelos")

@app.get("/visualizar", response_class=HTMLResponse)
async def visualizar(request: Request):
    return modelos.TemplateResponse("visualizar.html", {"request": request})



# --- Rota inicial ---
@app.get("/", response_class=HTMLResponse)
async def root():
    return {"mensagem": "🚀 GraphSense IA Demo ativa! Vá até /visualizar para ver o painel."}

# --- Rota para exibir o painel profissional ---
@app.get("/visualizar", response_class=HTMLResponse)
async def visualizar(request: Request):
    return templates.TemplateResponse("visualizar.html", {"request": request})

# --- Rodar localmente (Render ignora isso, mas útil pra testes locais) ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
