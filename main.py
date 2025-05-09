from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from openai import AsyncOpenAI
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.post("/generate", response_class=HTMLResponse)
async def generate(request: Request, idea: str = Form(...)):
    prompt = f"Сгенерируй подробный бизнес-план на основе идеи: {idea}"
    try:
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Ты бизнес-аналитик."},
                {"role": "user", "content": prompt}
            ]
        )
        result = response.choices[0].message.content
        html_template = f'''
        <html>
        <head><link rel="stylesheet" href="/static/style.css"></head>
        <body>
        <div class='container'>
            <h1>Ваш бизнес-план</h1>
            <div class='result-box'>{result}</div>
            <a href='/' class='back-link'>&larr; Назад</a>
        </div>
        </body></html>
        '''
        return HTMLResponse(html_template)
    except Exception as e:
        return HTMLResponse(f"<p>Ошибка: {str(e)}</p>")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
