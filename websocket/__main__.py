from socketio_server import SocketIOServer
from config import Config
from namespaces import ExampleGuiNamespace 
# from .namespaces import ExampleWebNamespace

if __name__ == "__main__":
    
    server = None
    
    try:
        
        server = SocketIOServer(
            host = Config.websocket.host,
            port = Config.websocket.port,
            namespaces = [
                ExampleGuiNamespace("/Example")
            ]
        )
        
        server.run()
        
    except Exception as e:
        
        if server is not None:
            server.log.exception("Unhandled exception: %s", str(e))