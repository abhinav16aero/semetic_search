from fastapi import FastAPI, File, Form, UploadFile, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .utils import  process_data, search
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET,OPTIONS,PATCH,DELETE,POST,PUT"],
    allow_headers=["X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version"],
)
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def index():
    return templates.TemplateResponse("index.html", {"request": None})



@app.post("/api/upload")
async def upload(content: str = Form(None)):
    if not content:
        return {"status": "error"}

    process_data(content)
    return {"status": "success"}




@app.get("/api/search")
async def perform_search(query: str):
    results = search(query)
    return results

@app.get("/src/main.js", response_class=Response)
async def get_main_js():
    with open("src/main.js", "r") as file:
        js_content = file.read()
    return Response(content=js_content, media_type="application/javascript")

    

# try:
#     predict(...)
# except Exception as error:
#     print(error)