# 🔌 أمثلة API - AutoPublisher AI

أمثلة عملية لاستخدام جميع API endpoints.

---

## 🔐 Auth Service (Port 8005)

### 1. تسجيل مستخدم جديد
```bash
curl -X POST http://localhost:8005/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!",
    "full_name": "John Doe"
  }'
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "subscription_tier": "free",
  "articles_this_month": 0,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### 2. تسجيل الدخول
```bash
curl -X POST http://localhost:8005/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. تحديث Access Token
```bash
curl -X POST http://localhost:8005/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "YOUR_REFRESH_TOKEN"
  }'
```

### 4. الحصول على معلومات المستخدم
```bash
curl -X GET http://localhost:8005/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. تحديث البروفايل
```bash
curl -X PUT http://localhost:8005/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "John Smith",
    "bio": "Content creator and AI enthusiast"
  }'
```

### 6. تغيير كلمة المرور
```bash
curl -X PUT http://localhost:8005/api/v1/auth/me/password \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePassword123!",
    "new_password": "NewSecurePassword456!"
  }'
```

### 7. الحصول على إحصائيات الاستخدام
```bash
curl -X GET http://localhost:8005/api/v1/auth/me/usage \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "subscription_tier": "free",
  "articles_this_month": 3,
  "articles_limit": 5,
  "remaining_articles": 2,
  "reset_date": "2024-02-01T00:00:00Z"
}
```

### 8. ترقية الاشتراك
```bash
curl -X PUT http://localhost:8005/api/v1/auth/me/subscription \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tier": "pro"
  }'
```

---

## 📝 Content Service (Port 8001)

### 1. توليد مقال (متزامن)
```bash
curl -X POST http://localhost:8001/api/content/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "الذكاء الاصطناعي في التعليم",
    "language": "ar",
    "tone": "professional",
    "target_audience": "teachers",
    "keywords": ["الذكاء الاصطناعي", "التعليم", "التكنولوجيا"],
    "include_images": true,
    "include_faq": true
  }'
```

**Response:**
```json
{
  "title": "الذكاء الاصطناعي: ثورة في عالم التعليم",
  "content": "<p>في عصر التكنولوجيا المتسارعة...</p>",
  "excerpt": "استكشف كيف يغير الذكاء الاصطناعي مستقبل التعليم...",
  "featured_image_url": "https://oaidalleapiprodscus.blob.core.windows.net/...",
  "word_count": 1500,
  "reading_time": 6,
  "seo": {
    "meta_title": "الذكاء الاصطناعي في التعليم: دليل شامل 2024",
    "meta_description": "اكتشف كيف يحدث الذكاء الاصطناعي ثورة في التعليم...",
    "keywords": ["الذكاء الاصطناعي", "التعليم", "التكنولوجيا"],
    "slug": "ai-in-education-comprehensive-guide"
  },
  "faq": [
    {
      "question": "ما هو دور الذكاء الاصطناعي في التعليم؟",
      "answer": "يساعد الذكاء الاصطناعي في تخصيص التعلم..."
    }
  ]
}
```

### 2. توليد مقال (غير متزامن)
```bash
curl -X POST http://localhost:8001/api/content/generate-async \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Future of AI",
    "language": "en"
  }'
```

**Response:**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "message": "Article generation started"
}
```

### 3. التحقق من حالة المهمة
```bash
curl -X GET http://localhost:8001/api/content/task/550e8400-e29b-41d4-a716-446655440000
```

**Response (Pending):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "progress": 30
}
```

**Response (Completed):**
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "title": "...",
    "content": "..."
  }
}
```

---

## 📤 Publishing Service (Port 8002)

### 1. النشر على WordPress
```bash
curl -X POST http://localhost:8002/api/publish \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "wordpress",
    "content": {
      "title": "عنوان المقال",
      "content": "<p>محتوى المقال...</p>",
      "excerpt": "ملخص المقال",
      "featured_image_url": "https://example.com/image.jpg",
      "categories": ["تقنية", "ذكاء اصطناعي"],
      "tags": ["AI", "تعليم"],
      "status": "publish"
    },
    "credentials": {
      "url": "https://your-site.com",
      "username": "your-username",
      "app_password": "xxxx xxxx xxxx xxxx xxxx xxxx"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "platform": "wordpress",
  "post_id": "123",
  "post_url": "https://your-site.com/article-slug",
  "published_at": "2024-01-01T12:00:00Z"
}
```

