from hybirdmongo_monitor import server
from prometheus_client import start_http_server


def main():
    start_http_server(8000)
    server.main()
