import ssl
import certifi
from dataclasses import dataclass
from typing import List, Optional
from geopy.geocoders import Nominatim

# --- SSL fix (macOS / Python 3.13+) ---
ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where()
)

# --- Static European data ---

EUROPE_CURRENCY = {
    "AL": "ALL", "AT": "EUR", "BE": "EUR", "BG": "BGN", "CH": "CHF",
    "CY": "EUR", "CZ": "CZK", "DE": "EUR", "DK": "DKK", "EE": "EUR",
    "ES": "EUR", "FI": "EUR", "FR": "EUR", "GB": "GBP", "GR": "EUR",
    "HR": "EUR", "HU": "HUF", "IE": "EUR", "IS": "ISK", "IT": "EUR",
    "LI": "CHF", "LT": "EUR", "LU": "EUR", "LV": "EUR", "MT": "EUR",
    "NL": "EUR", "NO": "NOK", "PL": "PLN", "PT": "EUR", "RO": "RON",
    "RS": "RSD", "SE": "SEK", "SI": "EUR", "SK": "EUR", "UA": "UAH",
}

EUROPE_LANGUAGES = {
    "AL": ["sq"], "AT": ["de"], "BE": ["nl", "fr", "de"], "BG": ["bg"],
    "CH": ["de", "fr", "it", "rm"], "CY": ["el", "tr"], "CZ": ["cs"],
    "DE": ["de"], "DK": ["da"], "EE": ["et"], "ES": ["es"],
    "FI": ["fi", "sv"], "FR": ["fr"], "GB": ["en"], "GR": ["el"],
    "HR": ["hr"], "HU": ["hu"], "IE": ["en", "ga"], "IS": ["is"],
    "IT": ["it"], "LI": ["de"], "LT": ["lt"], "LU": ["fr", "de", "lb"],
    "LV": ["lv"], "MT": ["mt", "en"], "NL": ["nl"], "NO": ["no"],
    "PL": ["pl"], "PT": ["pt"], "RO": ["ro"], "RS": ["sr"],
    "SE": ["sv"], "SI": ["sl"], "SK": ["sk"], "UA": ["uk"],
}

LANGUAGE_NAMES = {
    "en": "English", "de": "German", "fr": "French", "it": "Italian",
    "es": "Spanish", "pt": "Portuguese", "nl": "Dutch", "sv": "Swedish",
    "no": "Norwegian", "da": "Danish", "fi": "Finnish", "pl": "Polish",
    "cs": "Czech", "sk": "Slovak", "hu": "Hungarian", "ro": "Romanian",
    "bg": "Bulgarian", "hr": "Croatian", "sl": "Slovenian",
    "sr": "Serbian", "el": "Greek", "et": "Estonian", "lv": "Latvian",
    "lt": "Lithuanian", "is": "Icelandic", "ga": "Irish",
    "mt": "Maltese", "sq": "Albanian", "uk": "Ukrainian",
    "rm": "Romansh", "lb": "Luxembourgish",
}

# --- Data model ---

@dataclass
class LocaleInfo:
    source_address: str
    country_code: Optional[str] = None
    currency: Optional[str] = None
    language_codes: List[str] = None
    languages: List[str] = None

    def __post_init__(self) -> None:
        self.language_codes = []
        self.languages = []
        self._resolve()

    def _resolve(self) -> None:
        geolocator = Nominatim(user_agent="locale-info-resolver")

        location = geolocator.geocode(
            self.source_address,
            addressdetails=True,
            language="en"
        )

        if not location:
            return

        address = location.raw.get("address", {})
        self.country_code = address.get("country_code", "").upper()

        self._resolve_currency()
        self._resolve_languages()

    def _resolve_currency(self) -> None:
        self.currency = EUROPE_CURRENCY.get(self.country_code)

    def _resolve_languages(self) -> None:
        self.language_codes = EUROPE_LANGUAGES.get(self.country_code, [])
        self.languages = [
            LANGUAGE_NAMES.get(code, code)
            for code in self.language_codes
        ]

    def __str__(self) -> str:
        return (
            f"LocaleInfo("
            f"address='{self.source_address}', "
            f"country_code='{self.country_code}', "
            f"currency='{self.currency}', "
            f"languages={self.languages})"
        )


# --- Test function ---

def test_locale_info() -> None:
    test_addresses = [
        "Bundesplatz 1, 3005 Bern, Switzerland",
        "10 Downing Street, London, UK",
        "Champs-Élysées, Paris, France",
        "Via Roma, Rome, Italy",
    ]

    for addr in test_addresses:
        locale = LocaleInfo(addr)
        print(locale)


if __name__ == "__main__":
    test_locale_info()