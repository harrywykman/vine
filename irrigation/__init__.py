from fastapi import FastAPI

from irrigation.router import router


def include_irrigation(app: FastAPI) -> None:
    """
    Register the irrigation module with the FastAPI app.
    Call this from main.py:

        from irrigation import include_irrigation
        include_irrigation(app)

    To disable the module, comment out that single line.
    The irrigation tables will remain in the database but be inert.
    """
    app.include_router(router)
    app.state.modules["irrigation"] = True
