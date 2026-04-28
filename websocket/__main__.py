from socketio_server import SocketIOServer
from config import Config
from namespaces import ExampleGmailPushNotificationNamespace, ExampleRedisEventBroadcasterNamespace 


if __name__ == "__main__":
    
    server = None
    
    try:
        
        server = SocketIOServer(
            host = Config.websocket.host,
            port = Config.websocket.port,
            namespaces = [
                ExampleGmailPushNotificationNamespace("/example_gui/gmail_push_notification"),
                ExampleRedisEventBroadcasterNamespace("/example_gui/redis_event_broadcaster")
            ]
        )
        
        server.run()
        
    except Exception as e:
        
        if server is not None:
            server.log.exception("Unhandled exception: %s", str(e))