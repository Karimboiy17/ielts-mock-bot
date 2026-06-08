"""i18n — trilingual support (uz/en/ru)."""

LANGS = {"🇺🇿 O'zbekcha": "uz", "🇬🇧 English": "en", "🇷🇺 Русский": "ru"}
LANG_BY_CODE = {v: k for k, v in LANGS.items()}

LANG_NAMES = {"uz": "🇺🇿 O'zbekcha", "en": "🇬🇧 English", "ru": "🇷🇺 Русский"}
FALLBACK = "uz"

# ─── All translatable strings ─────────────────────────────
T = {
    # Language selection
    "choose_lang": {
        "uz": "🇺🇿 Tilni tanlang:\n🇬🇧 Choose language:\n🇷🇺 Выберите язык:",
        "en": "Choose your language:",
        "ru": "Выберите язык:",
    },
    "lang_set": {
        "uz": "✅ Til o'zbekcha qilindi! /start ni bosing.",
        "en": "✅ Language set to English! Press /start.",
        "ru": "✅ Язык установлен на русский! Нажмите /start.",
    },

    # Start / welcome
    "welcome_title": {
        "uz": "🎓 *IELTS Zone \\| Mock Imtihon Bandlov Boti*",
        "en": "🎓 *IELTS Zone \\| Mock Exam Booking Bot*",
        "ru": "🎓 *IELTS Zone \\| Бот для записи на Mock Экзамен*",
    },
    "welcome_desc": {
        "uz": "Mock imtihon uchun o'qituvchidan vaqt band qilish tizimi\\.",
        "en": "Book a time slot with a teacher for your mock exam\\.",
        "ru": "Забронируйте время у преподавателя для пробного экзамена\\.",
    },
    "welcome_how": {
        "uz": "📌 *Qanday ishlaydi:*",
        "en": "📌 *How it works:*",
        "ru": "📌 *Как это работает:*",
    },
    "welcome_step1": {
        "uz": "1\\. \"Mavjud slotlar\" — bo'sh vaqtlarni ko'ring",
        "en": "1\\. \"Available Slots\" — see open times",
        "ru": "1\\. \"Свободные слоты\" — посмотрите доступное время",
    },
    "welcome_step2": {
        "uz": "2\\. Kerakli vaqtni tanlang — to'lov chekini yuboring",
        "en": "2\\. Pick a time — send payment receipt",
        "ru": "2\\. Выберите время — отправьте чек об оплате",
    },
    "welcome_step3": {
        "uz": "3\\. Admin tasdiqlasa — bandlov tayyor ✅",
        "en": "3\\. Admin approves — booking confirmed ✅",
        "ru": "3\\. Админ подтвердит — бронь готова ✅",
    },
    "welcome_step4": {
        "uz": "4\\. \"Mening bandlovlarim\" — bandlovlaringizni ko'ring",
        "en": "4\\. \"My Bookings\" — view your bookings",
        "ru": "4\\. \"Мои брони\" — посмотрите свои записи",
    },
    "welcome_step5": {
        "uz": "5\\. \"Bandlovni bekor qilish\" — kerak bo'lsa bekor qiling",
        "en": "5\\. \"Cancel Booking\" — cancel if needed",
        "ru": "5\\. \"Отменить бронь\" — отмените при необходимости",
    },

    # Admin welcome
    "admin_welcome_title": {
        "uz": "👑 *Admin Panel*",
        "en": "👑 *Admin Panel*",
        "ru": "👑 *Админ-панель*",
    },
    "admin_welcome_desc": {
        "uz": "Siz admin huquqlariga egasiz\\.",
        "en": "You have admin privileges\\.",
        "ru": "У вас есть права администратора\\.",
    },
    "admin_welcome_menu": {
        "uz": "*Menyu:*\n• Yangi slot qo'shish\n• Doimiy slotlar\n• O'qituvchilarni boshqarish\n• Bandlovlarni ko'rish\n• To'lov cheklarini tasdiqlash",
        "en": "*Menu:*\n• Add new slots\n• Recurring slots\n• Manage teachers\n• View bookings\n• Approve payments",
        "ru": "*Меню:*\n• Добавить слоты\n• Повторяющиеся слоты\n• Управление учителями\n• Просмотр броней\n• Подтверждение оплат",
    },

    # Teacher welcome
    "teacher_welcome_title": {
        "uz": "👨‍🏫 *O'qituvchi Panel*",
        "en": "👨‍🏫 *Teacher Panel*",
        "ru": "👨‍🏫 *Панель учителя*",
    },
    "teacher_welcome_desc": {
        "uz": "Slotlaringizni boshqaring va bandlovlarni tasdiqlang\\.",
        "en": "Manage your slots and approve bookings\\.",
        "ru": "Управляйте своими слотами и подтверждайте брони\\.",
    },

    # Menus — student
    "menu_slots": {"uz": "📋 Mavjud slotlar", "en": "📋 Available Slots", "ru": "📋 Свободные слоты"},
    "menu_mybookings": {"uz": "📅 Mening bandlovlarim", "en": "📅 My Bookings", "ru": "📅 Мои брони"},
    "menu_cancel": {"uz": "❌ Bandlovni bekor qilish", "en": "❌ Cancel Booking", "ru": "❌ Отменить бронь"},

    # Menus — admin / teacher
    "menu_newslot": {"uz": "➕ Yangi slot", "en": "➕ New Slot", "ru": "➕ Новый слот"},
    "menu_myslots": {"uz": "📊 Slotlarim", "en": "📊 My Slots", "ru": "📊 Мои слоты"},
    "menu_recurring": {"uz": "🔄 Doimiy slot", "en": "🔄 Recurring Slot", "ru": "🔄 Повтор. слот"},
    "menu_myrecurring": {"uz": "📋 Doimiy slotlarim", "en": "📋 My Recurring", "ru": "📋 Мои повтор."},
    "menu_addteacher": {"uz": "👨‍🏫 O'qituvchi qo'shish", "en": "👨‍🏫 Add Teacher", "ru": "👨‍🏫 Добавить учителя"},
    "menu_teachers": {"uz": "👥 O'qituvchilar", "en": "👥 Teachers", "ru": "👥 Учителя"},
    "menu_all_bookings": {"uz": "📊 Barcha bandlovlar", "en": "📊 All Bookings", "ru": "📊 Все брони"},
    "menu_pending_payments": {"uz": "💳 To'lov tasdiqlash", "en": "💳 Approve Payments", "ru": "💳 Подтвердить оплату"},
    "menu_checksearch": {"uz": "🔍 Chek qidirish", "en": "🔍 Find Checks", "ru": "🔍 Поиск чеков"},

    # Slot picking
    "pick_date": {"uz": "📅 *Slot sanasini tanlang:*", "en": "📅 *Pick a date:*", "ru": "📅 *Выберите дату:*"},
    "pick_time": {"uz": "🕐 *{date} — vaqtni tanlang:*", "en": "🕐 *{date} — pick a time:*", "ru": "🕐 *{date} — выберите время:*"},
    "slot_added": {
        "uz": "✅ *Slot qo'shildi!*\n\n📅 Sana: {date}\n🕐 Vaqt: {time}",
        "en": "✅ *Slot added!*\n\n📅 Date: {date}\n🕐 Time: {time}",
        "ru": "✅ *Слот добавлен!*\n\n📅 Дата: {date}\n🕐 Время: {time}",
    },
    "add_more": {
        "uz": "Yana slot qo'shasizmi?",
        "en": "Add another slot?",
        "ru": "Добавить еще слот?",
    },
    "no_times_selected": {
        "uz": "Hech qanday vaqt tanlanmadi!",
        "en": "No times selected!",
        "ru": "Время не выбрано!",
    },
    "slots_added": {
        "uz": "✅ {count} ta slot qo'shildi: {date}",
        "en": "✅ {count} slots added: {date}",
        "ru": "✅ Добавлено {count} слотов: {date}",
    },
    "yes_add_more": {
        "uz": "Ha, yana qo'shish",
        "en": "Yes, add more",
        "ru": "Да, добавить",
    },
    "no_back": {
        "uz": "Yo'q, menyuga",
        "en": "No, back to menu",
        "ru": "Нет, в меню",
    },
    "no_slots": {
        "uz": "📭 Hozircha slotlar yo'q.",
        "en": "📭 No slots yet.",
        "ru": "📭 Пока нет слотов.",
    },
    "your_slots": {
        "uz": "*📊 Slotlaringiz:*\\n\\n",
        "en": "*📊 Your Slots:*\\n\\n",
        "ru": "*📊 Ваши слоты:*\\n\\n",
    },

    # Recurring
    "pick_day": {
        "uz": "📅 *Doimiy slot uchun kunni tanlang:*",
        "en": "📅 *Pick day for recurring slot:*",
        "ru": "📅 *Выберите день для повтор. слота:*",
    },
    "recurring_added": {
        "uz": "✅ *Doimiy slot qo'shildi!*\\n\\n📅 Har hafta: {day}\\n🕐 Vaqt: {time}\\n📊 {count} ta yangi slot yaratildi (4 haftaga)",
        "en": "✅ *Recurring slot added!*\\n\\n📅 Every: {day}\\n🕐 Time: {time}\\n📊 {count} new slots created (4 weeks)",
        "ru": "✅ *Повтор. слот добавлен!*\\n\\n📅 Каждую неделю: {day}\\n🕐 Время: {time}\\n📊 {count} новых слотов создано (4 недели)",
    },
    "no_recurring": {
        "uz": "📭 Hozircha doimiy slotlar yo'q.",
        "en": "📭 No recurring slots yet.",
        "ru": "📭 Пока нет повторяющихся слотов.",
    },
    "recurring_title": {
        "uz": "*📋 Doimiy slotlaringiz:*\\n\\n",
        "en": "*📋 Your Recurring Slots:*\\n\\n",
        "ru": "*📋 Ваши повтор. слоты:*\\n\\n",
    },
    "recurring_delete_hint": {
        "uz": "\\n\\n🗑 O'chirish uchun pastdagi slotni bosing:",
        "en": "\\n\\n🗑 Click a slot below to delete:",
        "ru": "\\n\\n🗑 Нажмите на слот ниже, чтобы удалить:",
    },
    "recurring_deleted": {
        "uz": "🗑 *Doimiy slot o'chirildi!*",
        "en": "🗑 *Recurring slot deleted!*",
        "ru": "🗑 *Повтор. слот удалён!*",
    },

    # Bookings
    "booking_success": {
        "uz": "✅ *So'rov yuborildi!*\\n\\n📅 {date} {time}\\n👨‍🏫 O'qituvchi: {teacher}\\n\\n⏳ O'qituvchi tasdiqlashini kuting.",
        "en": "✅ *Request sent!*\\n\\n📅 {date} {time}\\n👨‍🏫 Teacher: {teacher}\\n\\n⏳ Waiting for approval.",
        "ru": "✅ *Запрос отправлен!*\\n\\n📅 {date} {time}\\n👨‍🏫 Учитель: {teacher}\\n\\n⏳ Ожидайте подтверждения.",
    },
    "booking_confirmed_student": {
        "uz": "✅ *Bandlovingiz tasdiqlandi!*\\n\\n📅 {date} {time}\\n👨‍🏫 O'qituvchi: {teacher}",
        "en": "✅ *Your booking is confirmed!*\\n\\n📅 {date} {time}\\n👨‍🏫 Teacher: {teacher}",
        "ru": "✅ *Ваша бронь подтверждена!*\\n\\n📅 {date} {time}\\n👨‍🏫 Учитель: {teacher}",
    },
    "booking_rejected_student": {
        "uz": "❌ *Bandlovingiz rad etildi.*\\n\\n📅 {date} {time}\\n👨‍🏫 O'qituvchi: {teacher}\\n\\nBoshqa vaqt tanlang.",
        "en": "❌ *Your booking was rejected.*\\n\\n📅 {date} {time}\\n👨‍🏫 Teacher: {teacher}\\n\\nPlease pick another time.",
        "ru": "❌ *Ваша бронь отклонена.*\\n\\n📅 {date} {time}\\n👨‍🏫 Учитель: {teacher}\\n\\nВыберите другое время.",
    },
    "no_bookings": {
        "uz": "📭 Sizda hozircha bandlov yo'q.",
        "en": "📭 You have no bookings yet.",
        "ru": "📭 У вас пока нет броней.",
    },
    "your_bookings": {
        "uz": "*📅 Sizning bandlovlaringiz:*\\n\\n",
        "en": "*📅 Your Bookings:*\\n\\n",
        "ru": "*📅 Ваши брони:*\\n\\n",
    },
    "booking_cancelled": {
        "uz": "🗑 Bandlov bekor qilindi.",
        "en": "🗑 Booking cancelled.",
        "ru": "🗑 Бронь отменена.",
    },
    "no_bookings_to_cancel": {
        "uz": "📭 Bekor qilish uchun bandlov yo'q.",
        "en": "📭 No bookings to cancel.",
        "ru": "📭 Нет броней для отмены.",
    },
    "all_bookings_title": {
        "uz": "*📊 Barcha bandlovlar:*\\n\\n",
        "en": "*📊 All Bookings:*\\n\\n",
        "ru": "*📊 Все брони:*\\n\\n",
    },
    "no_bookings_admin": {
        "uz": "📭 Hozircha hech qanday bandlov yo'q.",
        "en": "📭 No bookings yet.",
        "ru": "📭 Пока нет броней.",
    },
    "all_teachers_title": {
        "uz": "*👥 Ro'yxatdagi o'qituvchilar:*\\n\\n",
        "en": "*👥 Registered Teachers:*\\n\\n",
        "ru": "*👥 Зарегистрированные учителя:*\\n\\n",
    },
    "no_teachers": {
        "uz": "📭 Hozircha o'qituvchilar yo'q.",
        "en": "📭 No teachers yet.",
        "ru": "📭 Пока нет учителей.",
    },

    # Payment
    "payment_required": {
        "uz": "💳 *To'lov talab qilinadi*\\n\\n📅 {date} {time}\\n👨‍🏫 O'qituvchi: {teacher}\\n\\n📸 Iltimos, to'lov chekini (skrinshot) yuboring\\.",
        "en": "💳 *Payment Required*\\n\\n📅 {date} {time}\\n👨‍🏫 Teacher: {teacher}\\n\\n📸 Please send the payment receipt (screenshot)\\.",
        "ru": "💳 *Требуется оплата*\\n\\n📅 {date} {time}\\n👨‍🏫 Учитель: {teacher}\\n\\n📸 Пожалуйста, отправьте чек об оплате (скриншот)\\.",
    },
    "payment_received": {
        "uz": "📸 *Chek qabul qilindi!* Admin tasdiqlashini kuting ⏳",
        "en": "📸 *Receipt received!* Waiting for admin approval ⏳",
        "ru": "📸 *Чек получен!* Ожидайте подтверждения админа ⏳",
    },
    "payment_approve_student": {
        "uz": "✅ *To'lovingiz tasdiqlandi!* Bandlovingiz faollashtirildi\\.",
        "en": "✅ *Payment approved!* Your booking is now active\\.",
        "ru": "✅ *Оплата подтверждена!* Ваша бронь активирована\\.",
    },
    "payment_reject_student": {
        "uz": "❌ *To'lovingiz rad etildi.* Iltimos, to'g'ri chek yuboring yoki boshqa vaqt tanlang\\.",
        "en": "❌ *Payment rejected.* Please send a correct receipt or choose another time\\.",
        "ru": "❌ *Оплата отклонена.* Пожалуйста, отправьте правильный чек или выберите другое время\\.",
    },
    "payment_approve_admin": {
        "uz": "💳 *Yangi to'lov cheki*\\n\\n👤 O'quvchi: {student}\\n📅 {date} {time}\\n👨‍🏫 O'qituvchi: {teacher}",
        "en": "💳 *New Payment Receipt*\\n\\n👤 Student: {student}\\n📅 {date} {time}\\n👨‍🏫 Teacher: {teacher}",
        "ru": "💳 *Новый чек об оплате*\\n\\n👤 Студент: {student}\\n📅 {date} {time}\\n👨‍🏫 Учитель: {teacher}",
    },
    "payment_approve_btn": {"uz": "✅ Tasdiqlash", "en": "✅ Approve", "ru": "✅ Подтвердить"},
    "payment_reject_btn": {"uz": "❌ Rad etish", "en": "❌ Reject", "ru": "❌ Отклонить"},
    "no_good": {
        "uz": "⚠️ To'lov uchun avval slot tanlang\\.",
        "en": "⚠️ Please pick a slot first before sending payment\\.",
        "ru": "⚠️ Сначала выберите слот для оплаты\\.",
    },

    # General
    "admin_only": {
        "uz": "⛔ Admin huquqi kerak.",
        "en": "⛔ Admin only.",
        "ru": "⛔ Только для админа.",
    },
    "teacher_only": {
        "uz": "⛔ O'qituvchi huquqi kerak.",
        "en": "⛔ Teacher only.",
        "ru": "⛔ Только для учителя.",
    },
    "added_teacher": {
        "uz": "👨‍🏫 O'qituvchi qo'shildi\\!",
        "en": "👨‍🏫 Teacher added\\!",
        "ru": "👨‍🏫 Учитель добавлен\\!",
    },
    "same_month": {"uz": "Shu oy", "en": "This month", "ru": "Текущий месяц"},
    "next_month": {"uz": "Keyingi oy", "en": "Next month", "ru": "След. месяц"},

    # Status
    "status_available": {"uz": "Bo'sh", "en": "Available", "ru": "Свободно"},
    "status_pending": {"uz": "Kutilmoqda", "en": "Pending", "ru": "Ожидает"},
    "status_booked": {"uz": "Band", "en": "Booked", "ru": "Занято"},
    "status_rejected": {"uz": "Rad etilgan", "en": "Rejected", "ru": "Отклонено"},
    "status_accepted": {"uz": "Tasdiqlangan", "en": "Accepted", "ru": "Принято"},
    "status_payment_pending": {"uz": "To'lov kutilmoqda", "en": "Payment Pending", "ru": "Ожидает оплаты"},
    "status_info": {
        "uz": "⏳ band, ✅ tasdiqlangan, ❌ rad etilgan, 🟢 bo'sh",
        "en": "⏳ pending, ✅ accepted, ❌ rejected, 🟢 available",
        "ru": "⏳ ожидает, ✅ принято, ❌ отклонено, 🟢 свободно",
    },
    "click_to_book": {
        "uz": "Band qilish uchun slotni tanlang:",
        "en": "Select a slot to book:",
        "ru": "Выберите слот для бронирования:",
    },

    # Cancel
    "cancel_prompt": {
        "uz": "Bekor qilish uchun bandlov ID sini tanlang:",
        "en": "Select booking ID to cancel:",
        "ru": "Выберите ID брони для отмены:",
    },
    "booking_item": {
        "uz": "/cancel\\_{id} — {date} {time} ({teacher}) [{status}]",
        "en": "/cancel\\_{id} — {date} {time} ({teacher}) [{status}]",
        "ru": "/cancel\\_{id} — {date} {time} ({teacher}) [{status}]",
    },
    "cancel_usage": {
        "uz": "Bekor qilish uchun yuqoridagi ID ni bosing yoki `/cancel ID` yozing.",
        "en": "Click the ID above or type `/cancel ID` to cancel.",
        "ru": "Нажмите ID выше или введите `/cancel ID` для отмены.",
    },

    # Sync status
    "sheets_sync_ok": {
        "uz": "✅ Google Sheets'dan {t} ta o'qituvchi, {s} ta slot yuklandi.",
        "en": "✅ Loaded {t} teachers, {s} slots from Google Sheets.",
        "ru": "✅ Загружено {t} учителей, {s} слотов из Google Sheets.",
    },
    "sheets_sync_fail": {
        "uz": "⚠️ Google Sheets ulanishda xato: {err}",
        "en": "⚠️ Google Sheets connection error: {err}",
        "ru": "⚠️ Ошибка подключения к Google Sheets: {err}",
    },
}

