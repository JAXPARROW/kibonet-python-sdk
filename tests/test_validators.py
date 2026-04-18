"""
Tests for the PhoneNumberValidator utility.
"""

import pytest
from kibonet_sdk.utils.validators import PhoneNumberValidator


class TestPhoneNumberValidator:

    # ---- validate ----

    def test_valid_tz_international(self):
        assert PhoneNumberValidator.validate("255712345678") is True

    def test_valid_tz_local_format(self):
        assert PhoneNumberValidator.validate("0712345678") is True

    def test_valid_tz_plus_prefix(self):
        assert PhoneNumberValidator.validate("+255712345678") is True

    def test_invalid_empty(self):
        assert PhoneNumberValidator.validate("") is False

    def test_invalid_none(self):
        assert PhoneNumberValidator.validate(None) is False  # type: ignore[arg-type]

    def test_invalid_letters(self):
        assert PhoneNumberValidator.validate("invalid_phone") is False

    def test_invalid_too_short(self):
        assert PhoneNumberValidator.validate("255123") is False

    # ---- clean ----

    def test_clean_tz_international(self):
        assert PhoneNumberValidator.clean("255712345678") == "255712345678"

    def test_clean_local_converts_to_international(self):
        assert PhoneNumberValidator.clean("0712345678") == "255712345678"

    def test_clean_strips_plus(self):
        assert PhoneNumberValidator.clean("+255712345678") == "255712345678"

    def test_clean_raises_on_invalid(self):
        with pytest.raises(ValueError, match="Invalid phone number"):
            PhoneNumberValidator.clean("invalid")

    def test_clean_raises_on_empty(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            PhoneNumberValidator.clean("")

    # ---- to_csv ----

    def test_to_csv_from_list(self):
        result = PhoneNumberValidator.to_csv(["255712345678", "255798765432"])
        assert result == "255712345678,255798765432"

    def test_to_csv_from_string(self):
        result = PhoneNumberValidator.to_csv("255712345678")
        assert result == "255712345678"

    def test_to_csv_from_csv_string(self):
        result = PhoneNumberValidator.to_csv("255712345678, 255798765432")
        assert result == "255712345678,255798765432"

    def test_to_csv_local_format_in_list(self):
        result = PhoneNumberValidator.to_csv(["0712345678"])
        assert result == "255712345678"

    def test_to_csv_empty_raises(self):
        with pytest.raises(ValueError, match="At least one"):
            PhoneNumberValidator.to_csv([])

    # ---- validate_batch ----

    def test_validate_batch(self):
        results = PhoneNumberValidator.validate_batch(
            ["255712345678", "invalid", "0798765432"]
        )
        assert results[0] == ("255712345678", True)
        assert results[1] == ("invalid", False)
        assert results[2] == ("0798765432", True)
