from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from sqlmodel import SQLModel

from database import engine
from models.admin import (
    ManagementUnitAdmin,
    VarietyAdmin,
    VineyardAdmin,
    WineColourAdmin,
)
from routers import vineyards

# Initialise Fast API app
app = FastAPI()

admin = Admin(app, engine)

app.include_router(vineyards.router)

# create db
SQLModel.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

admin.add_view(VineyardAdmin)
admin.add_view(ManagementUnitAdmin)
admin.add_view(VarietyAdmin)
admin.add_view(WineColourAdmin)
