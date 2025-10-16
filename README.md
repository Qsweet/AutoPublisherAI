# AutoPublisherAI

<div align="center">

![AutoPublisherAI Logo](https://img.shields.io/badge/AutoPublisherAI-v1.0.0-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal?style=for-the-badge&logo=fastapi)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?style=for-the-badge&logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**منصة احترافية لتوليد المحتوى ونشره تلقائياً باستخدام الذكاء الاصطناعي**

[التثبيت](#-التثبيت-والتشغيل) •
[الاستخدام](#-الاستخدام) •
[التوثيق](#-التوثيق) •
[المساهمة](#-المساهمة)

</div>

---

## 📋 نظرة عامة

**AutoPublisherAI** هي منصة متكاملة تستخدم الذكاء الاصطناعي لتوليد محتوى احترافي ونشره تلقائياً على منصات متعددة. تم بناؤها باستخدام **بنية الخدمات المصغرة (Microservices Architecture)** لتكون قابلة للتطوير والصيانة.

### ✨ المميزات الرئيسية

- 🤖 **توليد محتوى ذكي** - استخدام GPT-4 لإنشاء مقالات احترافية
- 🎨 **توليد صور** - إنشاء صور مميزة باستخدام DALL-E 3
- 🔍 **تحسين SEO متقدم** - تحليل وتحسين المحتوى لمحركات البحث
- 📱 **نشر متعدد المنصات** - WordPress، Instagram، وأكثر
- ⚡ **معالجة خلفية** - استخدام Celery لمعالجة المهام بشكل غير متزامن
- 📊 **لوحة تحكم عربية** - واجهة ويب حديثة وسهلة الاستخدام
- 🔄 **جدولة ذكية** - نشر المحتوى في أوقات محددة
- 🏗️ **بنية قابلة للتطوير** - إضافة منصات جديدة بسهولة
- 🐳 **Docker-Ready** - تشغيل سريع باستخدام Docker Compose
- 📈 **مراقبة شاملة** - Flower لمراقبة المهام

---

## 🏗️ البنية المعمارية

AutoPublisherAI مبني على **بنية الخدمات المصغرة** مع فصل كامل للمسؤوليات:

```
┌─────────────────────────────────────────────────────────────┐
│                     Dashboard (Frontend)                     │
│                   Tailwind CSS + Vanilla JS                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator Service (FastAPI)                  │
│          Workflow Coordination & Task Management             │
└──────┬──────────────────────┬──────────────────────┬────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────────┐
│  Content    │      │ Publishing  │      │  Celery Worker  │
│  Service    │      │  Service    │      │  + Beat + Flower│
│  (FastAPI)  │      │  (FastAPI)  │      │  (Background)   │
└─────────────┘      └─────────────┘      └─────────────────┘
       │                      │                      │
       ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Layer                            │
│     PostgreSQL (DB) + Redis (Cache & Queue)                 │
└─────────────────────────────────────────────────────────────┘
```

### الخدمات

#### 1. **Content Service** (خدمة توليد المحتوى)
- تحليل SEO متقدم
- توليد مقالات باستخدام GPT-4
- توليد صور باستخدام DALL-E 3
- إنشاء أقسام FAQ
- استخراج الكلمات المفتاحية

#### 2. **Publishing Service** (خدمة النشر)
- نظام إضافات قابل للتوسع (Plugin System)
- دعم WordPress (REST API)
- دعم Instagram (Graph API)
- جاهز لإضافة Facebook، X، LinkedIn
- إعادة محاولة تلقائية عند الفشل

#### 3. **Orchestrator Service** (خدمة التنسيق)
- تنسيق العمليات بين الخدمات
- إدارة المهام الخلفية (Celery)
- جدولة المهام (Celery Beat)
- تتبع حالة العمليات
- دعم العمليات الجماعية

#### 4. **Dashboard** (لوحة التحكم)
- واجهة عربية كاملة (RTL)
- تصميم حديث باستخدام Tailwind CSS
- تتبع لحظي للمهام
- إحصائيات شاملة
- إعدادات سهلة

---

## 🚀 التثبيت والتشغيل

### المتطلبات الأساسية

- Docker و Docker Compose
- OpenAI API Key
- (اختياري) حساب WordPress
- (اختياري) حساب Instagram Business

### خطوات التثبيت

#### 1. استنساخ المشروع

```bash
git clone https://github.com/Qsweet/AutoPublisherAI.git
cd AutoPublisherAI
```

#### 2. إعداد المتغيرات البيئية

```bash
cp .env.example .env
nano .env  # أو استخدم محرر نصوص آخر
```

**المتغيرات المطلوبة:**

```env
# OpenAI Configuration (مطلوب)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4
OPENAI_IMAGE_MODEL=dall-e-3

# WordPress Configuration (اختياري)
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your-username
WORDPRESS_APP_PASSWORD=your-app-password

# Instagram Configuration (اختياري)
INSTAGRAM_ACCESS_TOKEN=your-access-token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your-account-id

# Database Configuration
POSTGRES_USER=autopublisher
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=autopublisher_db
```

#### 3. تشغيل المشروع

```bash
# تشغيل جميع الخدمات
docker-compose up -d

# متابعة السجلات
docker-compose logs -f
```

#### 4. التحقق من التشغيل

```bash
# التحقق من حالة الخدمات
docker-compose ps

# يجب أن ترى:
# - content-service (Port 8001)
# - publishing-service (Port 8002)
# - orchestrator-service (Port 8000)
# - celery-worker
# - celery-beat
# - flower (Port 5555)
# - postgres (Port 5432)
# - redis (Port 6379)
```

#### 5. فتح لوحة التحكم

```bash
# تشغيل خادم ويب محلي للوحة التحكم
cd dashboard
python3 -m http.server 8080
```

افتح المتصفح على: **http://localhost:8080**

---

## 📖 الاستخدام

### عبر لوحة التحكم (موصى به)

1. افتح لوحة التحكم في المتصفح
2. أدخل موضوع المقال
3. اختر الإعدادات (اللغة، عدد الكلمات، مستوى SEO)
4. حدد المنصات للنشر
5. انقر على "إنشاء ونشر"
6. تابع التقدم في الوقت الفعلي

### عبر API

#### إنشاء ونشر مقال

```bash
curl -X POST http://localhost:8000/api/v1/workflow/execute \
  -H "Content-Type: application/json" \
  -d '{
    "content_params": {
      "topic": "فوائد العمل عن بعد للشركات الناشئة",
      "language": "ar",
      "target_length": 1500,
      "seo_level": "high",
      "include_image": true,
      "include_faq": true
    },
    "publishing_targets": [
      {
        "platform": "wordpress",
        "post_status": "publish"
      },
      {
        "platform": "instagram"
      }
    ],
    "auto_publish": true
  }'
```

#### التحقق من حالة المهمة

```bash
curl http://localhost:8000/api/v1/workflow/status/{workflow_id}
```

---

## 🔧 التكوين المتقدم

### إضافة منصة نشر جديدة

1. أنشئ ملف جديد في `services/publishing-service/app/publishers/`
2. ورّث من `BasePublisher`
3. نفّذ الدوال المطلوبة
4. أضف المنصة إلى `PublisherFactory`

مثال:

```python
# services/publishing-service/app/publishers/facebook.py
from app.publishers.base import BasePublisher

class FacebookPublisher(BasePublisher):
    def publish(self, content, config):
        # تنفيذ النشر على Facebook
        pass
```

---

## 📊 المراقبة والصيانة

### Flower Dashboard (مراقبة Celery)

افتح: **http://localhost:5555**

- عرض المهام النشطة
- إحصائيات الأداء
- سجلات المهام
- إعادة تشغيل المهام الفاشلة

### قاعدة البيانات

```bash
# الاتصال بقاعدة البيانات
docker-compose exec postgres psql -U autopublisher -d autopublisher_db
```

### السجلات

```bash
# عرض سجلات خدمة معينة
docker-compose logs -f content-service
docker-compose logs -f publishing-service
docker-compose logs -f orchestrator-service
docker-compose logs -f celery-worker
```

---

## 🛠️ التقنيات المستخدمة

### Backend
- **Python 3.11** - لغة البرمجة
- **FastAPI** - إطار عمل API
- **Celery** - معالجة المهام الخلفية
- **Redis** - طابور المهام والذاكرة المؤقتة
- **PostgreSQL** - قاعدة البيانات
- **SQLAlchemy** - ORM
- **Pydantic** - التحقق من البيانات
- **Docker** - الحاويات

### AI & APIs
- **OpenAI GPT-4** - توليد المحتوى
- **DALL-E 3** - توليد الصور
- **WordPress REST API** - النشر على WordPress
- **Instagram Graph API** - النشر على Instagram

### Frontend
- **HTML5** - بنية الصفحة
- **Tailwind CSS** - التصميم
- **Vanilla JavaScript** - الوظائف
- **Font Awesome** - الأيقونات

---

## 🗺️ خارطة الطريق

### الإصدار 1.1
- [ ] دعم Facebook
- [ ] دعم X (Twitter)
- [ ] دعم LinkedIn
- [ ] جدولة متقدمة
- [ ] قوالب محتوى مخصصة

### الإصدار 1.2
- [ ] تحرير المحتوى قبل النشر
- [ ] إحصائيات متقدمة
- [ ] تقارير الأداء
- [ ] دعم لغات إضافية
- [ ] وضع داكن

### الإصدار 2.0
- [ ] نظام المستخدمين والصلاحيات
- [ ] API عامة للمطورين
- [ ] تطبيق موبايل
- [ ] تكامل مع Zapier
- [ ] نظام الإضافات (Plugins)

---

## 🤝 المساهمة

نرحب بمساهماتك! يرجى قراءة [دليل المساهمة](CONTRIBUTING.md) قبل البدء.

### كيفية المساهمة

1. Fork المشروع
2. أنشئ فرع للميزة الجديدة (`git checkout -b feature/AmazingFeature`)
3. Commit التغييرات (`git commit -m 'Add some AmazingFeature'`)
4. Push إلى الفرع (`git push origin feature/AmazingFeature`)
5. افتح Pull Request

---

## 📄 الترخيص

هذا المشروع مرخص تحت **MIT License** - انظر ملف [LICENSE](LICENSE) للتفاصيل.

---

## 📞 الدعم

- **GitHub Issues**: [إنشاء مشكلة](https://github.com/Qsweet/AutoPublisherAI/issues)
- **البريد الإلكتروني**: support@autopublisher.ai

---

## 🙏 شكر وتقدير

- [OpenAI](https://openai.com) - GPT-4 و DALL-E 3
- [FastAPI](https://fastapi.tiangolo.com) - إطار العمل
- [Celery](https://docs.celeryq.dev) - معالجة المهام
- [Tailwind CSS](https://tailwindcss.com) - التصميم

---

<div align="center">

**صُنع بـ ❤️ للمحتوى العربي**

[⬆ العودة للأعلى](#autopublisherai)

</div>

