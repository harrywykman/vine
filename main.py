from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqladmin import Admin, ModelView
from sqlmodel import SQLModel

from database import database_url, engine
from models.vineyard import ManagementUnit, Vineyard
from routers import vineyards

# Initialise Fast API app
app = FastAPI()


print(database_url)

admin = Admin(app, engine)

app.include_router(vineyards.router)

# create db
SQLModel.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class VineyardAdmin(ModelView, model=Vineyard):
    column_list = [Vineyard.id, Vineyard.name, Vineyard.address]


class ManagementUnitAdmin(ModelView, model=ManagementUnit):
    column_list = [ManagementUnit.id, ManagementUnit.name]


admin.add_view(VineyardAdmin)
admin.add_view(ManagementUnitAdmin)
