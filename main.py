"""API for managing a SQLite-backed server inventory."""

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

app = FastAPI(title="Server Inventory API")
templates = Jinja2Templates(directory="templates")
engine = create_engine(
    "sqlite:///./inventory.db",
    connect_args={"check_same_thread": False},
)


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


class Server(Base):
    """SQLAlchemy model for a server in the inventory."""
    __tablename__ = "servers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    ip_address: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()


class ServerCreate(BaseModel):
    """Pydantic model for creating a new server."""
    name: str
    ip_address: str
    status: str


class ServerResponse(ServerCreate):
    """Pydantic model for server response, including the server ID."""
    id: int

    model_config = {"from_attributes": True}


Base.metadata.create_all(engine)

# Can seed the database with initial/permanent server data if needed
def seed_servers() -> None:
    """Seed the database with initial server data if it's empty."""
    with Session(engine) as session:
        if session.scalar(select(Server.id).limit(1)) is not None:
            return

        session.add_all(
            (
                Server(
                    name="web-01",
                    ip_address="192.168.1.10",
                    status="online",
                ),
                Server(
                    name="web-02",
                    ip_address="192.168.1.11",
                    status="online",
                ),
                Server(
                    name="database-01",
                    ip_address="192.168.1.20",
                    status="online",
                ),
                Server(
                    name="cache-01",
                    ip_address="192.168.1.30",
                    status="maintenance",
                ),
                Server(
                    name="backup-01",
                    ip_address="192.168.1.40",
                    status="offline",
                ),
            )
        )
        session.commit()


seed_servers()


@app.get("/")
@app.get("/servers")
def list_servers(request: Request):
    """List all servers in the inventory."""
    with Session(engine) as session:
        servers = session.scalars(select(Server).order_by(Server.id)).all()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"servers": servers},
    )


@app.post(
    "/servers",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_server(server: ServerCreate) -> Server:
    """Add a new server to the inventory."""
    with Session(engine) as session:
        db_server = Server(**server.model_dump())
        session.add(db_server)
        session.commit()
        session.refresh(db_server)
        return db_server


@app.post("/add")
def add_server_from_form(
    name: str = Form(...),
    ip_address: str = Form(...),
    server_status: str = Form(..., alias="status"),
) -> RedirectResponse:
    """Add a new server to the inventory from form data."""
    add_server(
        ServerCreate(
            name=name,
            ip_address=ip_address,
            status=server_status,
        )
    )
    return RedirectResponse(url="/servers", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/delete/{server_id}")
def delete_server(server_id: int) -> RedirectResponse:
    """Delete a server from the inventory."""
    with Session(engine) as session:
        server = session.get(Server, server_id)
        if server is not None:
            session.delete(server)
        session.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/edit/{server_id}")
def edit_server(request: Request, server_id: int):
    """Render the edit server form."""
    with Session(engine) as session:
        server = session.get(Server, server_id)

    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")

    return templates.TemplateResponse(
        request=request,
        name="edit.html",
        context={"server": server},
    )


@app.post("/edit/{server_id}")
def update_server(
    server_id: int,
    name: str = Form(...),
    ip_address: str = Form(...),
    server_status: str = Form(..., alias="status"),
) -> RedirectResponse:
    """Update a server's information in the inventory."""
    with Session(engine) as session:
        server = session.get(Server, server_id)
        if server is None:
            raise HTTPException(status_code=404, detail="Server not found")

        server.name = name
        server.ip_address = ip_address
        server.status = server_status
        session.commit()

    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)
