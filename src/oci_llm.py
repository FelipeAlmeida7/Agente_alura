from __future__ import annotations

import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

SYSTEM_PROMPT = """Você é o Assistente Corporativo IA de uma empresa fictícia.
Responda apenas com base no contexto documental fornecido.
Se a informação não estiver no contexto, diga claramente que não encontrou a resposta nos documentos disponíveis.
Seja objetivo, profissional e cite os nomes das fontes usadas ao final da resposta.
Não invente políticas, números, prazos ou regras.
"""


def is_configured() -> bool:
    required = [
        "OCI_GENAI_BASE_URL",
        "OCI_GENAI_API_KEY",
        "OCI_GENAI_PROJECT_OCID",
        "OCI_GENAI_MODEL",
    ]
    return all(os.getenv(item) for item in required)


def answer_with_oci(question: str, context: str) -> str:
    if not is_configured():
        raise RuntimeError("OCI Generative AI ainda não foi configurado nas variáveis de ambiente.")

    client = OpenAI(
        base_url=os.environ["OCI_GENAI_BASE_URL"],
        api_key=os.environ["OCI_GENAI_API_KEY"],
        project=os.environ["OCI_GENAI_PROJECT_OCID"],
    )

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"CONTEXTO DOCUMENTAL:\n{context}\n\n"
        f"PERGUNTA DO COLABORADOR:\n{question}"
    )

    response = client.responses.create(
        model=os.environ["OCI_GENAI_MODEL"],
        input=prompt,
    )
    return response.output_text
