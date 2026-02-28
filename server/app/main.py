from fastapi import FastAPI

app = FastAPI(title="Harmony")


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello from Harmony :P"}
