"""Keyboards — trilingual (uz/en/ru)."""
from datetime import date, timedelta
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from i18n import LANGS, t, get_lang
from config import ADMIN_IDS
from db import is_teacher


# ─── Language Picker ──────────────────────────────────

def lang_picker_keyboard():
    buttons = [
        [InlineKeyboardButton(label, callback_data=f"lang_{code}")]
        for label, code in LANGS.items()
    ]
    return InlineKeyboardMarkup(buttons)


# ─── Student Reply Keyboard ──────────────────────────

def student_reply_keyboard(lang="uz"):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(t("menu_slots", lang))],
            [KeyboardButton(t("menu_mybookings", lang)),
             KeyboardButton(t("menu_cancel", lang))],
        ],
        resize_keyboard=True,
    )


# ─── Admin Reply Keyboard ────────────────────────────

def admin_reply_keyboard(lang="uz"):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(t("menu_newslot", lang)),
             KeyboardButton(t("menu_myslots", lang))],
            [KeyboardButton(t("menu_recurring", lang)),
             KeyboardButton(t("menu_myrecurring", lang))],
            [KeyboardButton(t("menu_addteacher", lang)),
             KeyboardButton(t("menu_teachers", lang))],
            [KeyboardButton(t("menu_all_bookings", lang)),
             KeyboardButton(t("menu_pending_payments", lang))],
        ],
        resize_keyboard=True,
    )


# ─── Teacher Reply Keyboard ──────────────────────────

def teacher_reply_keyboard(lang="uz"):
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton(t("menu_newslot", lang)),
             KeyboardButton(t("menu_myslots", lang))],
            [KeyboardButton(t("menu_recurring", lang)),
             KeyboardButton(t("menu_myrecurring", lang))],
        ],
        resize_keyboard=True,
    )


# ─── Date Picker ─────────────────────────────────────

def date_picker_keyboard(lang="uz"):
    today = date.today()
    buttons = []
    for i in range(7):
        d = today + timedelta(days=i)
        label = d.strftime("%d.%m")
        cb = f"addslot_date_{d.strftime('%Y-%m-%d')}"
        buttons.append([InlineKeyboardButton(label, callback_data=cb)])
    return InlineKeyboardMarkup(buttons)


# ─── Time Picker ─────────────────────────────────────

TIMES = ["09:00", "10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00", "18:00"]


def time_picker_keyboard(selected_date, lang="uz"):
    buttons = []
    row = []
    for tm in TIMES:
        row.append(InlineKeyboardButton(
            tm,
            callback_data=f"addslot_time_{selected_date}_{tm}",
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


# ─── Day Picker (Recurring) ──────────────────────────

HEADER_DAYS_uz = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
HEADER_DAYS_en = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]
HEADER_DAYS_ru = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

HEADER_DAYS_BY_LANG = {"uz": HEADER_DAYS_uz, "en": HEADER_DAYS_en, "ru": HEADER_DAYS_ru}


def day_picker_keyboard(lang="uz"):
    days = HEADER_DAYS_BY_LANG.get(lang, HEADER_DAYS_uz)
    buttons = []
    row = []
    for i, label in enumerate(days):
        row.append(InlineKeyboardButton(label, callback_data=f"recur_day_{i}"))
        if len(row) == 4:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def time_picker_recurring_keyboard(day_of_week, lang="uz"):
    buttons = []
    row = []
    for tm in TIMES:
        row.append(InlineKeyboardButton(
            tm,
            callback_data=f"recur_time_{day_of_week}_{tm}",
        ))
        if len(row) == 3:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)


def recurring_list_keyboard(patterns, lang="uz"):
    buttons = []
    from db import DAY_NAMES_I18N
    day_names = DAY_NAMES_I18N.get(lang, DAY_NAMES_I18N["uz"])
    for p in patterns:
        day_name = day_names.get(p["day_of_week"], str(p["day_of_week"]))
        label = f"🗑 {day_name} {p['time']}"
        cb = f"recur_del_{p['id']}"
        buttons.append([InlineKeyboardButton(label, callback_data=cb)])
    return InlineKeyboardMarkup(buttons)


# ─── Booking confirm / reject ────────────────────────

def booking_confirm_keyboard(booking_id, lang="uz"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{booking_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{booking_id}"),
        ]
    ])


# ─── Payment approve / reject ────────────────────────

def payment_approve_keyboard(booking_id, lang="uz"):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t("payment_approve_btn", lang), callback_data=f"payok_{booking_id}"),
            InlineKeyboardButton(t("payment_reject_btn", lang), callback_data=f"payno_{booking_id}"),
        ]
    ])
