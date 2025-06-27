from pathlib import Path

import fastapi_chameleon
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from sqlmodel import SQLModel

from data.admin import (
    ChemicalAdmin,
    ChemicalGroupAdmin,
    GrowthStageAdmin,
    ManagementUnitAdmin,
    SprayProgramAdmin,
    SprayProgramChemicalAdmin,
    SprayRecordAdmin,
    StatusAdmin,
    UserAdmin,
    VarietyAdmin,
    VineyardAdmin,
    WineColourAdmin,
)
from database import engine
from routers import account, chemicals, spray_programs, vineyards

# Initialise Fast API app
app = FastAPI()

admin = Admin(app, engine)

# Chameleon templates

dev_mode = True

BASE_DIR = Path(__file__).resolve().parent
template_folder = str(BASE_DIR / "templates")
fastapi_chameleon.global_init(template_folder, auto_reload=dev_mode)

# routers

app.include_router(vineyards.router)
app.include_router(chemicals.router)
app.include_router(spray_programs.router)
app.include_router(account.router)

# create db
SQLModel.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

admin.add_view(UserAdmin)
admin.add_view(VineyardAdmin)
admin.add_view(ManagementUnitAdmin)
admin.add_view(VarietyAdmin)
admin.add_view(WineColourAdmin)
admin.add_view(StatusAdmin)
admin.add_view(SprayProgramAdmin)
admin.add_view(SprayRecordAdmin)
admin.add_view(ChemicalAdmin)
admin.add_view(GrowthStageAdmin)
admin.add_view(ChemicalGroupAdmin)
admin.add_view(SprayProgramChemicalAdmin)
