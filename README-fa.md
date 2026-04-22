<h1 align="center"/>sadWatcher</h1>

<p align="center">
 <a href="./README.md">
 English
 </a>
 /
 <a href="./README-fa.md">
 فارسی
 </a>
</p>

---

**سدواچر** یه اسکریپت سبکه که ترافیک یوزرهای پنل [Rebecca](https://github.com/rebeccapanel/Rebecca) یا [Marzban](https://github.com/Gozargah/Marzban) یا [PasarGuard](https://github.com/PasarGuard/panel) رو لحظه‌به‌لحظه چک می‌کنه. و فوری کانکشن‌های فعال کاربران محدود شده رو قطع می‌کنه.

---

## چرا sadWatcher؟

پنل ها خودشون یوزرهای پر‌حجم رو توی دیتابیس disabled می‌کنن، ولی کانکشن‌های فعال تا ری‌استارت بعدی xray قطع نمی‌شن. سدواچر این کانکشن‌ها رو ظرف چند ثانیه می‌بنده، بدون اینکه نیازی به ری‌استارت کل پنل باشه.

پشتیبانی می‌کند از:
- Rebecca
- Marzban
- PasarGuard

مسیرهای پیش‌فرض دیتابیس:
- Rebecca: `/var/lib/rebecca/db.sqlite3`
- Marzban: `/var/lib/marzban/db.sqlite3`
- PasarGuard: `/var/lib/pasarguard/db.sqlite3`

---

## نحوه کار

1. هر N ثانیه دیتابیس SQLite رو می‌خونه
2. یوزرهایی که `used_traffic > data_limit` دارن رو پیدا می‌کنه
3. با ss پورت هایی که کانفیگ فعال دارین رو کیل میکنه
4. همه چیز رو لاگ می‌کنه

---

## نصب

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/horamsafaryani/sadWatcher/latest/install.sh)"
```

اینستالر این سوالا رو ازت می‌پرسه:
- مسیر دیتابیس SQLite پنل
- پورت‌های xray که باید واچ بشن
- فاصله بین هر چک (ثانیه)
- سطح لاگ

---

## تنظیمات

فایل config در `/var/lib/sadWatcher/.env` قرار داره:

| متغیر | پیش‌فرض | توضیح |
|---|---|---|
| `DB_PATH` | `/var/lib/rebecca/db.sqlite3` | مسیر دیتابیس (Rebecca / Marzban / PasarGuard) |
| `CHECK_INTERVAL` | `5` | فاصله بین هر چک (ثانیه) |
| `BOUNCE_PORTS` | `8080,8880` | پورت‌های xray (با کاما جدا کن) |
| `LOG_FILE` | `/var/lib/sadWatcher/sadWatcher.log` | مسیر فایل لاگ |
| `LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR |

بعد از ویرایش `.env` سرویس رو ری‌استارت کن:
```bash
systemctl restart sadWatcher
```

---

## دستورات مفید

```bash
systemctl status sadWatcher                      # وضعیت سرویس
journalctl -fu sadWatcher                        # لاگ زنده
tail -f /var/lib/sadWatcher/sadWatcher.log       # فایل لاگ
```

---

## حذف نصب کامل

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/horamsafaryani/sadWatcher/latest/install.sh)" -- uninstall
```

---

## پیش‌نیازها

- لینوکس با `ss` (iproute2) — هر distro مدرن
- دسترسی root (برای `ss -K` لازمه)
- پنل Rebecca یا Marzban یا PasarGuard با دیتابیس SQLite


---

## لایسنس

MIT
