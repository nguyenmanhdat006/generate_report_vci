from fastapi import FastAPI

from app.api.reports import router as report_router

app = FastAPI(title="generate-pdf-service")

app.include_router(report_router)


