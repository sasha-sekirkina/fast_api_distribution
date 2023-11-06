from fastapi import FastAPI

from depends import data_manager
from distribution.task import distribute
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
    data_manager.distribute_callback = distribute
    existing_distributions = data_manager.distributions.get_all()
    for dist in existing_distributions:
        if dist["status"] != "finished":
            distribute.apply_async(
                (dist,),
                eta=dist["start_date"],
                expires=dist["end_date"],
                task_id=dist["id"]
            )


@app.on_event("shutdown")
async def shutdown_event():
    ...
