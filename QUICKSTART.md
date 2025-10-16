# 🚀 دليل البدء السريع - AutoPublisherAI

هذا الدليل سيساعدك على تشغيل AutoPublisherAI في أقل من 10 دقائق!

---

## ⚡ الخطوات السريعة

### 1. المتطلبات

تأكد من تثبيت:
- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Git](https://git-scm.com/downloads)

### 2. استنساخ المشروع

```bash
git clone https://github.com/Qsweet/AutoPublisherAI.git
cd AutoPublisherAI
```

### 3. إعداد المتغيرات البيئية

```bash
# نسخ ملف المثال
cp .env.example .env

# تحرير الملف وإضافة مفتاح OpenAI
nano .env
```

**أضف على الأقل:**
```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 4. تشغيل المشروع

```bash
docker-compose up -d
```

### 5. التحقق من التشغيل

```bash
# عرض حالة الخدمات
docker-compose ps

# يجب أن ترى جميع الخدمات "Up"
```

### 6. فتح لوحة التحكم

```bash
# في نافذة طرفية جديدة
cd dashboard
python3 -m http.server 8080
```

افتح المتصفح على: **http://localhost:8080**

---

## 🎯 أول مقال لك

### عبر لوحة التحكم

1. افتح http://localhost:8080
2. في حقل "الموضوع"، اكتب: **"فوائد الذكاء الاصطناعي"**
3. اختر اللغة: **العربية**
4. حدد المنصات: **WordPress** (إذا كان لديك موقع) أو قم بإلغاء التحديد للاختبار فقط
5. انقر على **"إنشاء ونشر"**
6. شاهد التقدم في الوقت الفعلي!

### عبر API

```bash
curl -X POST http://localhost:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "content_params": {
      "topic": "فوائد الذكاء الاصطناعي",
      "language": "ar",
      "target_length": 1000,
      "seo_level": "high",
      "include_image": true,
      "include_faq": true
    },
    "publishing_targets": [],
    "auto_publish": false
  }'
```

**ملاحظة:** `publishing_targets` فارغة للاختبار فقط. المقال سيتم توليده ولكن لن يُنشر.

---

## 🔧 الإعدادات الاختيارية

### إعداد WordPress

إذا كنت تريد النشر على WordPress:

1. افتح موقع WordPress الخاص بك
2. اذهب إلى: **المستخدمون > الملف الشخصي**
3. انتقل إلى قسم **"Application Passwords"**
4. أنشئ كلمة مرور جديدة للتطبيق
5. أضف إلى `.env`:

```env
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

6. أعد تشغيل الخدمات:
```bash
docker-compose restart
```

### إعداد Instagram

لإعداد Instagram، ستحتاج إلى:

1. حساب Instagram Business
2. صفحة Facebook مرتبطة
3. Facebook App مع Instagram Graph API

**الخطوات:**

1. اذهب إلى [Facebook Developers](https://developers.facebook.com/)
2. أنشئ تطبيق جديد
3. أضف Instagram Graph API
4. احصل على Access Token و Business Account ID
5. أضف إلى `.env`:

```env
INSTAGRAM_ACCESS_TOKEN=your-long-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id
```

6. أعد تشغيل الخدمات:
```bash
docker-compose restart
```

---

## 📊 الوصول إلى الخدمات

بعد التشغيل، ستكون الخدمات متاحة على:

| الخدمة | العنوان | الوصف |
|--------|---------|-------|
| **Dashboard** | http://localhost:8080 | لوحة التحكم |
| **Orchestrator API** | http://localhost:8000 | API الرئيسي |
| **Content Service** | http://localhost:8001 | خدمة المحتوى |
| **Publishing Service** | http://localhost:8002 | خدمة النشر |
| **Flower** | http://localhost:5555 | مراقبة Celery |
| **API Docs** | http://localhost:8000/docs | توثيق API |

---

## 🐛 حل المشاكل الشائعة

### المشكلة: الخدمات لا تعمل

**الحل:**
```bash
# أوقف جميع الخدمات
docker-compose down

# احذف الحاويات القديمة
docker-compose rm -f

# أعد البناء والتشغيل
docker-compose up -d --build
```

### المشكلة: خطأ في الاتصال بـ OpenAI

**الحل:**
- تأكد من صحة `OPENAI_API_KEY` في ملف `.env`
- تحقق من رصيدك في OpenAI
- تأكد من تفعيل API في حسابك

```bash
# اختبر المفتاح
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### المشكلة: لا يمكن الوصول إلى لوحة التحكم

**الحل:**
```bash
# تأكد من أن المنفذ 8080 غير مستخدم
lsof -i :8080

# أو استخدم منفذ آخر
python3 -m http.server 9000
```

### المشكلة: Celery Worker لا يعمل

**الحل:**
```bash
# عرض سجلات Celery
docker-compose logs -f celery-worker

# إعادة تشغيل Worker
docker-compose restart celery-worker
```

---

## 📝 الأوامر المفيدة

```bash
# عرض حالة جميع الخدمات
docker-compose ps

# عرض السجلات
docker-compose logs -f

# عرض سجلات خدمة معينة
docker-compose logs -f orchestrator-service

# إيقاف جميع الخدمات
docker-compose down

# إيقاف وحذف البيانات
docker-compose down -v

# إعادة بناء خدمة معينة
docker-compose up -d --build content-service

# الدخول إلى حاوية
docker-compose exec content-service bash
```

---

## 🎓 الخطوات التالية

الآن بعد أن أصبح لديك AutoPublisherAI يعمل:

1. **اقرأ التوثيق الكامل** - [README.md](README.md)
2. **جرّب الميزات المتقدمة** - جدولة، نشر جماعي
3. **أضف منصات جديدة** - Facebook، X، LinkedIn
4. **ساهم في المشروع** - [CONTRIBUTING.md](CONTRIBUTING.md)

---

## 💡 نصائح

- **استخدم GPT-4 Turbo** للحصول على أفضل نتائج
- **اضبط `target_length`** حسب احتياجاتك (300-5000 كلمة)
- **جرّب مستويات SEO المختلفة** لمعرفة الأنسب لك
- **راقب Flower** لمتابعة أداء المهام
- **احفظ المقالات المهمة** قبل النشر للمراجعة

---

## 🆘 تحتاج مساعدة؟

- **GitHub Issues**: [إنشاء مشكلة](https://github.com/Qsweet/AutoPublisherAI/issues)
- **التوثيق الكامل**: [README.md](README.md)
- **دليل المساهمة**: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**مبروك! 🎉 أنت الآن جاهز لاستخدام AutoPublisherAI!**

