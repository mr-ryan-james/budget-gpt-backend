from fastapi import FastAPI
from routes import router
from database import *
import uvicorn


app = FastAPI()
app.include_router(router)


@app.on_event("startup")
def startup_db_client():
    app.db = Database()


@app.on_event("shutdown")
def shutdown_db_client():
    app.db.close()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
