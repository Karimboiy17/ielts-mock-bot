# 🎯 IELTS ZONE Mock Exam Booking Bot

## 📊 Loyiha haqida

IELTS Zone o'quv markazi uchun **avtomatlashtirilgan mock imtihon bandlov tizimi**. Telegram bot orqali o'quvchilar o'qituvchilarning bo'sh vaqtlarini ko'rib, band qilishlari mumkin. O'qituvchi har bir so'rovni tasdiqlaydi yoki rad etadi.

---

## 🏗 Texnik Arxitektura

```
O'quvchi (Telegram)          O'qituvchi (Telegram)         Admin (Telegram)
       │                            │                           │
       └────────────────────────────┬───────────────────────────┘
                                    │
                          ┌─────────▼─────────┐
                          │   Telegram Bot     │
                          │  (python-telegram- │
                          │   bot, Railway)    │
                          └─────────┬─────────┘
                                    │
                          ┌─────────▼─────────┐
                          │    SQLite DB       │
                          │  • O'qituvchilar   │
                          │  • Slotlar         │
                          │  • Bandlovlar      │
                          │  • Doimiy pattern  │
                          └───────────────────┘
```

| Komponent | Texnologiya | Izoh |
|-----------|------------|------|
| **Bot framework** | `python-telegram-bot` v21 | Asinxron, eng so'nggi versiya |
| **Server** | Railway.app | 24/7 ishlaydi, avtomatik deploy |
| **Kod saqlash** | GitHub (`Karimboiy17/ielts-mock-bot`) | Har bir yangilanish avtomatik serverga chiqadi |
| **Ma'lumotlar bazasi** | SQLite | Tez, bepul, alohida server kerak emas |
| **Til** | O'zbek tili | To'liq o'zbekcha interfeys |

---

## 👥 Foydalanuvchi Rollari (3 xil)

| Rol | Imkoniyatlari |
|-----|--------------|
| 🎓 **O'quvchi** | Mavjud slotlarni ko'rish, band qilish so'rovi yuborish, bandlovni bekor qilish |
| 👨‍🏫 **O'qituvchi** | Bir martalik va doimiy slot qo'shish, bandlov so'rovlarini tasdiqlash/rad etish, slotlarini ko'rish |
| 👑 **Admin** | O'qituvchi qo'shish/o'chirish, barcha bandlovlarni ko'rish, to'liq nazorat |

---

## 🔄 Ish Jarayoni (Booking Flow)

```
1. Admin/O'qituvchi slot qo'shadi
         │
2. O'quvchi mavjud slotlarni ko'radi
         │
3. O'quvchi slot tanlab "Band qilish 🎯" bosadi
         │
4. Bot → O'qituvchiga xabar yuboradi:
   "❓ Karimboy 15-iyun 14:00 ga mock imtihon so'rayapti"
   [✅ Tasdiqlash] [❌ Rad etish]
         │
    ┌────┴────┐
    │         │
5a. Tasdiqlansa        5b. Rad etilsa
  O'quvchiga:           O'quvchiga:
  "✅ Tasdiqlandi!"     "❌ Rad etildi"
  Slot band qilinadi     Slot qayta ochiladi
```

---

## 🎛 Bot Imkoniyatlari

### Asosiy menyu (Reply keyboard — ekran pastida)

| Tugma | Kim ko'radi | Vazifasi |
|-------|------------|----------|
| 📋 Mavjud slotlar | Barcha | Bo'sh vaqtlarni sana bo'yicha ko'rish |
| 📅 Mening bandlovlarim | Barcha | O'z bandlovlari ro'yxati |
| ❌ Bandlovni bekor qilish | Barcha | Bandlovni o'chirish |
| ➕ Yangi slot | Admin/O'qituvchi | Bir martalik slot qo'shish (sana+vaqt tanlanadi) |
| 🔄 Doimiy slot qo'shish | Admin/O'qituvchi | Har hafta takrorlanadigan slot (masalan "har Dushanba 14:00") |
| 📋 Doimiy slotlarim | Admin/O'qituvchi | Doimiy slotlar ro'yxati + o'chirish |
| 📊 Slotlarim | Admin/O'qituvchi | Barcha slotlarni ko'rish (band/qilingan) |
| 👨‍🏫 O'qituvchi qo'shish | Admin | Yangi o'qituvchi ro'yxatdan o'tkazish |
| 📊 Barcha bandlovlar | Admin | To'liq bandlovlar hisoboti |

### Smart xususiyatlar

| Xususiyat | Tavsif |
|-----------|--------|
| 🗓 **Sana tanlash** | Bosqichma-bosqich: Avval sana, keyin vaqt tanlanadi (xato format kiritilmaydi) |
| 🔁 **Doimiy slotlar** | "Har Dushanba 14:00" — bot avtomatik 4 haftaga slot yaratadi |
| 👑 **Avtomatik o'qituvchi** | Admin birinchi slot qo'shganda avtomatik o'qituvchi bo'ladi |
| 🔒 **Ruxsat tekshiruvi** | Admin paneli faqat adminlarga, o'qituvchi funksiyalari faqat o'qituvchilarga |

---

## 💰 Xarajatlar

| Xizmat | Narx |
|--------|------|
| Railway (server) | **Bepul** (oyiga $5 kredit) |
| GitHub | **Bepul** |
| Telegram Bot API | **Bepul** |
| SQLite | **Bepul** |
| **JAMI** | **0 so'm/oy** |

---

## 📈 Afzalliklari

| Muammo (avval) | Yechim (hozir) |
|----------------|----------------|
| 📞 O'quvchilar qo'ng'iroq qilib vaqt so'rardi | Telegram'da o'zlari ko'radi |
| 📝 Admin daftarga yozardi | Barcha bandlovlar DB'da saqlanadi |
| ⏰ O'qituvchi vaqtini unutardi | Bot eslatadi / ro'yxatda ko'rinadi |
| 🤝 Chalkashliklar bo'lardi | Har bir bandlov tasdiqlash orqali |
| 🔄 O'quvchiga qayta qo'ng'iroq qilish kerak edi | Bot avtomatik javob yuboradi |

---

## 🚀 Texnik Ma'lumotlar

| Ko'rsatkich | Qiymat |
|-------------|--------|
| **Bot username** | `@ieltszonemockbot` |
| **Server joylashuvi** | Yevropa (EU West) |
| **Ish vaqti** | 24/7 (Railway har doim onlayn) |
| **Deploy usuli** | GitHub push → Railway avtomatik |
| **Kod tili** | Python 3.12 |
| **DB struktura** | 4 ta jadval: teachers, slots, bookings, recurring_patterns |

---

## 📅 Kelajakdagi Imkoniyatlar

- [ ] Google Sheets'ga avtomatik hisobot eksport qilish
- [ ] O'quvchilarga eslatma (mock imtihondan 1 kun oldin)
- [ ] To'lov integratsiyasi (Click/Payme)
- [ ] Mock natijalarini bot orqali yuborish
- [ ] IELTS Zone guruhiga qo'shish (guruh ichida ishlash)

---

*Bot 2026-iyun oyida ishlab chiqilgan. Dasturchi: Karimboy Xolmirzayev*
