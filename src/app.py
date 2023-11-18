from fastapi import FastAPI

from depends import data_manager
from distribution.worker import DistributionsWorker
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
    DistributionsWorker(data_manager).start()


@app.on_event("shutdown")
async def shutdown_event():
    ...
