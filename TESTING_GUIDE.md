# 🧪 دليل التشغيل والاختبار - AutoPublisher AI

دليل شامل لتشغيل واختبار النظام بالكامل.

---

## 📋 المتطلبات الأساسية

### 1. البرامج المطلوبة
```bash
# Docker & Docker Compose
docker --version          # يجب أن يكون 20.10+
docker-compose --version  # يجب أن يكون 1.29+

# Python (للاختبار المحلي)
python3 --version  # يجب أن يكون 3.11+

# Node.js (للـ Dashboard)
node --version     # يجب أن يكون 18+
npm --version      # يجب أن يكون 9+
```

### 2. المفاتيح المطلوبة
- ✅ OpenAI API Key (للمحتوى والصور)
- ✅ WordPress credentials (للنشر)
- ✅ Instagram credentials (للنشر)

---

## 🚀 الخطوة 1: الإعداد الأولي

### 1.1 استنساخ المشروع
```bash
git clone https://github.com/Qsweet/AutoPublisherAI.git
cd AutoPublisherAI
```

### 1.2 إنشاء ملف .env
```bash
cp .env.example .env
nano .env  # أو أي محرر نصوص
```

### 1.3 تعديل المتغيرات المطلوبة
```env
# ⚠️ يجب تغيير هذه القيم!

# Database (اختر كلمة مرور قوية)
POSTGRES_PASSWORD=your-strong-password-here

# JWT (يجب أن يكون 32 حرف على الأقل)
JWT_SECRET_KEY=your-super-secret-jwt-key-min-32-characters-long

# OpenAI (مطلوب)
OPENAI_API_KEY=sk-your-openai-api-key-here

# WordPress (اختياري للاختبار)
WORDPRESS_URL=https://your-site.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Instagram (اختياري للاختبار)
INSTAGRAM_ACCESS_TOKEN=your-instagram-token
INSTAGRAM_USER_ID=your-user-id
```

---

## 🐳 الخطوة 2: تشغيل النظام بـ Docker

### 2.1 بناء الحاويات
```bash
# بناء جميع الخدمات
docker-compose build

# أو بناء خدمة معينة
docker-compose build auth-service
```

### 2.2 تشغيل النظام
```bash
# تشغيل جميع الخدمات
docker-compose up -d

# مشاهدة الـ logs
docker-compose logs -f

# مشاهدة logs لخدمة معينة
docker-compose logs -f auth-service
```

### 2.3 التحقق من الحالة
```bash
# عرض حالة الخدمات
docker-compose ps

# يجب أن ترى:
# - postgres (Up)
# - redis (Up)
# - auth-service (Up)
# - content-service (Up)
# - publishing-service (Up)
# - orchestrator-service (Up)
# - strategy-service (Up)
# - celery-worker (Up)
# - celery-beat (Up)
# - flower (Up)
```

### 2.4 تشغيل مع Health Checks
```bash
# استخدام ملف health checks
docker-compose -f docker-compose.healthchecks.yml up -d

# مراقبة الحالة
watch docker-compose ps
```

---

## 🧪 الخطوة 3: اختبار الخدمات

### 3.1 اختبار Health Checks
```bash
# Auth Service
curl http://localhost:8005/health

# Content Service
curl http://localhost:8001/health

# Publishing Service
curl http://localhost:8002/health

# Orchestrator Service
curl http://localhost:8003/health

# Strategy Service
curl http://localhost:8004/health
```

**النتيجة المتوقعة:**
```json
{
  "status": "healthy",
  "service": "auth-service",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00Z"
}
```

### 3.2 اختبار API Documentation
افتح المتصفح وزر:
- Auth Service: http://localhost:8005/docs
- Content Service: http://localhost:8001/docs
- Publishing Service: http://localhost:8002/docs
- Orchestrator Service: http://localhost:8003/docs
- Strategy Service: http://localhost:8004/docs
- Flower (Celery): http://localhost:5555

---

## 👤 الخطوة 4: اختبار Auth Service

### 4.1 تسجيل مستخدم جديد
```bash
curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!",
    "full_name": "Test User"
  }'
```

**النتيجة المتوقعة:**
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "subscription_tier": "free",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 4.2 تسجيل الدخول
```bash
curl -X POST http://localhost:8005/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePassword123!"
  }'
```

**النتيجة المتوقعة:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**احفظ الـ access_token للاستخدام في الطلبات التالية!**

