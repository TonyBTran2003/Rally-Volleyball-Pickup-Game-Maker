from fastapi import FastAPI


app = FastAPI(
    title="Rally API",
    description="API for organizing and finding volleyball games",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "message": "Welcome to Rally"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }