"""Protocolo simples de invocação remota usando UDP e mensagens JSON."""
from __future__ import annotations

import json
import socket
import uuid
from dataclasses import dataclass
from typing import Any


class ProtocolError(Exception):
    """Mensagem recebida não respeita o formato do protocolo."""


@dataclass
class Request:
    request_id: str
    operation_id: str
    arguments: list[Any]
    client_address: tuple[str, int]


def encode_message(message: dict[str, Any]) -> bytes:
    return json.dumps(message, ensure_ascii=False).encode("utf-8")


def decode_message(data: bytes) -> dict[str, Any]:
    try:
        message = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProtocolError("Mensagem não contém JSON válido.") from exc
    if not isinstance(message, dict):
        raise ProtocolError("A mensagem deve ser um objeto JSON.")
    return message


class UDPClient:
    """Implementa doOperation(): invoca uma operação no servidor remoto."""

    def __init__(self, server_host: str, server_port: int, timeout: float = 2.0, retries: int = 2):
        self.server = (server_host, server_port)
        self.timeout = timeout
        self.retries = retries

    def do_operation(self, operation_id: str, arguments: list[Any]) -> Any:
        request_id = str(uuid.uuid4())
        request = {
            "type": "request",
            "request_id": request_id,
            "operation_id": operation_id,
            "arguments": arguments,
        }
        payload = encode_message(request)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(self.timeout)
            for attempt in range(self.retries + 1):
                sock.sendto(payload, self.server)
                try:
                    data, address = sock.recvfrom(65535)
                except socket.timeout:
                    if attempt == self.retries:
                        raise TimeoutError("O servidor não respondeu dentro do tempo esperado.")
                    continue

                if address != self.server:
                    continue
                response = decode_message(data)
                if response.get("request_id") != request_id:
                    continue
                if response.get("type") != "response":
                    raise ProtocolError("Tipo de resposta inesperado.")
                if response.get("status") == "error":
                    raise RuntimeError(response.get("error", "Erro não especificado pelo servidor."))
                return response.get("result")

        raise TimeoutError("Não foi possível obter uma resposta válida.")


class UDPServer:
    """Implementa getRequest() e sendReply() para operações UDP."""

    def __init__(self, host: str = "127.0.0.1", port: int = 5000):
        self.address = (host, port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.address)
        self.address = self.socket.getsockname()
        self.running = False
        self.operations = {
            "add": self._add,
            "subtract": self._subtract,
            "multiply": self._multiply,
            "divide": self._divide,
            "echo": self._echo,
        }

    def get_request(self) -> Request:
        """Aguarda uma requisição e devolve seus dados e endereço de origem."""
        data, client_address = self.socket.recvfrom(65535)
        message = decode_message(data)
        if message.get("type") != "request":
            raise ProtocolError("Tipo de mensagem inesperado; era esperada uma requisição.")
        request_id = message.get("request_id")
        operation_id = message.get("operation_id")
        arguments = message.get("arguments")
        if not isinstance(request_id, str) or not isinstance(operation_id, str) or not isinstance(arguments, list):
            raise ProtocolError("Campos obrigatórios ausentes ou inválidos.")
        return Request(request_id, operation_id, arguments, client_address)

    def send_reply(self, request: Request, result: Any = None, error: str | None = None) -> None:
        """Envia o resultado ao cliente, concluindo o ciclo requisição-resposta."""
        response = {
            "type": "response",
            "request_id": request.request_id,
            "status": "error" if error else "ok",
        }
        if error:
            response["error"] = error
        else:
            response["result"] = result
        self.socket.sendto(encode_message(response), request.client_address)

    def handle_request(self, request: Request) -> None:
        operation = self.operations.get(request.operation_id)
        if operation is None:
            self.send_reply(request, error=f"Operação desconhecida: {request.operation_id}")
            return
        try:
            result = operation(*request.arguments)
            self.send_reply(request, result=result)
        except (TypeError, ValueError, ZeroDivisionError) as exc:
            self.send_reply(request, error=str(exc))

    def serve_forever(self) -> None:
        self.running = True
        while self.running:
            try:
                request = self.get_request()
                self.handle_request(request)
            except socket.timeout:
                continue
            except ProtocolError:
                # Pacote inválido: descarta e continua aguardando novas requisições.
                continue
            except OSError:
                if self.running:
                    raise

    def close(self) -> None:
        self.running = False
        self.socket.close()

    @staticmethod
    def _add(a: float, b: float) -> float:
        return a + b

    @staticmethod
    def _subtract(a: float, b: float) -> float:
        return a - b

    @staticmethod
    def _multiply(a: float, b: float) -> float:
        return a * b

    @staticmethod
    def _divide(a: float, b: float) -> float:
        if b == 0:
            raise ZeroDivisionError("Não é possível dividir por zero.")
        return a / b

    @staticmethod
    def _echo(value: Any) -> Any:
        return value
