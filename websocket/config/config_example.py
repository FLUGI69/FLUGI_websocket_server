from pathlib import Path
import os, sys

class Config(object):
    
    class websocket:
        
        host = "0.0.0.0"
        port = 0000
        auth_token = ""
        excluded_models = {"", "", ""}
        folder = "gui/utils/dc/websocket"

    class dev:
    
        class db:
        
            user = ""
            password = ""
            host = "127.0.0.1"
            port = 1234
            database = ""
        
        class redis:
                
            host = "127.0.0.1"
            port = 1234
            db = 0
            password = ""

    class log:
        
        level = "DEBUG"                    
        file_name = "app.log" 
        path = Path(__file__).parent.parent / "log"   
        fmt = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        print_level = 15
        

    class time:

        timezone = "UTC"
        timeformat = "%Y-%m-%d %H:%M:%S"
        
    class db:
        
        user = ""
        password = ""
        host = ""
        port = ""
        database = ""
        
        class ssh:
            
            host = ""
            port = 1234
            user = ""
            passwd = None
            privateKeyPath = "C:\\.ppk"
        
    class redis:
        
        host = ""
        port = ""
        db = 0
        password = ""
        
        class ssh:
            
            host = ""
            port = 1234
            user = ""
            passwd = None
            privateKeyPath = "C:\\.ppk"
        
        class cache:
            pass