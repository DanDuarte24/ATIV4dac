import argparse
import signal

from .protocol import UDPServer


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de invocação remota via UDP")
    parser.add_argument("--host", default="0.0.0.0", help="Endereço de escuta (padrão: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=5000, help="Porta UDP (padrão: 5000)")
    args = parser.parse_args()

    server = UDPServer(args.host, args.port)
    print(f"Servidor UDP aguardando em {server.address[0]}:{server.address[1]}")
    signal.signal(signal.SIGINT, lambda *_: server.close())
    try:
        server.serve_forever()
    except OSError:
        pass
    finally:
        server.close()
        print("Servidor encerrado.")


if __name__ == "__main__":
    main()
