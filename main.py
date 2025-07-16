from pathlib import Path

import fastapi_chameleon
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin
from sqlmodel import Session, SQLModel

from config import SETTINGS
from data.admin import (
    ChemicalAdmin,
    ChemicalGroupAdmin,
    GrowthStageAdmin,
    ManagementUnitAdmin,
    SprayAdmin,
    SprayChemicalAdmin,
    SprayRecordAdmin,
    SprayRecordChemicalAdmin,
    StatusAdmin,
    UserAdmin,
    VarietyAdmin,
    VineyardAdmin,
    WineColourAdmin,
)
from database import engine
from routers import (
    account,
    administration,
    chemicals,
    spray_programs,
    sprays,
    vineyards,
)
from services import user_service

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
app.include_router(sprays.router)
app.include_router(account.router)
app.include_router(administration.router)

# create db
SQLModel.metadata.create_all(engine)

# create superuser if no users exist
with Session(engine) as session:
    user_service.create_first_superadmin(
        session,
        SETTINGS.super_admin_name,
        SETTINGS.super_admin_email,
        SETTINGS.super_admin_password,
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

admin.add_view(UserAdmin)
admin.add_view(VineyardAdmin)
admin.add_view(ManagementUnitAdmin)
admin.add_view(VarietyAdmin)
admin.add_view(WineColourAdmin)
admin.add_view(StatusAdmin)
admin.add_view(SprayAdmin)
admin.add_view(SprayRecordAdmin)
admin.add_view(ChemicalAdmin)
admin.add_view(GrowthStageAdmin)
admin.add_view(ChemicalGroupAdmin)
admin.add_view(SprayChemicalAdmin)
admin.add_view(SprayRecordChemicalAdmin)
