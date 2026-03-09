import typing as t
from dataclass import DataclassBaseModel

class Environ(DataclassBaseModel):
    path: str
    query_string: str
    query_params: t.Dict[str, str]
    headers: t.List[t.Tuple[bytes, bytes]]
    client_ip: t.Optional[str] = None
    client_port: t.Optional[int] = None
    server_ip: t.Optional[str] = None
    server_port: t.Optional[int] = None