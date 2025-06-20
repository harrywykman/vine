from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from sqlmodel import SQLModel

import os
from pathlib import Path
import fastapi_chameleon

from database import engine
from data.admin import (
    ManagementUnitAdmin,
    VarietyAdmin,
    VineyardAdmin,
    WineColourAdmin,
    StatusAdmin,
)
from routers import vineyards

# Initialise Fast API app
app = FastAPI()

admin = Admin(app, engine)

# Chameleon templates

dev_mode = True

BASE_DIR = Path(__file__).resolve().parent
template_folder = str(BASE_DIR / 'templates')
fastapi_chameleon.global_init(template_folder, auto_reload=dev_mode)

# routers

app.include_router(vineyards.router)

# create db
SQLModel.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

admin.add_view(VineyardAdmin)
admin.add_view(ManagementUnitAdmin)
admin.add_view(VarietyAdmin)
admin.add_view(WineColourAdmin)
admin.add_view(StatusAdmin)
