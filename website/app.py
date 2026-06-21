from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="website/static"), name="static")

templates = Jinja2Templates(directory="website/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})