### 2. النشر على Instagram
```bash
curl -X POST http://localhost:8002/api/publish \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "instagram",
    "content": {
      "caption": "نص المنشور مع الهاشتاجات #AI #تقنية",
      "image_url": "https://example.com/image.jpg"
    },
    "credentials": {
      "access_token": "YOUR_INSTAGRAM_ACCESS_TOKEN",
      "user_id": "YOUR_INSTAGRAM_USER_ID"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "platform": "instagram",
  "post_id": "17895695668004550",
  "permalink": "https://www.instagram.com/p/ABC123/",
  "published_at": "2024-01-01T12:00:00Z"
}
```

### 3. النشر الجماعي (Multi-Platform)
```bash
curl -X POST http://localhost:8002/api/publish/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "platforms": ["wordpress", "instagram"],
    "content": {
      "title": "عنوان المقال",
      "content": "<p>محتوى...</p>",
      "excerpt": "ملخص...",
      "caption": "نص للسوشيال ميديا",
      "image_url": "https://example.com/image.jpg",
      "categories": ["تقنية"],
      "tags": ["AI"]
    },
    "credentials": {
      "wordpress": {
        "url": "https://your-site.com",
        "username": "username",
        "app_password": "password"
      },
      "instagram": {
        "access_token": "token",
        "user_id": "user_id"
      }
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "platform": "wordpress",
      "success": true,
      "post_id": "123",
      "post_url": "https://..."
    },
    {
      "platform": "instagram",
      "success": true,
      "post_id": "17895695668004550",
      "permalink": "https://..."
    }
  ]
}
```

---

## 🎯 Strategy Service (Port 8004)

### 1. توليد استراتيجية محتوى (90 يوم)
```bash
curl -X POST http://localhost:8004/api/strategy/generate \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "التكنولوجيا",
    "target_audience": "المطورين والمبرمجين",
    "goals": ["increase_traffic", "build_authority", "generate_leads"],
    "duration_days": 90,
    "language": "ar",
    "current_traffic": 1000,
    "content_frequency": "daily"
  }'
```

**Response:**
```json
{
  "industry": "التكنولوجيا",
  "target_audience": "المطورين والمبرمجين",
  "duration_days": 90,
  "keyword_clusters": [
    {
      "main_keyword": "الذكاء الاصطناعي",
      "related_keywords": ["تعلم الآلة", "الشبكات العصبية"],
      "search_volume": 10000,
      "difficulty": "medium"
    }
  ],
  "content_ideas": [
    {
      "title": "دليل شامل للذكاء الاصطناعي للمبتدئين",
      "description": "مقال تعليمي يغطي أساسيات الذكاء الاصطناعي...",
      "keywords": ["الذكاء الاصطناعي", "تعلم الآلة"],
      "estimated_difficulty": "medium",
      "estimated_traffic": 500,
      "content_type": "tutorial"
    }
  ],
  "publishing_schedule": {
    "monday": ["morning", "evening"],
    "tuesday": ["morning"],
    "wednesday": ["morning", "evening"]
  },
  "traffic_projections": {
    "month_1": 1500,
    "month_2": 2500,
    "month_3": 4000
  },
  "recommendations": [
    "ركز على المحتوى التعليمي في البداية",
    "استخدم الأمثلة العملية",
    "أضف صور توضيحية"
  ]
}
```

### 2. توليد استراتيجية (غير متزامن)
```bash
curl -X POST http://localhost:8004/api/strategy/generate-async \
  -H "Content-Type: application/json" \
  -d '{
    "industry": "Technology",
    "target_audience": "Developers",
    "duration_days": 90
  }'
```

---

## 🔄 Orchestrator Service (Port 8003)