### 4.3 الحصول على معلومات المستخدم
```bash
# استبدل YOUR_TOKEN بالـ token من الخطوة السابقة
curl -X GET http://localhost:8005/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4.4 تحديث البروفايل
```bash
curl -X PUT http://localhost:8005/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name",
    "bio": "This is my bio"
  }'
```

### 4.5 الحصول على إحصائيات الاستخدام
```bash
curl -X GET http://localhost:8005/api/v1/auth/me/usage \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 الخطوة 5: اختبار Content Service

### 5.1 توليد مقال
```bash
curl -X POST http://localhost:8001/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "الذكاء الاصطناعي في التعليم",
    "language": "ar",
    "tone": "professional",
    "target_audience": "teachers",
    "keywords": ["الذكاء الاصطناعي", "التعليم", "التكنولوجيا"]
  }'
```

**النتيجة المتوقعة:**
```json
{
  "title": "الذكاء الاصطناعي: ثورة في عالم التعليم",
  "content": "...",
  "excerpt": "...",
  "featured_image_url": "https://...",
  "seo": {
    "meta_title": "...",
    "meta_description": "...",
    "keywords": ["..."],
    "slug": "..."
  },
  "faq": [
    {
      "question": "...",
      "answer": "..."
    }
  ]
}
```

### 5.2 توليد مقال (غير متزامن)
```bash
curl -X POST http://localhost:8001/api/content/generate-async \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "الذكاء الاصطناعي",
    "language": "ar"
  }'
```

**النتيجة:**
```json
{
  "task_id": "task-uuid-here",
  "status": "pending"
}
```

### 5.3 التحقق من حالة المهمة
```bash
curl -X GET http://localhost:8001/api/content/task/TASK_ID
```

---

## 📤 الخطوة 6: اختبار Publishing Service

### 6.1 النشر على WordPress
```bash
curl -X POST http://localhost:8002/api/publish \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "wordpress",
    "content": {
      "title": "عنوان المقال",
      "content": "محتوى المقال...",
      "excerpt": "ملخص المقال",
      "featured_image_url": "https://...",
      "categories": ["تقنية"],
      "tags": ["ذكاء اصطناعي"]
    },
    "credentials": {
      "url": "https://your-site.com",
      "username": "your-username",
      "app_password": "your-app-password"
    }
  }'
```

### 6.2 النشر على Instagram
```bash
curl -X POST http://localhost:8002/api/publish \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "content": {
      "caption": "نص المنشور...",
      "image_url": "https://..."
    },
    "credentials": {
      "access_token": "your-token",
      "user_id": "your-user-id"
    }
  }'
```

### 6.3 النشر الجماعي
```bash
curl -X POST http://localhost:8002/api/publish/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["wordpress", "instagram"],
    "content": {
      "title": "عنوان",
      "content": "محتوى...",
      "image_url": "https://..."
    },
    "credentials": {
      "wordpress": {...},
      "instagram": {...}
    }
  }'
```

---

## 🎯 الخطوة 7: اختبار Strategy Service

### 7.1 توليد استراتيجية محتوى
```bash
curl -X POST http://localhost:8004/api/strategy/generate \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "التكنولوجيا",
    "target_audience": "المطورين والمبرمجين",
    "goals": ["زيادة الزيارات", "بناء سلطة"],
    "duration_days": 90,
    "language": "ar"
  }'
```

**النتيجة المتوقعة:**
```json
{
  "industry": "التكنولوجيا",
  "target_audience": "المطورين والمبرمجين",
  "duration_days": 90,
  "keyword_clusters": [...],
  "content_ideas": [
    {
      "title": "...",
      "description": "...",
      "keywords": [...],
      "estimated_difficulty": "medium"
    }
  ],
  "publishing_schedule": {...},
  "traffic_projections": {...},
  "recommendations": [...]
}
```

---

## 🔄 الخطوة 8: اختبار Orchestrator Service

### 8.1 إنشاء ونشر مقال كامل
```bash
curl -X POST http://localhost:8003/api/workflow/create-and-publish \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "الذكاء الاصطناعي",
    "platforms": ["wordpress"],
    "language": "ar",
    "credentials": {
      "wordpress": {
        "url": "https://your-site.com",
        "username": "your-username",
        "app_password": "your-app-password"
      }
    }
  }'
```

### 8.2 جدولة مقال
```bash
curl -X POST http://localhost:8003/api/workflow/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "الذكاء الاصطناعي",
    "platforms": ["wordpress"],
    "scheduled_time": "2024-12-31T12:00:00Z",
    "credentials": {...}
  }'
```

