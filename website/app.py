from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="website/static"), name="static")

templates = Jinja2Templates(directory="website/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/trend/reports")
def trend_reports(request: Request):
    # Mock data
    mock_reports = [
        {"id": 1, "title": "Trend Report 1", "date": "2023-01-01"},
        {"id": 2, "title": "Trend Report 2", "date": "2023-01-02"},
    ]
    return templates.TemplateResponse("trend_reports.html", {
        "request": request,
        "reports": mock_reports
    })


@app.get("/friction/reports")
def friction_reports(request: Request):
    # Mock data
    mock_reports = [
        {"id": 1, "title": "Friction Report 1", "date": "2023-01-01"},
        {"id": 2, "title": "Friction Report 2", "date": "2023-01-02"},
    ]
    return templates.TemplateResponse("friction_reports.html", {
        "request": request,
        "reports": mock_reports
    })


@app.get("/report/{id}")
def report_detail(request: Request, id: int):
    # Mock data
    mock_report = {
        "id": id,
        "title": f"Report {id}",
        "content": "This is the content of report number " + str(id),
        "date": "2023-01-01"
    }
    return templates.TemplateResponse("report_detail.html", {
        "request": request,
        "report": mock_report
    })


@app.get("/evidence/{id}")
def evidence_detail(request: Request, id: int):
    # Mock data
    mock_evidence = {
        "id": id,
        "title": f"Evidence {id}",
        "content": "This is the content of evidence number " + str(id),
        "date": "2023-01-01"
    }
    return templates.TemplateResponse("evidence_detail.html", {
        "request": request,
        "evidence": mock_evidence
    })


@app.get("/source/{id}")
def source_detail(request: Request, id: int):
    # Mock data
    mock_source = {
        "id": id,
        "name": f"Source {id}",
        "url": "https://example.com",
        "type": "Web Source"
    }
    return templates.TemplateResponse("source_detail.html", {
        "request": request,
        "source": mock_source
    })


@app.get("/operator")
def operator_dashboard(request: Request):
    # Mock data
    mock_data = {
        "users": 100,
        "reports_generated": 50,
        "evidence_count": 200
    }
    return templates.TemplateResponse("operator_dashboard.html", {
        "request": request,
        "data": mock_data
    })
