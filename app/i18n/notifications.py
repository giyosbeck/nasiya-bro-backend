"""Translation dictionary for push notification titles and bodies.

Usage:
    from app.i18n.notifications import t
    body = t("new_user.body", lang=admin.language, name=user.name, type="GADGETS")

`lang` None or unknown falls back to "uz".
"""

from typing import Any

TRANSLATIONS: dict[str, dict[str, str]] = {
    "uz": {
        "new_user.title": "Yangi foydalanuvchi",
        "new_user.body": "{name} ({type}) ro'yxatdan o'tdi — 90 kunlik trial boshlandi",
        "trial_expiring.title": "Trial tugayapti",
        "trial_expiring.body": "Trialingizga {days} kun qoldi. Admin bilan bog'laning.",
        "trial_expired.title": "Obuna muddati tugadi",
        "trial_expired.body": "Davom etish uchun admin bilan bog'laning.",
        "payment_due.title": "Bugun to'lov bor",
        "payment_due.body": "{name} — {amount}",
    },
    "ru": {
        "new_user.title": "Новый пользователь",
        "new_user.body": "{name} ({type}) зарегистрировался — начался 90-дневный триал",
        "trial_expiring.title": "Триал заканчивается",
        "trial_expiring.body": "Осталось {days} дней. Свяжитесь с администратором.",
        "trial_expired.title": "Подписка истекла",
        "trial_expired.body": "Для продолжения свяжитесь с администратором.",
        "payment_due.title": "Сегодня платёж",
        "payment_due.body": "{name} — {amount}",
    },
    "en": {
        "new_user.title": "New user",
        "new_user.body": "{name} ({type}) registered — 90-day trial started",
        "trial_expiring.title": "Trial ending",
        "trial_expiring.body": "{days} days left. Please contact admin.",
        "trial_expired.title": "Subscription expired",
        "trial_expired.body": "Please contact admin to continue.",
        "payment_due.title": "Payment due today",
        "payment_due.body": "{name} — {amount}",
    },
}

FALLBACK_LANG = "uz"


def t(key: str, lang: str | None = None, **kwargs: Any) -> str:
    """Translate a notification key into the target language.

    Unknown lang or key falls back to Uzbek, then to the raw key string.
    """
    resolved = lang if lang in TRANSLATIONS else FALLBACK_LANG
    template = TRANSLATIONS[resolved].get(key)
    if template is None:
        template = TRANSLATIONS[FALLBACK_LANG].get(key, key)
    try:
        return template.format(**kwargs)
    except (KeyError, IndexError):
        return template
