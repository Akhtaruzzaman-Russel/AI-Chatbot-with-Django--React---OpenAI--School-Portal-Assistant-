import os
from pathlib import Path

from django.conf import settings
from openai import OpenAI
from openai import APIStatusError, APIConnectionError
from rest_framework.decorators import api_view
from rest_framework.response import Response


BASE_DIR = Path(__file__).resolve().parent.parent


def build_mock_reply(user_message: str) -> str:
    message = (user_message or "").strip()
    if not message:
        return "Mock reply: I’m here to help. Please ask a question about the school portal."

    return (
        f"Mock reply: I’m unable to reach the OpenAI service right now, "
        f"but I can still help with your message: {message}"
    )


def load_system_prompt():
    prompt_path = BASE_DIR / "prompts" / "unihelp_template.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


@api_view(["POST"])
def chat_with_unihelp(request):
    try:
        api_key = getattr(settings, "OPENAI_API_KEY", None) or os.getenv("OPENAI_API_KEY")
        user_message = request.data.get("message", "")

        if not api_key:
            return Response({"response": build_mock_reply(user_message)})

        client = OpenAI(api_key=api_key)
        system_template = load_system_prompt()

        prompt_input = [
            {"role": "system", "content": system_template},
            {"role": "user", "content": user_message},
        ]

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt_input,
            temperature=0.4,
            max_output_tokens=600,
        )

        answer = response.output_text
        return Response({"response": answer})

    except APIStatusError as exc:
        detail = getattr(exc, "body", None)
        message = str(exc)
        if isinstance(detail, dict):
            error_detail = detail.get("error", {})
            if isinstance(error_detail, dict):
                message = error_detail.get("message", message)
        return Response({"error": f"OpenAI API error: {message}"}, status=502)
    except APIConnectionError as exc:
        return Response({"error": f"OpenAI connection error: {str(exc)}"}, status=502)
    except Exception as e:
        return Response(
            {"error": f"An unexpected error occurred. {str(e)}"},
            status=500,
        )
