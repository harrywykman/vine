from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.status import HTTP_303_SEE_OTHER
import fastapi_chameleon

from dependencies import get_session
from data.vineyard import Vineyard
from viewmodels.vineyards.list_viewmodel import ListViewModel
from viewmodels.vineyards.details_viewmodel import DetailsViewModel

router = APIRouter()
templates = Jinja2Templates(directory="templates")


# HTML routes


@router.get("/", response_class=HTMLResponse)
@fastapi_chameleon.template('vineyard/index.pt')
def vineyard_index(request: Request):
    vm = ListViewModel(request)
    return vm.to_dict()


@router.get("/vineyards/{vineyard_id}", response_class=HTMLResponse)
@fastapi_chameleon.template('vineyard/vineyard_details.pt')
def vineyard_details(
    request: Request, vineyard_id: int, session: Session = Depends(get_session)
):
    vm = DetailsViewModel(vineyard_id, request)
    print("DETAILS VIEW")

    return vm.to_dict()


@router.get("/vineyards", response_class=HTMLResponse)
def vineyard_index(request: Request, session: Session = Depends(get_session)):
    vineyards = session.query(Vineyard).all()
    return templates.TemplateResponse(
        "vineyards.html",
        {
            "request": request,
            "vineyard": None,
            "vineyards": vineyards,
        },
    )


""" @router.get("/vineyards/{vineyard_id}", response_class=HTMLResponse)
def vineyard_form(
    request: Request, vineyard_id: int, session: Session = Depends(get_session)
):
    vineyard = session.query(Vineyard).get(vineyard_id)
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")

    vineyards = session.query(Vineyard).all()
    return templates.TemplateResponse(
        "vineyard.html",
        {
            "request": request,
            "vineyard": vineyard,
            "vineyards": vineyards,
        },
    ) """


@router.post("/vineyards")
def create_vineyard_html(
    name: str = Form(...),
    address: str = Form(""),
    session: Session = Depends(get_session),
):
    vineyard = Vineyard(name=name, address=address)
    session.add(vineyard)
    session.commit()
    return RedirectResponse(url="/vineyards", status_code=HTTP_303_SEE_OTHER)


@router.post("/vineyards/{vineyard_id}")
def update_vineyard_html(
    vineyard_id: int,
    name: str = Form(...),
    address: str = Form(""),
    session: Session = Depends(get_session),
):
    vineyard = session.query(Vineyard).get(vineyard_id)
    if not vineyard:
        raise HTTPException(status_code=404, detail="Vineyard not found")
    vineyard.name = name
    vineyard.address = address
    session.commit()
    return RedirectResponse(url="/vineyards", status_code=HTTP_303_SEE_OTHER)


@router.post("/vineyards/{vineyard_id}/delete")
def delete_vineyard_html(
    
    vineyard_id: int,
    session: Session = Depends(get_session),
):
    vineyard = session.query(Vineyard).get(vineyard_id)
    if vineyard:
        print(f"About to delete vineyard {vineyard_id}.")
        session.delete(vineyard)
        session.commit()
        print(f"Delete vineyard {vineyard_id}.")
    return RedirectResponse(url="/vineyards", status_code=HTTP_303_SEE_OTHER)
