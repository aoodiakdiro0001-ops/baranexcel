# 🧹 منظف ملفات Excel/CSV — by Baran Avisat

ينظف ملفاتك الفوضوية بضغطة واحدة: يحذف الفارغ والمكرر، يوحد الأرقام
(1,200 ← 1200)، يقرأ كل الترميزات العربية (cp1256)، ويخرج ملفاً منسقاً
مع ورقة ملخص — `baraniplog`-style credit: Baran Avisat · baranavisat@gmail.com

## التشغيل

```bash
pip install -r requirements.txt
python3 clean.py ملفك.csv -o ./نظيف
python3 clean.py a.xlsx b.csv -o ./نظيف   # عدة ملفات
```

## بوت تلجرام مدفوع (bot.py)

يستقبل الملفات ويرجعها نظيفة خلال ثوانٍ: أول 3 مجاناً، ثم 10 ملفات
لكل 5$ USDT (المستخدم يدفع ويرسل `/paid رقم_العملية`، وأنت توافق
بـ `/approve user_id` من حسابك).

```bash
cp .env.example .env   # ضع توكن بوت جديد + ADMIN_ID (لا يُنشر أبداً)
python3 bot.py         # يعمل على جهازك، بلا استضافة
```

### تشغيل دائم على Mac (launchd — يعمل 24/7 ويعود بعد إعادة التشغيل)

```bash
# أنشئ ~/Library/LaunchAgents/com.baran.cleanerbot.plist يشغّل:
# python3 -u /path/to/baranexcel/cleaner/bot.py
launchctl load ~/Library/LaunchAgents/com.baran.cleanerbot.plist
tail -f /tmp/cleanerbot.log     # المراقبة
launchctl unload ~/Library/LaunchAgents/com.baran.cleanerbot.plist  # للإيقاف
```

## ماذا يفعل
- أعمدة/صفوف فارغة تماماً ← حذف
- مسافات زائدة + أعمدة مكررة الاسم ← إصلاح
- أرقام بفواصل آلاف ← أرقام حقيقية **قبل** كشف التكرار
- إخراج: ورقة `البيانات` (ترويسة ملونة + تجميد) + ورقة `ملخص` بالإحصائيات
- ملفات `.xls` القديمة تحتاج `pip install xlrd` أو التحويل لـ `.xlsx`
