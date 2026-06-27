"""Stateless assistant chat endpoint (no persistence)."""

from __future__ import annotations

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.throttling import SimpleRateThrottle
from rest_framework.views import APIView

from kresh_energy_be.common.serializers import SUPPORTED_LANGUAGES
from kresh_energy_be.common.serializers import resolve_language

from .client import AssistantError
from .client import generate_reply
from .prompt import build_system_prompt
from .serializers import ChatRequestSerializer

# Friendly, localized fallback when the provider is unavailable.
FALLBACK_REPLY = {
    "de": (
        "Entschuldigung, der Assistent ist gerade nicht verfügbar. Bitte "
        "kontaktieren Sie uns direkt per WhatsApp oder Telefon."
    ),
    "en": (
        "Sorry, the assistant is currently unavailable. Please contact us "
        "directly via WhatsApp or phone."
    ),
    "ar": (
        "عذرًا، المساعد غير متاح حاليًا. يرجى التواصل معنا مباشرةً عبر واتساب أو "
        "الهاتف."
    ),
}


# Three layers, all must pass (DRF applies them with AND semantics):
#   1. burst  — stop rapid-fire requests from one client (per IP, short window)
#   2. sustained — bound a single client's usage per hour (per IP)
#   3. global  — a hard ceiling across ALL clients, so distributed / many-IP
#      abuse can't run up unbounded LLM spend.
class AssistantBurstThrottle(AnonRateThrottle):
    scope = "assistant_burst"


class AssistantRateThrottle(AnonRateThrottle):
    scope = "assistant"


class AssistantGlobalThrottle(SimpleRateThrottle):
    scope = "assistant_global"

    def get_cache_key(self, request, view):
        # A single shared bucket for every request to this endpoint.
        return "throttle_assistant_global"


class AssistantChatView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [
        AssistantBurstThrottle,
        AssistantRateThrottle,
        AssistantGlobalThrottle,
    ]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Locale: explicit payload value wins, else the Accept-Language header
        # (resolved by LocaleMiddleware), else the default language.
        locale = (data.get("locale") or "")[:2]
        lang = locale if locale in SUPPORTED_LANGUAGES else resolve_language()

        system_prompt = build_system_prompt(lang)
        history = [
            {"role": m["role"], "content": m["content"]} for m in data["messages"]
        ]

        try:
            reply = generate_reply(system_prompt, history)
        except AssistantError:
            return Response(
                {"reply": FALLBACK_REPLY.get(lang, FALLBACK_REPLY["de"])},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response({"reply": reply}, status=status.HTTP_200_OK)
