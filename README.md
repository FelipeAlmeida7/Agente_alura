# Christinus

O Christinus é uma aplicação desenvolvida em Python e Streamlit para análise de arquivos de log.

A aplicação identifica níveis de log, erros recorrentes, horários de ocorrência, endereços IP e códigos HTTP. Também possui uma opção de análise utilizando OCI Generative AI para explicar possíveis causas dos erros e sugerir formas de correção.

## Como funciona

O usuário pode:
- Enviar um arquivo `.log` ou `.txt`;
- Colar um log diretamente na aplicação;
- Utilizar um log de exemplo;
- Visualizar a quantidade de linhas analisadas;
- Identificar erros e avisos;
- Encontrar erros que aparecem várias vezes;
- Ver os horários em que ocorreram erros;
- Identificar os IPs mais frequentes;
- Identificar códigos HTTP;
- Filtrar e pesquisar linhas específicas do log;
- Utilizar a OCI Generative AI para analisar os erros;
- Baixar um relatório em formato `.md`.

## Estrutura

```text
Christinus/
├── app.py
├── src/
│   └── oci_llm.py
├── requirements.txt
├── .env
├── .env.example
├── Dockerfile
└── README.md

É o arquivo principal do projeto.

Nele estão:

* A interface da aplicação;
* A entrada das perguntas do usuário;
* A comunicação com a OCI Generative AI;
* O processamento da resposta;
* A exibição da resposta na tela.

### requirements.txt

Contém as bibliotecas Python utilizadas pelo projeto.

Para instalar:

```bash
pip install -r requirements.txt
```

### .env.example

Contém um exemplo das variáveis necessárias para conectar o projeto à OCI Generative AI.

As informações reais devem ser colocadas em um arquivo `.env`.

A chave de API não deve ser enviada para o GitHub.

### Dockerfile

Contém as instruções necessárias para criar uma imagem Docker do projeto.

## Como o código funciona

O funcionamento básico é:

```text
Usuário
   ↓
Streamlit
   ↓
app.py
   ↓
OCI Generative AI
   ↓
Modelo de IA
   ↓
Resposta
   ↓
Streamlit
```

O usuário faz uma pergunta pela interface do Streamlit. O `app.py` recebe essa pergunta e envia uma requisição para a OCI Generative AI.

A OCI processa a pergunta utilizando o modelo configurado e retorna uma resposta. O `app.py` recebe essa resposta e a apresenta novamente no Streamlit.

## Configuração

Primeiro, crie um ambiente virtual:

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Depois instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env`  e configure as informações da OCI Generative AI.

## Executando

Para iniciar a aplicação:

```bash
streamlit run app.py
```

Depois, o Streamlit disponibilizará a aplicação no navegador.

## Tecnologias utilizadas

* Python
* Streamlit
* OCI Generative AI
* Docker
* Oracle Cloud Infrastructure

## Docker

O projeto também pode ser executado utilizando Docker.

Para criar a imagem:

```bash
docker build -t christinus .
```

Para executar:

```bash
docker run --env-file .env -p 8501:8501 christinus
```

A porta `8501` é utilizada pelo Streamlit.
### NAO CONSEGUI COLOCAR UMA FOTO OU IMAGEM RODANDO NA ORACLE CLOUD
Tentei criar uma conta mas n conseguia de forma alguma, ate colocando cartao de credito e n foi
