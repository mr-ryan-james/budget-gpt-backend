from llm import chain
from fastapi import FastAPI
from routes import router


app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def startup_db_client():
    pass


@app.on_event("shutdown")
def shutdown_db_client():
    pass
