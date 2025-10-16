# دليل المساهمة في AutoPublisherAI

شكراً لاهتمامك بالمساهمة في AutoPublisherAI! نحن نرحب بجميع أنواع المساهمات من المجتمع.

## 📋 جدول المحتويات

- [كيفية المساهمة](#كيفية-المساهمة)
- [الإبلاغ عن الأخطاء](#الإبلاغ-عن-الأخطاء)
- [اقتراح ميزات جديدة](#اقتراح-ميزات-جديدة)
- [إرسال Pull Request](#إرسال-pull-request)
- [معايير الكود](#معايير-الكود)
- [الالتزام بالرسائل](#الالتزام-بالرسائل)

---

## كيفية المساهمة

### 1. Fork المشروع

انقر على زر "Fork" في أعلى الصفحة لإنشاء نسخة من المشروع في حسابك.

### 2. استنساخ المشروع

```bash
git clone https://github.com/YOUR_USERNAME/AutoPublisherAI.git
cd AutoPublisherAI
```

### 3. إنشاء فرع جديد

```bash
git checkout -b feature/amazing-feature
```

أنواع الفروع:
- `feature/` - ميزات جديدة
- `fix/` - إصلاح أخطاء
- `docs/` - تحديثات التوثيق
- `refactor/` - إعادة هيكلة الكود
- `test/` - إضافة اختبارات

### 4. إجراء التغييرات

قم بإجراء التغييرات المطلوبة مع الالتزام بمعايير الكود.

### 5. اختبار التغييرات

```bash
# تشغيل الاختبارات
docker-compose exec content-service pytest
docker-compose exec publishing-service pytest
docker-compose exec orchestrator-service pytest
```

### 6. Commit التغييرات

```bash
git add .
git commit -m "feat: add amazing feature"
```

### 7. Push إلى GitHub

```bash
git push origin feature/amazing-feature
```

### 8. إنشاء Pull Request

افتح Pull Request من فرعك إلى `main` في المشروع الأصلي.

---

## الإبلاغ عن الأخطاء

عند الإبلاغ عن خطأ، يرجى تضمين:

- **وصف واضح** للمشكلة
- **خطوات إعادة الإنتاج** - كيفية إعادة إنتاج المشكلة
- **السلوك المتوقع** - ما كنت تتوقع حدوثه
- **السلوك الفعلي** - ما حدث بالفعل
- **لقطات الشاشة** - إن أمكن
- **البيئة** - نظام التشغيل، إصدار Python، إلخ
- **السجلات** - أي رسائل خطأ ذات صلة

### مثال

```markdown
**وصف المشكلة:**
عند محاولة إنشاء مقال، تفشل العملية بخطأ 500.

**خطوات إعادة الإنتاج:**
1. افتح لوحة التحكم
2. أدخل موضوع "اختبار"
3. انقر على "إنشاء ونشر"
4. تظهر رسالة خطأ

**السلوك المتوقع:**
يجب أن يتم إنشاء المقال بنجاح.

**السلوك الفعلي:**
ظهور خطأ 500 Internal Server Error.

**البيئة:**
- OS: Ubuntu 22.04
- Docker: 24.0.5
- Python: 3.11

**السجلات:**
```
ERROR: Failed to generate content: Connection timeout
```
```

---

## اقتراح ميزات جديدة

نرحب باقتراحات الميزات الجديدة! يرجى:

1. **التحقق من Issues الموجودة** - تأكد من عدم اقتراح الميزة مسبقاً
2. **وصف الميزة بوضوح** - ما هي الميزة وكيف ستعمل
3. **شرح الفائدة** - لماذا هذه الميزة مفيدة
4. **أمثلة الاستخدام** - كيف سيستخدم المستخدمون هذه الميزة

### مثال

```markdown
**الميزة المقترحة:**
إضافة دعم للنشر على LinkedIn.

**الوصف:**
إضافة ناشر جديد يدعم النشر التلقائي على LinkedIn.

**الفائدة:**
سيتمكن المستخدمون من نشر محتواهم على منصة احترافية إضافية.

**مثال الاستخدام:**
```python
{
  "publishing_targets": [
    {
      "platform": "linkedin",
      "visibility": "public"
    }
  ]
}
```
```

---

## إرسال Pull Request

### قبل الإرسال

- ✅ تأكد من أن الكود يعمل بشكل صحيح
- ✅ أضف اختبارات للميزات الجديدة
- ✅ حدّث التوثيق إذا لزم الأمر
- ✅ تأكد من اتباع معايير الكود
- ✅ اكتب رسائل commit واضحة

### وصف Pull Request

يجب أن يتضمن Pull Request:

- **العنوان** - وصف مختصر للتغييرات
- **الوصف** - شرح تفصيلي للتغييرات
- **نوع التغيير** - ميزة جديدة، إصلاح خطأ، إلخ
- **الاختبارات** - كيف تم اختبار التغييرات
- **Issues المرتبطة** - رقم Issue إن وجد

### مثال

```markdown
## الوصف
إضافة دعم للنشر على LinkedIn.

## نوع التغيير
- [x] ميزة جديدة
- [ ] إصلاح خطأ
- [ ] تحديث توثيق

## الاختبارات
- [x] اختبارات الوحدة
- [x] اختبارات التكامل
- [x] اختبار يدوي

## Issues المرتبطة
Closes #42
```

---

## معايير الكود

### Python

نستخدم **PEP 8** كمعيار للكود Python.

#### أدوات التنسيق

```bash
# تنسيق الكود
black services/content-service/app/
black services/publishing-service/app/
black services/orchestrator-service/app/

# فحص الكود
flake8 services/content-service/app/
pylint services/content-service/app/
```

#### القواعد الأساسية

- استخدم 4 مسافات للمسافة البادئة
- أقصى طول للسطر: 100 حرف
- استخدم docstrings لجميع الدوال والفئات
- استخدم type hints
- استخدم أسماء واضحة ووصفية

#### مثال

```python
from typing import Dict, Any, Optional


def generate_content(
    topic: str,
    language: str = "ar",
    target_length: int = 1500
) -> Dict[str, Any]:
    """
    Generate content using AI.
    
    Args:
        topic: The main topic for the article
        language: Content language (default: "ar")
        target_length: Target word count (default: 1500)
        
    Returns:
        Dictionary containing generated content
        
    Raises:
        ValueError: If topic is empty
    """
    if not topic:
        raise ValueError("Topic cannot be empty")
    
    # Implementation here
    return {"title": "...", "content": "..."}
```

### JavaScript

نستخدم **JavaScript Standard Style**.

#### القواعد الأساسية

- استخدم 2 مسافات للمسافة البادئة
- استخدم single quotes للنصوص
- استخدم semicolons
- استخدم const/let بدلاً من var
- استخدم arrow functions عندما يكون مناسباً

#### مثال

```javascript
const createWorkflow = async (workflowData) => {
  try {
    const response = await fetch('/api/workflow', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(workflowData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error creating workflow:', error);
    throw error;
  }
};
```

---

## الالتزام بالرسائل

نستخدم **Conventional Commits** لرسائل الالتزام.

### الصيغة

```
<type>(<scope>): <subject>

<body>

<footer>
```

### الأنواع

- `feat` - ميزة جديدة
- `fix` - إصلاح خطأ
- `docs` - تحديثات التوثيق
- `style` - تنسيق الكود
- `refactor` - إعادة هيكلة الكود
- `test` - إضافة اختبارات
- `chore` - مهام صيانة

### أمثلة

```bash
# ميزة جديدة
feat(publishing): add LinkedIn publisher

# إصلاح خطأ
fix(content): resolve SEO analyzer timeout issue

# تحديث توثيق
docs(readme): update installation instructions

# إعادة هيكلة
refactor(orchestrator): simplify workflow execution logic

# اختبارات
test(content): add unit tests for content generator
```

---

## الأسئلة الشائعة

### كيف أبدأ في المساهمة؟

ابدأ بالبحث عن Issues المُعلّمة بـ `good first issue` أو `help wanted`.

### هل يمكنني المساهمة في التوثيق فقط؟

بالتأكيد! تحسينات التوثيق مهمة جداً ونرحب بها.

### كم من الوقت يستغرق مراجعة Pull Request؟

نحاول مراجعة جميع Pull Requests في غضون 3-5 أيام.

### ماذا لو كان لدي سؤال؟

افتح Issue جديد بعنوان يبدأ بـ `[Question]` وسنجيب عليك في أقرب وقت.

---

## مدونة قواعد السلوك

نحن ملتزمون بتوفير بيئة ترحيبية وشاملة للجميع. يُتوقع من جميع المساهمين:

- استخدام لغة ترحيبية وشاملة
- احترام وجهات النظر والخبرات المختلفة
- قبول النقد البناء بلطف
- التركيز على ما هو أفضل للمجتمع
- إظهار التعاطف تجاه أعضاء المجتمع الآخرين

---

## الترخيص

بالمساهمة في AutoPublisherAI، فإنك توافق على أن مساهماتك ستكون مرخصة تحت MIT License.

---

## شكراً لك!

شكراً لمساهمتك في جعل AutoPublisherAI أفضل! 🎉


