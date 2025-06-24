import fastapi_chameleon
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from dependencies import get_session
from viewmodels.chemicals.list_viewmodel import ListViewModel

router = APIRouter()

# HTML routes


@router.get("/chemicals", response_class=HTMLResponse)
@fastapi_chameleon.template("chemical/index.pt")
def chemical_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    return vm.to_dict()
