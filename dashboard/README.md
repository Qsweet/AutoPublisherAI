# AutoPublisher AI Dashboard

لوحة تحكم احترافية لمنصة AutoPublisher AI مبنية بـ React و TypeScript.

## 🚀 التقنيات المستخدمة

- **React 18** - مكتبة UI
- **TypeScript** - للأمان والجودة
- **Tailwind CSS** - للتصميم
- **Vite** - أداة البناء
- **React Router** - للتنقل
- **Zustand** - إدارة الحالة
- **React Query** - إدارة البيانات
- **Axios** - HTTP Client

## 📦 التثبيت

```bash
# تثبيت المكتبات
pnpm install

# نسخ ملف البيئة
cp .env.example .env

# تشغيل التطبيق
pnpm dev
```

## 🎯 الصفحات

- **Login** - تسجيل الدخول
- **Register** - إنشاء حساب جديد
- **Dashboard** - لوحة التحكم الرئيسية
- **Create Article** - إنشاء مقال جديد
- **Articles** - عرض المقالات
- **Settings** - الإعدادات

## 🔧 البنية

```
src/
├── components/      # المكونات القابلة لإعادة الاستخدام
├── pages/          # صفحات التطبيق
├── services/       # API Services
├── stores/         # Zustand Stores
├── types/          # TypeScript Types
├── utils/          # Utility Functions
└── hooks/          # Custom Hooks
```

## 🌐 API Integration

التطبيق يتصل بـ Auth Service على المنفذ 8005.

تأكد من تشغيل الخدمات الخلفية:

```bash
# في المجلد الرئيسي
docker-compose up -d
```

## 📝 الأوامر

```bash
# التطوير
pnpm dev

# البناء للإنتاج
pnpm build

# معاينة البناء
pnpm preview

# Linting
pnpm lint
```

## 🎨 التخصيص

يمكنك تخصيص الألوان في `tailwind.config.js`.

## 🔐 الأمان

- JWT Authentication
- Protected Routes
- Token Refresh
- Secure Storage

## 📱 الاستجابة

التطبيق مصمم ليعمل على جميع الأجهزة.

## 🌍 اللغة

التطبيق يدعم اللغة العربية بشكل كامل مع دعم RTL.

