import os
from dotenv import load_dotenv
from mistralai import Mistral

load_dotenv()

SYSTEM_PROMPT = """Tu es un assistant clientèle multi-enseigne pour les fast-foods en France : Quick, Burger King, McDonald's et KFC.
Tu réponds de façon naturelle, polie et concise en français.
Le nom de l'enseigne est précisé dans le contexte. Utilise-le.
Le menu et les prix fournis dans le contexte sont des informations RÉELLES. Utilise-les en priorité.
Si le contexte ne contient pas l'information demandée, tu peux répondre avec tes connaissances générales sur l'enseigne concernée.
Ne donne JAMAIS de prix ou d'informations que tu inventes. Si tu n'es pas sûr, dis-le honnêtement."""


class MistralHandler:
    def __init__(self):
        api_key = os.environ.get("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError("MISTRAL_API_KEY environment variable not set")
        self.client = Mistral(api_key=api_key)
        self.model = "mistral-small-latest"

    def _build_messages(self, user_question: str, context: str = "") -> list:
        if context:
            user_content = f"Informations disponibles :\n{context}\n\nQuestion du client : {user_question}"
        else:
            user_content = f"Question du client : {user_question}"
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ]

    def generate_answer(self, user_question: str, context: str = "") -> str:
        messages = self._build_messages(user_question, context)
        response = self.client.chat.complete(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    def generate_answer_stream(self, user_question: str, context: str = ""):
        messages = self._build_messages(user_question, context)
        with self.client.chat.stream(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=300
        ) as stream:
            for event in stream:
                if hasattr(event, 'data') and hasattr(event.data, 'choices'):
                    content = event.data.choices[0].delta.content
                    if content:
                        yield content