### 1. إنشاء ونشر مقال كامل
```bash
curl -X POST http://localhost:8003/api/workflow/create-and-publish \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "الذكاء الاصطناعي في الطب",
    "platforms": ["wordpress", "instagram"],
    "language": "ar",
    "tone": "professional",
    "credentials": {
      "wordpress": {
        "url": "https://your-site.com",
        "username": "username",
        "app_password": "password"
      },
      "instagram": {
        "access_token": "token",
        "user_id": "user_id"
      }
    }
  }'
```

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "steps": {
    "content_generation": "pending",
    "publishing": "pending"
  }
}
```

### 2. جدولة مقال
```bash
curl -X POST http://localhost:8003/api/workflow/schedule \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "مستقبل الذكاء الاصطناعي",
    "platforms": ["wordpress"],
    "scheduled_time": "2024-12-31T12:00:00Z",
    "language": "ar",
    "credentials": {
      "wordpress": {...}
    }
  }'
```

### 3. التحقق من حالة Workflow
```bash
curl -X GET http://localhost:8003/api/workflow/550e8400-e29b-41d4-a716-446655440000/status
```

**Response:**
```json
{
  "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "steps": {
    "content_generation": {
      "status": "completed",
      "completed_at": "2024-01-01T12:05:00Z"
    },
    "publishing": {
      "status": "completed",
      "completed_at": "2024-01-01T12:06:00Z",
      "results": [
        {
          "platform": "wordpress",
          "success": true,
          "post_url": "https://..."
        }
      ]
    }
  },
  "created_at": "2024-01-01T12:00:00Z",
  "completed_at": "2024-01-01T12:06:00Z"
}
```

### 4. إلغاء Workflow
```bash
curl -X POST http://localhost:8003/api/workflow/550e8400-e29b-41d4-a716-446655440000/cancel
```

---

## 🧪 أمثلة متقدمة

### مثال 1: سير عمل كامل
```bash
#!/bin/bash

# 1. تسجيل الدخول
TOKEN=$(curl -s -X POST http://localhost:8005/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}' \
  | jq -r '.access_token')

# 2. توليد استراتيجية
STRATEGY=$(curl -s -X POST http://localhost:8004/api/strategy/generate \
  -H "Content-Type: application/json" \
  -d '{"industry":"Tech","target_audience":"Developers","duration_days":30}')

# 3. استخراج أول فكرة
TOPIC=$(echo $STRATEGY | jq -r '.content_ideas[0].title')

# 4. توليد مقال
ARTICLE=$(curl -s -X POST http://localhost:8001/api/content/generate \
  -H "Content-Type: application/json" \
  -d "{\"topic\":\"$TOPIC\",\"language\":\"en\"}")

# 5. نشر المقال
curl -X POST http://localhost:8002/api/publish \
  -H "Content-Type: application/json" \
  -d "{\"platform\":\"wordpress\",\"content\":$ARTICLE,\"credentials\":{...}}"
```

### مثال 2: نشر مجدول
```bash
# جدولة 5 مقالات على مدار أسبوع
for i in {1..5}; do
  SCHEDULED_TIME=$(date -d "+$i days 10:00" -Iseconds)
  
  curl -X POST http://localhost:8003/api/workflow/schedule \
    -H "Content-Type: application/json" \
    -d "{
      \"topic\": \"AI Topic $i\",
      \"platforms\": [\"wordpress\"],
      \"scheduled_time\": \"$SCHEDULED_TIME\",
      \"credentials\": {...}
    }"
done
```

---

## 📚 ملاحظات

### Authentication
معظم endpoints تتطلب JWT token في header:
```bash
-H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Error Handling
جميع الأخطاء تُرجع بصيغة:
```json
{
  "detail": "Error message here"
}
```

### Rate Limiting
- Free tier: 5 requests/minute
- Basic tier: 20 requests/minute
- Pro tier: 100 requests/minute
- Enterprise: Unlimited

---

**للمزيد من الأمثلة، راجع:**
- [TESTING_GUIDE.md](./TESTING_GUIDE.md)
- [API Documentation](http://localhost:8005/docs)

