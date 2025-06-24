import fastapi_chameleon
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlmodel import select

from data.vineyard import Chemical
from dependencies import get_session
from viewmodels.spray_programs.details_viewmodel import DetailsViewModel
from viewmodels.spray_programs.list_viewmodel import ListViewModel

router = APIRouter()

# HTML routes


@router.get("/spray_programs", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/index.pt")
def spray_program_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    return vm.to_dict()


@router.get("/spray_program/chemical_row", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/_chemical_row.pt")
def get_chemical_row(session: Session = Depends(get_session)):
    print("___________________________________________________________________")
    chemicals = session.exec(select(Chemical)).all()
    if not chemicals:
        raise HTTPException(status_code=404, detail="No chemicals found")
    return {"chemicals": chemicals}


@router.get("/spray_program/new", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_program/spray_program_form.pt")
def spray_program_index(request: Request, session: Session = Depends(get_session)):
    vm = DetailsViewModel(None, request, session)

    return vm.to_dict()
