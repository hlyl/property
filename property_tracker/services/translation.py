"""Translation services for property descriptions.

Provides two implementations:
- DeepTranslatorService: Free translation using deep-translator library
- GoogleTransService: Google Translate API (fallback option)
"""

from typing import Protocol

from loguru import logger


class TranslationService(Protocol):
    """Interface for translation services."""

    def translate(self, text: str) -> str:
        """Translate text from Italian to Danish.

        Args:
            text: Italian text to translate

        Returns:
            Translated Danish text
        """
        ...


class DeepTranslatorService:
    """Free translation service using deep-translator library.

    Uses the deep-translator library which provides free access to
    multiple translation services including Google Translate (unofficial),
    MyMemory, and others. No API key required.
    """

    def __init__(self, service: str = "google") -> None:
        """Initialize the translation service.

        Args:
            service: Translation service to use ('google' or 'mymemory')
                    Default: 'google' (unofficial Google Translate, free)
        """
        try:
            from deep_translator import GoogleTranslator, MyMemoryTranslator
        except ImportError:
            raise ImportError(
                "deep-translator library not installed. "
                "Install with: uv sync (should be in main dependencies)"
            ) from None

        self.service = service
        if service == "google":
            self.translator = GoogleTranslator(source="it", target="da")
            logger.info("Using deep-translator with Google Translate (free, unofficial)")
        elif service == "mymemory":
            self.translator = MyMemoryTranslator(source="it", target="da")
            logger.info("Using deep-translator with MyMemory (free, 5000 chars/day)")
        else:
            raise ValueError(f"Unknown translation service: {service}")

    def translate(self, text: str) -> str:
        """Translate Italian text to Danish.

        Args:
            text: Italian text to translate

        Returns:
            Danish translation, or original text if translation fails
        """
        if not text or not text.strip():
            return text

        try:
            # deep-translator has a 5000 character limit per request
            if len(text) > 4500:
                # Split and translate in chunks
                chunks = [text[i : i + 4500] for i in range(0, len(text), 4500)]
                translations = []
                for chunk in chunks:
                    translated = self.translator.translate(chunk)
                    translations.append(translated if translated else chunk)
                result = " ".join(translations)
                logger.debug(
                    f"Translated {len(text)} chars in {len(chunks)} chunks using {self.service}"
                )
                return result
            else:
                result = self.translator.translate(text)
                if result:
                    logger.debug(f"Translated {len(text)} chars using {self.service}")
                    return result
                else:
                    logger.warning(
                        "Translation returned empty result, returning original text"
                    )
                    return text
        except Exception as e:
            logger.error(f"Translation failed with {self.service}: {e}")
            logger.warning("Returning original text due to translation failure")
            return text  # Return original text on failure


class GoogleTransService:
    """Google Translate service using googletrans library (fallback).

    Uses the unofficial googletrans library. This library can be unreliable
    and may break without warning. Provided as a fallback option.

    NOTE: This library is deprecated and frequently breaks. Use DeepTranslatorService instead.
    """

    def __init__(self) -> None:
        """Initialize Google Translate service.

        Raises:
            ImportError: If googletrans library is not installed
        """
        try:
            from googletrans import Translator
        except ImportError:
            raise ImportError(
                "googletrans library not installed. "
                "Install with: uv sync --extra google"
            ) from None

        self.translator = Translator()
        logger.warning(
            "Using googletrans (deprecated, unreliable). "
            "Consider using DeepTranslatorService instead."
        )

    def translate(self, text: str) -> str:
        """Translate Italian text to Danish.

        Args:
            text: Italian text to translate

        Returns:
            Danish translation, or original text if translation fails
        """
        if not text or not text.strip():
            return text

        try:
            result = self.translator.translate(text, dest="da")
            if result and result.text:
                logger.debug(f"Translated {len(text)} chars using googletrans")
                return result.text
            else:
                logger.warning("googletrans returned empty result")
                return text
        except Exception as e:
            logger.error(f"googletrans translation failed: {e}")
            return text


def get_translation_service(use_google: bool = False) -> TranslationService:
    """Factory function to get the appropriate translation service.

    Args:
        use_google: If True, use googletrans library (deprecated, unreliable)
                   If False, use deep-translator (recommended, free)

    Returns:
        TranslationService implementation
    """
    if use_google:
        logger.warning(
            "Using deprecated googletrans library. Consider using deep-translator instead."
        )
        return GoogleTransService()
    else:
        logger.info("Using deep-translator for translations (recommended, free)")
        return DeepTranslatorService(service="google")
