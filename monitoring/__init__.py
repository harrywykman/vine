from fastapi import FastAPI

from monitoring.router import router


def include_monitoring(app: FastAPI) -> None:
    """
    Register the monitoring module with the FastAPI app.
    Call this from main.py:

        from monitoring import include_monitoring
        include_monitoring(app)

    To disable the module, comment out that single line.
    The monitoring tables will remain in the database but be inert.
    """
    app.include_router(router)
    app.state.modules["monitoring"] = True
