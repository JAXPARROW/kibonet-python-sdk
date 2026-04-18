"""
Phone number validation utilities.

KiboNet accepts numbers in international format (e.g. 255XXXXXXXXX for Tanzania).
Local 0XXXXXXXXX format is automatically converted.
"""

import re
from typing import List, Tuple, Union


class PhoneNumberValidator:
    """Validator for phone numbers used with KiboNet SMS API."""

    # Tanzania country code — most KiboNet customers are TZ-based
    DEFAULT_COUNTRY_CODE = "255"
    TZ_VALID_LENGTH = 12  # 255 + 9 digits

    @classmethod
    def _strip(cls, phone: str) -> str:
        """Remove all non-digit characters (spaces, dashes, +)."""
        return re.sub(r"\D", "", phone)

    @classmethod
    def validate(cls, phone: str) -> bool:
        """
        Return True if *phone* looks like a valid international number.

        Accepts:
        - Tanzanian format  : 255XXXXXXXXX  / 0XXXXXXXXX / +255XXXXXXXXX
        - Any E.164 number  : 1-15 digits with a non-zero leading digit
        """
        if not phone or not isinstance(phone, str):
            return False
        cleaned = cls._strip(phone)
        if cleaned.startswith("0") and len(cleaned) == 10:
            cleaned = cls.DEFAULT_COUNTRY_CODE + cleaned[1:]
        # E.164: 7–15 digits, no leading zero after stripping
        return bool(re.fullmatch(r"[1-9]\d{6,14}", cleaned))

    @classmethod
    def clean(cls, phone: str) -> str:
        """
        Clean and return phone in international format (no + prefix).

        Raises:
            ValueError: If the number is invalid.
        """
        if not phone:
            raise ValueError("Phone number cannot be empty")
        cleaned = cls._strip(phone)
        if cleaned.startswith("0") and len(cleaned) == 10:
            cleaned = cls.DEFAULT_COUNTRY_CODE + cleaned[1:]
        if not cls.validate(cleaned):
            raise ValueError(
                f"Invalid phone number: '{phone}'. "
                "Expected international format e.g. 255712345678"
            )
        return cleaned

    @classmethod
    def validate_batch(cls, phones: List[str]) -> List[Tuple[str, bool]]:
        """Validate a list of numbers, returning (phone, is_valid) tuples."""
        return [(p, cls.validate(p)) for p in phones]

    @classmethod
    def clean_batch(cls, phones: List[str]) -> List[str]:
        """
        Clean a list of phone numbers.

        Raises:
            ValueError: If any number is invalid.
        """
        return [cls.clean(p) for p in phones]

    @classmethod
    def to_csv(cls, phones: Union[str, List[str]]) -> str:
        """
        Convert a string or list of phone numbers to the comma-separated
        format required by KiboNet's ``contacts`` field.

        All numbers are validated and cleaned first.

        Raises:
            ValueError: If any number is invalid.
        """
        if isinstance(phones, str):
            # May already be CSV — split, clean, rejoin
            phones = [p.strip() for p in phones.split(",") if p.strip()]
        if not phones:
            raise ValueError("At least one recipient phone number is required")
        return ",".join(cls.clean_batch(phones))
