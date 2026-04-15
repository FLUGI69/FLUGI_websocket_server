import uvicorn
import logging
import socketio
import socket
import requests
import multiprocessing
import typing as t

from utils import LoggerMixin
from namespaces.abstract_namespace import AbstractNamespace

class SocketIOServer(LoggerMixin):
    
    log: logging.Logger
    
    def __init__(self, 
        host: str = "0.0.0.0",
        port: int = 8000,
        namespaces: t.List[AbstractNamespace] = []
        ):
        
        self.host = host
        
        self.port = port
        
        self.socketio = socketio.AsyncServer(async_mode = 'asgi')
        
        self.app = socketio.ASGIApp(self.socketio, on_shutdown = self._shutdown)
        
        for namespace in namespaces:
             
            self.register_namespace(namespace)

    def register_namespace(self, namespace: AbstractNamespace):
        
        self.socketio.register_namespace(namespace)
        
        AbstractNamespace._register_namespace(namespace.namespace)
        
        self.log.debug("Registered namespace: %s" % namespace.namespace)
        
    async def _shutdown(self):
        
        self.log.warning("Exit")
        
        for namespace in list(self.socketio.manager.get_namespaces()):
            
            for sid, _ in list(self.socketio.manager.get_participants(namespace, None)):
                
                await self.socketio.disconnect(sid, namespace = namespace)
        
        await self.socketio.shutdown()
        
        self.log.warning("%s exit" % multiprocessing.current_process().name)

    def get_display_host(self):

        return f"{self.host}:{self.port}"
    
    def run(self):
        
        display_host = self.get_display_host()
        
        self.log.info("SocketIO server is running on %s" % display_host)
        
        uvicorn.run(self.app, host = self.host, port = self.port, log_level = logging.WARNING)