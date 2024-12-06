from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"Hello"}

@app.get("/get/{name}")
async def getName(name):
    return {"Hello":name}