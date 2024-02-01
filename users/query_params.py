from pydantic import BaseModel, conint


class UsersListQueryParams(BaseModel):
    page: conint(gt=0, lt=100) = 1
    limit: conint(gt=0, lt=100) = 10
    filter_by_name: str | None = None
    sort_by: str = "username"
    order_by: str = "asc"
