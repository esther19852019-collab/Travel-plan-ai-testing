from fastapi import FastAPI

app = FastAPI(title="Travel Plan API")


@app.get("/")
def root():
    return {"message": "Travel Plan API is running"}