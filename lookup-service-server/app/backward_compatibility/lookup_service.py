class LookupService:
    SERVICE_URI_PREFIX = "lookup"
    port = 8080
    host = "localhost"
    datadirectory = "../elements"
    http_server = None
    LOOKUP_SERVICE = "lookup"

    def get_port(self):
        return LookupService.port
    
    def set_port(self, port: int):
        LookupService.port = port

    def get_host(self):
        return LookupService.host
    
    def set_host(self, host: str):
        LookupService.host = host

    def get_data_directory(self):
        return LookupService.datadirectory
    
    def set_data_diretory(self, datadirectory: str):
        LookupService.datadirectory = datadirectory

    def __init__(self, host:str="localhost", port:int=8080):
        LookupService.host = host
        LookupService.port = port
    
