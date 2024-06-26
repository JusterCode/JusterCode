import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from yookassa import Configuration, Payment
import uuid

# Загрузка переменных окружения из файла .env
load_dotenv()

app = FastAPI()

# Настройка токена авторизации для YooKassa
Configuration.configure(
    os.getenv('YOOKASSA_SHOP_ID'),
    os.getenv('YOOKASSA_SECRET_KEY')
)

# Настройка статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

@app.post("/generate_payment_link")
async def generate_payment_link(amount: float = Form(...), description: str = Form(...)):
    try:
        payment = Payment.create({
            "amount": {
                "value": amount,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://your-return-url.com"
            },
            "capture": True,
            "description": description
        }, uuid.uuid4().hex)

        return JSONResponse({'payment_url': payment.confirmation.confirmation_url})

    except Exception as e:
        return JSONResponse({'error': str(e)}, status_code=400)
