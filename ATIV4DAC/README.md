# Invocação Remota de Métodos com UDP

Implementação acadêmica do padrão **Requisição-Resposta** apresentado no material da disciplina de Sistemas Distribuídos. A comunicação utiliza sockets UDP (`SOCK_DGRAM`) e mensagens JSON codificadas em UTF-8.

## 1. Requisitos

- Python 3.10 ou superior
- Não exige bibliotecas externas: utiliza somente a biblioteca padrão do Python

## 2. Estrutura do projeto

```text
protocolo-udp/
├── README.md
├── src/
│   ├── __init__.py
│   ├── protocol.py
│   ├── server.py
│   └── client.py
└── tests/
    └── test_protocol.py
```

## 3. Como executar

Abra um terminal na pasta raiz do projeto.

### Iniciar o servidor

```bash
python (ou py -(versao que esta instalada do pyton no computador virgente do teste)) -m src.server --host 127.0.0.1 --port 5000
```

O servidor ficará aguardando datagramas UDP na porta 5000.

### Executar o cliente

Em outro terminal, na mesma pasta, execute por exemplo:

```bash
python (ou py -(versao que esta instalada do pyton no computador virgente do teste)) -m src.client add 7 5 --host 127.0.0.1 --port 5000
```

Resposta esperada:

```text
Resposta do servidor: 12.0
```

Outros exemplos:

```bash
python -m src.client subtract 9 4
python -m src.client multiply 6 7
python -m src.client divide 20 4
python -m src.client echo "Olá, servidor!"
```

Os argumentos `--host` e `--port` são opcionais no cliente. Por padrão, ele se conecta a `127.0.0.1:5000`.

## 4. Primitivas implementadas

| Primitiva do material | Implementação | Responsabilidade |
|---|---|---|
| `doOperation()` | `UDPClient.do_operation()` | O cliente empacota a operação e seus argumentos, envia a requisição e aguarda a resposta. |
| `getRequest()` | `UDPServer.get_request()` | O servidor recebe o datagrama e extrai identificador, operação, argumentos e endereço do cliente. |
| `sendReply()` | `UDPServer.send_reply()` | O servidor envia o resultado ou uma mensagem de erro ao endereço do cliente. |

### Formato das mensagens

Exemplo de requisição:

```json
{
  "type": "request",
  "request_id": "identificador-unico",
  "operation_id": "add",
  "arguments": [7, 5]
}
```

Exemplo de resposta:

```json
{
  "type": "response",
  "request_id": "identificador-unico",
  "status": "ok",
  "result": 12
}
```

O `request_id` permite associar a resposta à requisição correspondente. A resposta também pode conter `status: "error"` e o campo `error` com a descrição do problema.

## 5. Operações disponíveis

- `add(a, b)`: soma dois números.
- `subtract(a, b)`: subtrai o segundo número do primeiro.
- `multiply(a, b)`: multiplica dois números.
- `divide(a, b)`: divide o primeiro número pelo segundo; divisão por zero retorna erro.
- `echo(value)`: devolve o mesmo valor recebido, útil para testar a troca de mensagens.

## 6. Como executar os testes

Na pasta raiz do projeto, execute:

```bash
python -m unittest discover -s tests -v
```

Os testes iniciam um servidor UDP local em uma porta dinâmica e verificam:

1. Soma, subtração, multiplicação e divisão.
2. Operação `echo` e retorno de texto.
3. Tratamento de operação desconhecida.
4. Tratamento de divisão por zero.
5. Tratamento de quantidade incorreta de argumentos.

Não é necessário iniciar manualmente o servidor para executar os testes.

## 7. Teste entre dois colegas/computadores

1. O colega que atuará como servidor executa `python -m src.server --host 0.0.0.0 --port 5000`.
2. O colega que atuará como cliente executa, substituindo `IP_DO_SERVIDOR` pelo endereço IP acessível do computador servidor:

   ```bash
   python -m src.client add 15 8 --host IP_DO_SERVIDOR --port 5000
   ```

3. Se necessário, liberar a porta **UDP 5000** no firewall do computador servidor.
4. Confirmar que ambos estão na mesma rede ou que existe conectividade entre as máquinas.
5. Repetir com outras operações e registrar os resultados.

> Observação: UDP não estabelece conexão e não garante, por si só, entrega, ordenação ou ausência de duplicatas. O cliente inclui identificador de requisição, tempo limite e retransmissões para lidar com perdas simples. Em uma aplicação real, retransmissões também exigiriam controle de duplicidade no servidor para evitar executar novamente operações que não sejam idempotentes. Esta implementação é didática e não deve ser exposta diretamente à internet.