### 8.3 التحقق من حالة Workflow
```bash
curl -X GET http://localhost:8003/api/workflow/WORKFLOW_ID/status
```

---

## 🖥️ الخطوة 9: تشغيل Dashboard

### 9.1 تثبيت المكتبات
```bash
cd dashboard
npm install
```

### 9.2 إنشاء ملف .env
```bash
cp .env.example .env
nano .env
```

```env
VITE_API_BASE_URL=http://localhost:8005
VITE_AUTH_SERVICE_URL=http://localhost:8005
VITE_CONTENT_SERVICE_URL=http://localhost:8001
VITE_PUBLISHING_SERVICE_URL=http://localhost:8002
VITE_ORCHESTRATOR_SERVICE_URL=http://localhost:8003
VITE_STRATEGY_SERVICE_URL=http://localhost:8004
```

### 9.3 تشغيل Dashboard
```bash
npm run dev
```

افتح المتصفح: http://localhost:5173

---

## 🧪 الخطوة 10: اختبار متكامل

### 10.1 سيناريو كامل
```bash
# 1. تسجيل مستخدم
TOKEN=$(curl -s -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test"}' \
  | jq -r '.access_token')

# 2. توليد مقال
ARTICLE=$(curl -s -X POST http://localhost:8001/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{"topic":"الذكاء الاصطناعي","language":"ar"}')

# 3. نشر المقال
curl -X POST http://localhost:8002/api/publish \
  -H "Content-Type: application/json" \
  -d "{\"platform\":\"wordpress\",\"content\":$ARTICLE,\"credentials\":{...}}"

# 4. التحقق من الاستخدام
curl -X GET http://localhost:8005/api/v1/auth/me/usage \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 الخطوة 11: مراقبة النظام

### 11.1 Flower (Celery Monitoring)
افتح: http://localhost:5555

### 11.2 Logs
```bash
# جميع الخدمات
docker-compose logs -f

# خدمة معينة
docker-compose logs -f auth-service

# آخر 100 سطر
docker-compose logs --tail=100 content-service
```

### 11.3 Database
```bash
# الاتصال بـ PostgreSQL
docker-compose exec postgres psql -U autopublisher -d autopublisher_db

# عرض الجداول
\dt

# عرض المستخدمين
SELECT * FROM users;

# الخروج
\q
```

### 11.4 Redis
```bash
# الاتصال بـ Redis
docker-compose exec redis redis-cli

# عرض المفاتيح
KEYS *

# الخروج
exit
```

---

## 🛑 إيقاف النظام

```bash
# إيقاف جميع الخدمات
docker-compose down

# إيقاف مع حذف البيانات
docker-compose down -v

# إيقاف وحذف الصور
docker-compose down --rmi all
```

---

## 🐛 حل المشاكل الشائعة

### المشكلة 1: الخدمة لا تبدأ
```bash
# فحص الـ logs
docker-compose logs service-name

# إعادة بناء الخدمة
docker-compose build --no-cache service-name
docker-compose up -d service-name
```

### المشكلة 2: خطأ في الاتصال بـ Database
```bash
# التحقق من PostgreSQL
docker-compose exec postgres pg_isready

# إعادة تشغيل PostgreSQL
docker-compose restart postgres
```

### المشكلة 3: خطأ CORS
- تأكد من إضافة URL الخاص بك في `CORS_ORIGINS` في ملف `.env`

### المشكلة 4: OpenAI API Error
- تأكد من صحة `OPENAI_API_KEY`
- تأكد من وجود رصيد في حسابك

---

## ✅ قائمة التحقق النهائية

- [ ] Docker مثبت ويعمل
- [ ] ملف `.env` تم إنشاؤه وتعديله
- [ ] OpenAI API Key صحيح
- [ ] جميع الخدمات تعمل (`docker-compose ps`)
- [ ] Health checks تعمل
- [ ] تم تسجيل مستخدم بنجاح
- [ ] تم توليد مقال بنجاح
- [ ] Dashboard يعمل
- [ ] Flower يعمل

---

## 📚 موارد إضافية

- [README.md](./README.md) - نظرة عامة على المشروع
- [DEPLOYMENT.md](./DEPLOYMENT.md) - دليل النشر على VPS
- [IMPROVEMENTS_LOG.md](./IMPROVEMENTS_LOG.md) - سجل التحسينات
- [API Documentation](http://localhost:8005/docs) - توثيق API

---

**تم! النظام جاهز للاختبار! 🎉**

