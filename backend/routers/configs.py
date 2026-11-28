"""Router for health check and NEMO configuration profile endpoints."""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field

from backend import __version__
from backend.services.config_store import (
    DEFAULT_NEMO_ENVIRONMENT,
    DEFAULT_NEMO_URL,
    ConfigNotFoundError,
    build_nemo_config_content,
    config_profile_name,
    read_nemo_config_settings,
    update_nemo_config_content,
)

router = APIRouter(tags=["configs"])


class ConfigWriteRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=120)
    ini_content: str = Field(alias="iniContent", min_length=1)
    source_file: Optional[str] = Field(default="", alias="sourceFile")


class ConfigUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    ini_content: Optional[str] = Field(default=None, alias="iniContent", min_length=1)
    source_file: Optional[str] = Field(default=None, alias="sourceFile")


class ConfigCredentialsRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(default=None, min_length=1, max_length=120)
    tenant: str = Field(min_length=1, max_length=120, pattern=r"^[^\r\n]+$")
    userid: str = Field(min_length=1, max_length=240, pattern=r"^[^\r\n]+$")
    password: str = Field(min_length=1, max_length=1024, pattern=r"^[^\r\n]+$")
    nemo_url: str = Field(
        default=DEFAULT_NEMO_URL,
        alias="nemoUrl",
        min_length=1,
        max_length=500,
        pattern=r"^https?://[^\s]+$",
    )
    environment: str = Field(
        default=DEFAULT_NEMO_ENVIRONMENT,
        min_length=1,
        max_length=120,
        pattern=r"^[A-Za-z0-9._-]+$",
    )


class ConfigConnectionUpdateRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = Field(min_length=1, max_length=120)
    tenant: str = Field(min_length=1, max_length=120, pattern=r"^[^\r\n]+$")
    userid: str = Field(min_length=1, max_length=240, pattern=r"^[^\r\n]+$")
    password: str = Field(default="", max_length=1024, pattern=r"^[^\r\n]*$")
    nemo_url: str = Field(
        alias="nemoUrl",
        min_length=1,
        max_length=500,
        pattern=r"^https?://[^\s]+$",
    )
    environment: str = Field(min_length=1, max_length=120, pattern=r"^[A-Za-z0-9._-]+$")


@router.get("/api/health")
def health() -> dict:
    return {"status": "ok", "version": __version__}


@router.get("/api/configs")
def list_configs() -> dict:
    from backend import main as m

    store = m._store()
    profiles = store.list_profiles()
    return {
        "configs": [profile.to_dict() for profile in profiles],
        "defaultConfigId": store.default_profile(profiles).id if profiles else None,
    }


@router.post("/api/configs", status_code=201)
def create_config(request: "ConfigWriteRequest") -> dict:
    from backend import main as m

    profile = m._store().create_config(
        name=request.name,
        ini_content=request.ini_content,
        source_file=request.source_file or "",
    )
    return {"config": profile.to_dict()}


@router.post("/api/configs/from-credentials", status_code=201)
def create_config_from_credentials(request: "ConfigCredentialsRequest") -> dict:
    from backend import main as m

    try:
        name = request.name.strip() if request.name else config_profile_name(request.tenant)
        ini_content = build_nemo_config_content(
            request.tenant,
            request.userid,
            request.password,
            nemo_url=request.nemo_url,
            environment=request.environment,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    store = m._store()
    if any(profile.name.casefold() == name.casefold() for profile in store.list_profiles()):
        raise HTTPException(status_code=409, detail=f"Die Konfiguration '{name}' ist bereits vorhanden.")
    profile = store.create_config(name=name, ini_content=ini_content)
    m.log.info("Config-Profil über Oberfläche angelegt: id=%s name=%s tenant=%s", profile.id, profile.name, profile.tenant)
    return {"config": profile.to_dict()}


@router.get("/api/configs/{config_id}/connection")
def get_config_connection(config_id: str) -> dict:
    from backend import main as m

    try:
        store = m._store()
        profile = store.get_profile(config_id)
        settings = read_nemo_config_settings(store.decrypt_config(config_id))
    except ConfigNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"config": {"id": profile.id, "name": profile.name, **settings}}


@router.put("/api/configs/{config_id}/connection")
def update_config_connection(config_id: str, request: "ConfigConnectionUpdateRequest") -> dict:
    from backend import main as m

    store = m._store()
    try:
        profile = store.get_profile(config_id)
        duplicate = next(
            (
                item
                for item in store.list_profiles()
                if item.id != config_id and item.name.casefold() == request.name.strip().casefold()
            ),
            None,
        )
        if duplicate:
            raise HTTPException(status_code=409, detail=f"Die Konfiguration '{request.name.strip()}' ist bereits vorhanden.")
        ini_content = update_nemo_config_content(
            store.decrypt_config(config_id),
            tenant=request.tenant,
            userid=request.userid,
            password=request.password,
            nemo_url=request.nemo_url,
            environment=request.environment,
        )
        updated = store.update_config(config_id, name=request.name, ini_content=ini_content)
    except ConfigNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    m.log.info(
        "Config-Profil über Oberfläche geändert: id=%s name=%s tenant=%s environment=%s",
        updated.id,
        updated.name,
        updated.tenant,
        request.environment,
    )
    return {"config": updated.to_dict(), "passwordChanged": bool(request.password), "previousName": profile.name}


@router.put("/api/configs/{config_id}")
def update_config(config_id: str, request: "ConfigUpdateRequest") -> dict:
    from backend import main as m

    try:
        profile = m._store().update_config(
            config_id=config_id,
            name=request.name,
            ini_content=request.ini_content,
            source_file=request.source_file,
        )
    except ConfigNotFoundError as exc:
        raise m._http_not_found(exc) from exc
    return {"config": profile.to_dict()}


@router.delete("/api/configs/{config_id}", status_code=204)
def delete_config(config_id: str) -> None:
    from backend import main as m

    try:
        m._store().delete_config(config_id)
    except ConfigNotFoundError as exc:
        raise m._http_not_found(exc) from exc


@router.post("/api/configs/import-local")
def import_local_configs(overwrite: bool = Query(default=False)) -> dict:
    from backend import main as m

    profiles = m._store().import_ini_files(overwrite=overwrite)
    return {
        "count": len(profiles),
        "configs": [profile.to_dict() for profile in profiles],
    }
