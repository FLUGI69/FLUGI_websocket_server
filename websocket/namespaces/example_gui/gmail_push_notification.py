import logging

from ..abstract_namespace import AbstractNamespace
from utils.dc.websocket.auto_message import AutoMessage
from utils.dc.websocket.websocket_request import WebsocketRequest
from utils.dc.websocket.websocket_response import WebsocketResponse

class ExampleGmailPushNotificationNamespace(AbstractNamespace):
    
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
                    message = "%s has successfully connected to the server | Namespace: '%s'" % (
                        self.current_client.name, 
                        self.namespace
                    )
                )
            )
            
            self.log.info("%s has successfully connected to the server | Namespace: '%s'" % (
                self.current_client.name, 
                self.namespace)
            )
            
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
            
    # TODO: Implement Gmail push notification handling logic here       
                
    async def disconnected(self, sid: str, reason: str) -> WebsocketResponse:
        
        if self.current_client is not None:
            
            self.current_client.authenticated = False
            
            response = WebsocketResponse(
                success = True,
                error = None,
                data = AutoMessage(
                    message = "%s has successfully disconnected from the server | Namespace: '%s'" % (
                        self.current_client.name, 
                        self.namespace
                    )
                )
            )
            
            self.log.info("%s has successfully disconnected from the server | Namespace: '%s'" % (
                self.current_client.name, 
                self.namespace
            ))
            
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