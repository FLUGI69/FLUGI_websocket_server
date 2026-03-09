import socketio
import logging
from abc import ABC, abstractmethod
from urllib.parse import parse_qs
import typing as t

from utils.dc.websocket.environ import Environ
from utils.dc.websocket.client import WebsocketClient  
from utils.dc.websocket.websocket_response import WebsocketResponse
from utils.dc.websocket.websocket_request import WebsocketRequest
from utils.dc.websocket.websocket_request_response import WebsocketRequestResponse
from utils.logger import LoggerMixin
from config import Config

class AbstractNamespace(socketio.AsyncNamespace, ABC, LoggerMixin):
    
    log: logging.Logger
    
    _ALLOWED_NAMESPACES: t.ClassVar[t.List[str]] = []

    __clients: dict[str, WebsocketClient] = {}
    
    __environs: dict[str, Environ] = {}
    
    __current_sid: str | None = None
    
    def __init__(self, namespace):
        
        super().__init__(namespace)
        
    @property
    def current_client(self) -> WebsocketClient:
        
        if self.__current_sid is None:
            
            raise RuntimeError("No current sid set for property")
        
        if self.__current_sid not in self.__clients:
            
            raise RuntimeError("WebsocketClient for sid '%s' not initialized yet" % self.__current_sid)
        
        return self.__clients[self.__current_sid]

    @property
    def environ(self) -> Environ:
        
        if self.__current_sid is None:
            
            raise RuntimeError("No current sid set for property")
        
        if self.__current_sid not in self.__environs:
            
            raise RuntimeError("Environ for sid '%s' not initialized yet" % self.__current_sid)
        
        return self.__environs[self.__current_sid]

    @property
    def allowed_namespaces(self) -> tuple[str, ...]:

        return tuple(self._ALLOWED_NAMESPACES)
    
    @classmethod
    def _register_namespace(cls, namespace: str):

        if namespace not in cls._ALLOWED_NAMESPACES:
            
            cls._ALLOWED_NAMESPACES.append(namespace)
            
    def set_current_sid(self, sid: str):
        
        self.__current_sid = sid
     
    async def on_connect(self, sid: str, environ: dict, auth: dict):

        self.set_current_sid(sid)

        if self.namespace not in self.allowed_namespaces:
            
            self.log.warning("Attempt to connect to forbidden namespace: %s" % self.namespace)
      
            response = WebsocketResponse(
                success = False,
                error = f"Namespace '{self.namespace}' not allowed",
                data = None
            )
            
            await self.emit("websocket_response", response.model_dump(), room = sid)
            
            raise PermissionError("Namespace '%s' not allowed" % self.namespace)
        
        try:
            
            if isinstance(auth, dict):
                
                request = WebsocketRequest.model_validate(auth)
                
            else:
                
                request = auth
                
            self.__clients[sid] = request.data
            
            if self.current_client is not None:
                    
                scope = environ.get("asgi.scope")
                
                if scope is None:
                    
                    raise ValueError("Missing ASGI scope in environ")

                raw_querystr_bytes = scope.get("query_string")
                
                if raw_querystr_bytes is None:
                    
                    raw_querystr = ""
                    
                else:
                    
                    raw_querystr = raw_querystr_bytes.decode()

                query_params: t.Dict[str, str] = {}
                
                parsed_qs = parse_qs(raw_querystr)
                
                for key, values in parsed_qs.items():
                    
                    if values != []:
                        
                        query_params[key] = values[0]

                headers: t.List[t.Tuple[bytes, bytes]] = []
                
                raw_headers = scope.get("headers")
                
                if raw_headers is not None:
                    
                    headers = list(raw_headers)
                    
                client_ip: t.Optional[str] = None
                
                client_port: t.Optional[int] = None
                
                client = scope.get("client")
                
                if client and isinstance(client, (list, tuple)) and len(client) == 2:
                    
                    client_ip, client_port = client

                server_ip: t.Optional[str] = None
                
                server_port: t.Optional[int] = None
                
                server = scope.get("server")
                
                if server and isinstance(server, (list, tuple)) and len(server) == 2:
                    
                    server_ip, server_port = server

                self.__environs[sid] = Environ(
                    path = scope.get("path", ""),
                    query_string = raw_querystr,
                    query_params = query_params,
                    headers = headers,
                    client_ip = client_ip,
                    client_port = client_port,
                    server_ip = server_ip,
                    server_port = server_port,
                )
                
                if self.current_client.auth_token != Config.websocket.auth_token:
                    
                    self.log.warning("Auth token mismatch for client: %s" % self.current_client.name)

                    response = WebsocketResponse(
                        success = False,
                        error = "Invalid auth token",
                        data = self.current_client.name
                    )
                    
                    await self.emit("websocket_response", response.model_dump(), room = sid)

                    raise PermissionError(response.error)

                return await self.connected(sid)
            
        except Exception as e:
            
            self.log.exception("Unexpected error occurred during connection: %s" % str(e))
             
            response = WebsocketResponse(
                success = False, 
                error = str(e), 
                data = None
            )
            
            await self.emit("websocket_response", response.model_dump(), room = sid)
            
            raise
    
    async def on_disconnect(self, sid: str, *args, **kwargs):
        
        self.set_current_sid(sid)
        
        try:
            
            response = await self.disconnected(sid, *args, **kwargs)
        
            self.__clients.pop(self.__current_sid, None)
            self.__environs.pop(self.__current_sid, None)
            
            return response
        
        except Exception as e:
            
            self.log.exception("Unexpected error occurred during disconnection: %s" % str(e))
    
            response = WebsocketResponse(
                success = False,
                error = str(e),
                data = None
            )
            
            await self.emit("websocket_response", response.model_dump(), room = sid)
            
            raise

    async def broadcast_event(self, event: str, response: WebsocketResponse, sender_sid: str, namespace: str):

        for sid, client in self.__clients.items():
            
            try:
                
                if sid != sender_sid and client.authenticated == True:

                    self.log.debug("Broadcasting event '%s' to client '%s' in namespace '%s'" % (
                        event, 
                        client.name, 
                        namespace
                        )
                    )
                    
                    await self.emit(event, response.model_dump(), room = sid, namespace = namespace)

                elif sid == sender_sid and client.authenticated == True:
                    
                    self.log.debug("Sending request response back to sender client '%s' in namespace '%s'" % (
                        client.name,
                        namespace
                        )
                    )
                    
                    request_response = WebsocketRequestResponse(
                        success = response.success,
                        error = response.error,
                        event = response.data.__class__.__name__ if response.data else None,                    
                    )
                    
                    await self.emit(
                        "websocket_response_ack", 
                        request_response.model_dump(), 
                        room = sid, 
                        namespace = namespace
                    )
                    
            except Exception as e:
                
                self.log.error("Failed to emit event '%s' to client '%s': %s" % (
                    event, 
                    client.name, 
                    str(e)
                    )
                )
                
    @abstractmethod
    async def connected(self, sid: str) -> WebsocketResponse:
        pass
    
    @abstractmethod
    async def disconnected(self, sid: str, reason: str)-> WebsocketResponse:
        pass