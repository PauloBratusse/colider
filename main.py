from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,FileResponse
from colider import main

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("colider_viewer.html", {"request": request})


colider_file_path = "colider_output.txt"

@app.get("/colider_output",response_class=FileResponse)
async def root():
    return colider_file_path

@app.get("/generate_sim",response_class=FileResponse)
async def root():
    main()
    return colider_file_path