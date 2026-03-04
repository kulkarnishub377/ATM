"""
atm.strings
-----------
Bilingual (English / Hindi) UI string dictionary and lookup helper.
"""

from atm.enums import Language

_STRINGS: dict[str, dict[Language, str]] = {
    "welcome": {
        Language.ENGLISH: "WELCOME",
        Language.HINDI:   "स्वागत है",
    },
    "insert_card": {
        Language.ENGLISH: "Please insert your card",
        Language.HINDI:   "कृपया अपना कार्ड डालें",
    },
    "enter_pin": {
        Language.ENGLISH: "Enter 4-digit PIN: ",
        Language.HINDI:   "4-अंकीय PIN दर्ज करें: ",
    },
    "incorrect_pin": {
        Language.ENGLISH: "Incorrect PIN.",
        Language.HINDI:   "गलत PIN.",
    },
    "card_blocked": {
        Language.ENGLISH: "Card blocked due to multiple wrong PIN attempts.",
        Language.HINDI:   "कई गलत PIN प्रयासों के कारण कार्ड ब्लॉक कर दिया गया।",
    },
    "auth_success": {
        Language.ENGLISH: "Authentication successful.",
        Language.HINDI:   "प्रमाणीकरण सफल।",
    },
    "thank_you": {
        Language.ENGLISH: "Thank you for banking with us. Have a nice day!",
        Language.HINDI:   "हमारे साथ बैंकिंग के लिए धन्यवाद। आपका दिन शुभ हो!",
    },
    "please_wait": {
        Language.ENGLISH: "Please wait...",
        Language.HINDI:   "कृपया प्रतीक्षा करें...",
    },
}


def T(key: str, lang: Language) -> str:
    """Return the translation for *key* in *lang*, falling back to English."""
    return (
        _STRINGS.get(key, {}).get(lang)
        or _STRINGS.get(key, {}).get(Language.ENGLISH, key)
    )
