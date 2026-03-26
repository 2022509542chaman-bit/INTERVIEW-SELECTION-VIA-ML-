from fastapi import FastAPI

app = FastAPI()

@app.get("/api/test")
def test():
    return {"msg": "ok"}

