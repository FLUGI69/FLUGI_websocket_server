import logging

from ..abstract_namespace import AbstractNamespace
from utils.dc.websocket.auto_message import AutoMessage
from utils.dc.websocket.websocket_request import WebsocketRequest
from utils.dc.websocket.websocket_response import WebsocketResponse

class ExampleGuiNamespace(AbstractNamespace):
    
    log: logging.Logger
    
    def __init__(self, namespace: str):
        
        super().__init__(namespace)
 
    async def connected(self, sid: str) -> WebsocketResponse:
        
        if self.current_client is not None:
            
            self.current_client.authenticated = True
    
            response = WebsocketResponse(
                success = True,
                error = None,
                data = AutoMessage(
                    message = "%s has successfully connected to the server" % self.current_client.name
                    )
                )
            
            self.log.info("%s has successfully connected to the server" % self.current_client.name)
            
            self.log.debug("%s -> Session details | session id: %s - path: %s - ip: %s - query_string: %s" % (
                self.current_client.name,
                sid,
                self.environ.path,
                self.environ.client_ip,
                self.environ.query_params
                )
            )
            
            await self.emit(
                "websocket_response", 
                response.model_dump(), 
                room = sid, 
                namespace = self.namespace
            )
            
    async def on_redis_refresh(self, sid: str, data: dict):
  
        if self.current_client.authenticated:

            if isinstance(data, dict):
    
                request = WebsocketRequest.model_validate(data)
                
                self.log.debug("Received refresh request from client '%s' in namespace '%s': %s" % (
                    self.current_client.name,
                    self.namespace,
                    str(request)
                    )
                )
                
                await self.broadcast_event(
                    "websocket_response", 
                    WebsocketResponse(
                        success = request.success,
                        error = request.error,
                        data = request.data
                    ), 
                    sender_sid = sid, 
                    namespace = self.namespace
                )
                
    async def on_reminder_action(self, sid: str, data: dict):
        
        if self.current_client.authenticated:

            if isinstance(data, dict):
    
                request = WebsocketRequest.model_validate(data)
                
                self.log.debug("Received reminder action request from client '%s' in namespace '%s': %s" % (
                    self.current_client.name,
                    self.namespace,
                    str(request)
                    )
                )
                
                await self.broadcast_event(
                    "websocket_response", 
                    WebsocketResponse(
                        success = request.success,
                        error = request.error,
                        data = request.data
                    ), 
                    sender_sid = sid, 
                    namespace = self.namespace
                )
        
    async def disconnected(self, sid: str, reason: str) -> WebsocketResponse:
        
        if self.current_client is not None:
            
            self.current_client.authenticated = False
            
            response = WebsocketResponse(
                success = True,
                error = None,
                data = AutoMessage(
                    message = "%s has successfully disconnected from the server" % self.current_client.name
                )
            )
            
            self.log.info("%s has successfully disconnected from the server" % self.current_client.name)
            
            self.log.debug("%s -> Session details | session id: %s - path: %s - ip: %s - query_string: %s" % (
                self.current_client.name,
                sid,
                self.environ.path,
                self.environ.client_ip,
                self.environ.query_params
                )
            )
       
            await self.emit(
                "websocket_response", 
                response.model_dump(), 
                room = sid, 
                namespace = self.namespace
            )