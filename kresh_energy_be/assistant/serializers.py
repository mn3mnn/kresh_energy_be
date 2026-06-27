"""Request/response serializers for the assistant endpoint."""

from __future__ import annotations

from rest_framework import serializers

# Bound the conversation so prompts stay small; keep only the most recent turns.
MAX_HISTORY = 12
MAX_MESSAGE_CHARS = 2000


class ChatMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=["user", "assistant"])
    content = serializers.CharField(
        max_length=MAX_MESSAGE_CHARS,
        trim_whitespace=True,
        allow_blank=False,
    )


class ChatRequestSerializer(serializers.Serializer):
    messages = serializers.ListField(
        child=ChatMessageSerializer(),
        allow_empty=False,
        max_length=100,
    )
    locale = serializers.CharField(required=False, allow_blank=True, max_length=5)

    def validate_messages(self, value):
        if value[-1]["role"] != "user":
            msg = "The last message must be from the user."
            raise serializers.ValidationError(msg)
        # Keep only the most recent turns to bound prompt size.
        return value[-MAX_HISTORY:]


class ChatResponseSerializer(serializers.Serializer):
    reply = serializers.CharField()
