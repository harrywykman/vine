import fastapi_chameleon
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from dependencies import get_session
from viewmodels.spray_programs.list_viewmodel import ListViewModel

router = APIRouter()

# HTML routes


## GET List Spray Programs
@router.get("/spray_programs", response_class=HTMLResponse)
@fastapi_chameleon.template("spray_programs/index.pt")
def spray_program_index(request: Request, session: Session = Depends(get_session)):
    vm = ListViewModel(request, session)
    if not vm:
        raise HTTPException(status_code=404, detail="No view model.")
    return vm.to_dict()
