import os
import json
from typing import Dict, List, Any

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - allows import even if not installed yet
    OpenAI = None  # type: ignore


def _get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return None
    return OpenAI(api_key=api_key)


def chat_gpt(messages: List[Dict[str, Any]]) -> str:
    client = _get_client()
    if client is None:
        return ""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.2,
    )
    content = response.choices[0].message.content
    return content or ""


def extract_fields_with_gpt(raw_text: str, schema: Dict[str, Any]) -> Dict[str, Any]:
    client = _get_client()
    if client is None:
        return {key: "" for key in schema.keys()}
    system = "Extract and return JSON matching the provided schema keys only."
    user = (
        "Text:\n" + raw_text + "\n\nSchema keys:\n" + str(list(schema.keys())) + "\nReturn valid JSON."
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    try:
        parsed = json.loads(content)
    except Exception:
        parsed = {}
    return {key: parsed.get(key, "") for key in schema.keys()}

