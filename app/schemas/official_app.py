from pydantic import BaseModel, ConfigDict


class OfficialAppCreate(BaseModel):
    app_name: str
    developer: str
    package_id: str | None = None
    store: str
    store_url: str | None = None
    verified: bool = False


class OfficialAppResponse(BaseModel):
    id: int
    company_id: int
    app_name: str
    developer: str
    package_id: str | None = None
    store: str
    store_url: str | None = None
    verified: bool

    model_config = ConfigDict(from_attributes=True)
    