STATUS_MAP = {
    "available": {"uz": "🟢 Bo'sh", "en": "🟢 Free", "ru": "🟢 Свободно"},
    "pending": {"uz": "⏳ Kutish", "en": "⏳ Pending", "ru": "⏳ Ожидает"},
    "booked": {"uz": "🔴 Band", "en": "🔴 Booked", "ru": "🔴 Занято"},
    "accepted": {"uz": "✅ Tasdiqlangan", "en": "✅ Confirmed", "ru": "✅ Подтверждено"},
    "rejected": {"uz": "❌ Rad etilgan", "en": "❌ Rejected", "ru": "❌ Отклонено"},
}

PAYMENT_STATUS_ICON = {
    "payment_submitted": "💳",
    "payment_approved": "✅",
    "payment_rejected": "❌",
    "pending": "⏳",
}


def get_lang(context) -> str:
    """Get user's language from context or user_data, fallback to uz."""
    if context and context.user_data:
        lang = context.user_data.get("lang")
        if lang in LANGS.values():
            return lang
    return FALLBACK


def t(key: str, lang: str = None, **kwargs) -> str:
    """Translate a key. Use lang param or fallback."""
    lang = lang or FALLBACK
    if lang not in LANGS.values():
        lang = FALLBACK
    entry = T.get(key, {})
    text = entry.get(lang) or entry.get(FALLBACK, key)
    if kwargs:
        text = text.format(**kwargs)
    return text
