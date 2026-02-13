"""Translation module using Anthropic Claude API.

Translates Korean text to English or German with natural, conversational output.
"""

import sys
from anthropic import AsyncAnthropic


class Translator:
    """Translates Korean text to target language using Claude API."""

    def __init__(self, api_key: str, target_language: str = "en"):
        """Initialize translator with API key and target language.

        Args:
            api_key: Anthropic API key
            target_language: Target language code ("en" or "de")
        """
        self._client = AsyncAnthropic(api_key=api_key)
        self._target_lang = target_language
        self._system_prompt = self._build_system_prompt(target_language)

    def _build_system_prompt(self, lang: str) -> str:
        """Build system prompt for the target language.

        Args:
            lang: Language code ("en" for English, "de" for German)

        Returns:
            System prompt string for Claude
        """
        language_name = "English" if lang == "en" else "German"
        return (
            f"You are a real-time voice translator. Translate the following Korean "
            f"text into natural, conversational {language_name}. Rules: "
            f"1) Produce ONLY the translation, no explanations or meta-commentary. "
            f"2) Keep it concise - match the brevity of spoken language, not written prose. "
            f"3) Preserve the speaker's tone and meaning. "
            f"4) If the input is a greeting or filler, translate it naturally."
        )

    async def translate(self, text: str) -> str:
        """Translate Korean text to target language.

        Args:
            text: Korean text to translate

        Returns:
            Translated text, or empty string on error
        """
        if not text or not text.strip():
            return ""

        try:
            response = await self._client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                system=self._system_prompt,
                messages=[{"role": "user", "content": text}],
            )

            # Extract text from response
            translated = response.content[0].text.strip()
            return translated

        except Exception as e:
            print(f"Translation error: {e}", file=sys.stderr)
            return ""

    def set_target_language(self, lang: str):
        """Set target language for translation.

        Args:
            lang: Language code ("en" for English, "de" for German)
        """
        self._target_lang = lang
        self._system_prompt = self._build_system_prompt(lang)
