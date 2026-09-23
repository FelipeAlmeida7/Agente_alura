# Deploy do Christinus na Oracle Cloud

O Christinus pode ser executado localmente ou hospedado na Oracle Cloud Infrastructure (OCI). Este guia mostra o processo para configurar a OCI Generative AI, preparar a aplicação, criar o container e disponibilizá-lo na nuvem.

---

## 1. Preparando o acesso à OCI

Primeiro, é necessário possuir uma conta na Oracle Cloud e acesso aos serviços utilizados pelo projeto.

Na OCI, será utilizado principalmente:

* **Generative AI** — responsável pela análise dos logs com inteligência artificial;
* **Container Registry** — utilizado para armazenar a imagem Docker;
* **Container Instances** — responsável por executar a aplicação.

No serviço **Generative AI**, crie ou utilize um projeto existente.

Durante essa configuração, serão necessárias as informações fornecidas pela Oracle, como:

* URL de inferência;
* OCID do projeto;
* chave de acesso da API;
* modelo de IA escolhido.

Esses valores devem ser configurados no ambiente da aplicação.

> **Importante:** chaves e credenciais da OCI não devem ser colocadas diretamente no código ou enviadas para repositórios públicos.

---

## 2. Configuração das variáveis

O projeto possui um arquivo `.env.example` que serve como modelo para as configurações necessárias.

Faça uma cópia desse arquivo:

### Linux/macOS

```bash
cp .env.example .env
```

### Windows

```bash
copy .env.example .env
```

Depois, abra o `.env` e preencha os valores referentes à OCI Generative AI.

O arquivo `.env` deve permanecer fora do controle de versão caso contenha informações secretas.

---

## 3. Executando o Christinus no computador

Antes de enviar a aplicação para a nuvem, é recomendado verificar se ela funciona localmente.

Crie o ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente.

### Linux/macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Por fim, execute:

```bash
streamlit run app.py
```

O Streamlit iniciará a aplicação localmente.

---

## 4. Criando o container

O projeto possui um `Dockerfile`, que contém as instruções necessárias para montar o ambiente da aplicação.

A imagem pode ser criada com:

```bash
docker build -t christinus .
```

Depois de criada, execute um container para verificar se tudo está funcionando:

```bash
docker run --env-file .env -p 8501:8501 christinus
```

A porta `8501` é utilizada pelo Streamlit.

Se a aplicação abrir corretamente, o container está pronto para ser enviado para a OCI.

---

## 5. Enviando a imagem para a Oracle

A imagem Docker precisa estar disponível no **OCI Container Registry** para que a Oracle possa utilizá-la posteriormente.

No Console da OCI:

1. Acesse o **Container Registry**;
2. Crie um repositório para o projeto;
3. Configure a autenticação do Docker conforme as instruções apresentadas pela Oracle;
4. Adicione uma tag à imagem;
5. Faça o `push` da imagem para o repositório.

Depois desse processo, a imagem do Christinus estará armazenada no registro da OCI.

---

## 6. Executando o projeto na nuvem

Com a imagem disponível no Container Registry, é possível criar uma **Container Instance**.

No Console da Oracle:

**Developer Services → Container Instances**

Crie uma nova instância e configure:

* A imagem Docker armazenada no Container Registry;
* A porta `8501`;
* As variáveis de ambiente utilizadas pelo projeto;
* A rede/subnet necessária para permitir o acesso à aplicação.

As configurações relacionadas à rede devem permitir que o acesso externo chegue à aplicação.

Após finalizar a configuração, inicie a Container Instance.

---

## 7. Acessando a aplicação

Quando a instância estiver em execução, a OCI disponibilizará as informações necessárias para acessar o container.

Utilize o endereço público fornecido pela infraestrutura para abrir o Christinus no navegador.

O fluxo completo fica:

```text
Código do Christinus
        ↓
Dockerfile
        ↓
Imagem Docker
        ↓
OCI Container Registry
        ↓
OCI Container Instance
        ↓
Aplicação Streamlit
        ↓
Acesso pelo navegador
```

---

## 8. Testando a integração com a IA

Depois que o sistema estiver funciona
