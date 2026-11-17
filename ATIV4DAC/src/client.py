import argparse

from .protocol import UDPClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Cliente de invocação remota via UDP")
    parser.add_argument("operation", choices=["add", "subtract", "multiply", "divide", "echo"])
    parser.add_argument("arguments", nargs="*", help="Argumentos da operação")
    parser.add_argument("--host", default="127.0.0.1", help="Endereço do servidor")
    parser.add_argument("--port", type=int, default=5000, help="Porta UDP do servidor")
    args = parser.parse_args()

    values = args.arguments
    if args.operation in {"add", "subtract", "multiply", "divide"}:
        try:
            values = [float(value) for value in values]
        except ValueError as exc:
            parser.error(f"Os argumentos matemáticos devem ser números: {exc}")
    try:
        result = UDPClient(args.host, args.port).do_operation(args.operation, values)
        print(f"Resposta do servidor: {result}")
    except (TimeoutError, RuntimeError, ValueError) as exc:
        parser.exit(1, f"Erro na invocação remota: {exc}\n")


if __name__ == "__main__":
    main()
