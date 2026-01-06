from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from analyzer import ManadoAnalyzer

app = FastAPI()
templates = Jinja2Templates(directory="templates")
analyzer = ManadoAnalyzer()

# Halaman awal animatif
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Halaman analyzer
@app.get("/analyze", response_class=HTMLResponse)
def analyze_page(request: Request):
    return templates.TemplateResponse("analyzer.html", {"request": request})

# Proses analisis kalimat
@app.post("/analyze", response_class=HTMLResponse)
async def analyze(request: Request):
    form = await request.form()
    kalimat = form.get("kalimat")
    result = analyzer.analyze(kalimat)
    return templates.TemplateResponse(
        "analyzer.html",
        {"request": request, "result": result, "kalimat": kalimat}
    )
