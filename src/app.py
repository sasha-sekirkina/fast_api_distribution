from fastapi import FastAPI

from db.manager import data_manager
from routing.client import router as client_router
from routing.distribution import router as distribution_router
from routing.stat import router as stat_router

app = FastAPI(
    title="Distribution Manager",
    openapi_url="/core/openapi.json",
    docs_url="/core/docs"
)

app.include_router(client_router)
app.include_router(distribution_router)
app.include_router(stat_router)


@app.on_event("startup")
async def startup_event():
    # todo add loading existing distributions and add task to celery with eta argument
    existing_distributions = data_manager.distributions.get_all()
    ...


@app.on_event("shutdown")
async def shutdown_event():
    ...
