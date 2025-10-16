# 🐳 دليل تثبيت Docker - AutoPublisher AI

دليل شامل لتثبيت Docker و Docker Compose على جميع أنظمة التشغيل.

---

## 📋 اختر نظام التشغيل الخاص بك

- [Windows 10/11](#windows-1011)
- [macOS](#macos)
- [Linux (Ubuntu/Debian)](#linux-ubuntudebian)
- [Linux (CentOS/RHEL)](#linux-centosrhel)

---

## 🪟 Windows 10/11

### المتطلبات
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- أو Windows 11 64-bit
- تفعيل Virtualization في BIOS

### الخطوة 1: تحميل Docker Desktop

1. اذهب إلى: https://www.docker.com/products/docker-desktop/
2. اضغط على **"Download for Windows"**
3. انتظر حتى ينتهي التحميل (حوالي 500 MB)

### الخطوة 2: تثبيت Docker Desktop

1. **شغّل الملف المحمّل:** `Docker Desktop Installer.exe`

2. **اتبع معالج التثبيت:**
   - ✅ اقبل الشروط والأحكام
   - ✅ اختر **"Use WSL 2 instead of Hyper-V"** (موصى به)
   - ✅ اضغط **"Ok"**

3. **انتظر التثبيت** (قد يستغرق 5-10 دقائق)

4. **إعادة تشغيل الجهاز** عند الطلب

### الخطوة 3: تشغيل Docker Desktop

1. **افتح Docker Desktop** من قائمة Start

2. **انتظر حتى يبدأ Docker** (ستظهر أيقونة الحوت في شريط المهام)

3. **قد يطلب منك تثبيت WSL 2:**
   - إذا ظهرت رسالة، اضغط على الرابط المرفق
   - حمّل وثبّت WSL 2 kernel update
   - أعد تشغيل Docker Desktop

### الخطوة 4: التحقق من التثبيت

افتح **PowerShell** أو **Command Prompt** واكتب:

```powershell
docker --version
docker-compose --version
```

**النتيجة المتوقعة:**
```
Docker version 24.0.7, build afdd53b
Docker Compose version v2.23.0
```

### الخطوة 5: اختبار Docker

```powershell
docker run hello-world
```

إذا رأيت رسالة "Hello from Docker!" فكل شيء يعمل! ✅

---

### 🔧 حل المشاكل الشائعة (Windows)

#### المشكلة 1: "WSL 2 installation is incomplete"
**الحل:**
```powershell
# في PowerShell (كمسؤول):
wsl --install
wsl --set-default-version 2
```

#### المشكلة 2: "Hardware assisted virtualization is not enabled"
**الحل:**
1. أعد تشغيل الجهاز
2. ادخل BIOS (عادة F2 أو Del أو F10)
3. ابحث عن "Virtualization Technology" أو "VT-x" أو "AMD-V"
4. فعّلها (Enable)
5. احفظ واخرج

#### المشكلة 3: Docker بطيء جداً
**الحل:**
1. افتح Docker Desktop
2. Settings → Resources
3. زد Memory إلى 4GB على الأقل
4. زد CPUs إلى 2 على الأقل

---

## 🍎 macOS

### المتطلبات
- macOS 11 or newer
- Apple chip (M1/M2) أو Intel chip

### الخطوة 1: تحميل Docker Desktop

1. اذهب إلى: https://www.docker.com/products/docker-desktop/
2. اختر:
   - **"Mac with Apple chip"** إذا كان لديك M1/M2
   - **"Mac with Intel chip"** إذا كان Intel

### الخطوة 2: تثبيت Docker Desktop

1. **افتح الملف المحمّل:** `Docker.dmg`

2. **اسحب أيقونة Docker** إلى مجلد Applications

3. **افتح Docker** من Applications

4. **اقبل الأذونات** المطلوبة

5. **أدخل كلمة مرور Mac** عند الطلب

### الخطوة 3: التحقق من التثبيت

افتح **Terminal** واكتب:

```bash
docker --version
docker-compose --version
```

### الخطوة 4: اختبار Docker

```bash
docker run hello-world
```

---

### 🔧 حل المشاكل الشائعة (macOS)

#### المشكلة 1: "Docker Desktop is not running"
**الحل:**
1. افتح Docker Desktop من Applications
2. انتظر حتى تظهر أيقونة الحوت في Menu Bar

#### المشكلة 2: بطء في الأداء
**الحل:**
1. Docker Desktop → Preferences → Resources
2. زد Memory إلى 4GB
3. زد CPUs إلى 2

---

## 🐧 Linux (Ubuntu/Debian)

### الخطوة 1: تحديث النظام

```bash
sudo apt update
sudo apt upgrade -y
```

### الخطوة 2: تثبيت المتطلبات

```bash
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

### الخطوة 3: إضافة مفتاح GPG الرسمي لـ Docker

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

### الخطوة 4: إضافة مستودع Docker

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### الخطوة 5: تثبيت Docker Engine

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### الخطوة 6: إضافة المستخدم لمجموعة Docker

```bash
sudo usermod -aG docker $USER
```

**⚠️ مهم:** اخرج وادخل مرة أخرى (logout/login) أو شغّل:
```bash
newgrp docker
```

### الخطوة 7: تفعيل Docker للبدء التلقائي

```bash
sudo systemctl enable docker
sudo systemctl start docker
```

### الخطوة 8: التحقق من التثبيت

```bash
docker --version
docker compose version
```

### الخطوة 9: اختبار Docker

```bash
docker run hello-world
```

---

### 🔧 حل المشاكل الشائعة (Linux)

#### المشكلة 1: "permission denied"
**الحل:**
```bash
sudo usermod -aG docker $USER
newgrp docker
```

#### المشكلة 2: Docker لا يبدأ
**الحل:**
```bash
sudo systemctl status docker
sudo systemctl restart docker
```

---

## 🐧 Linux (CentOS/RHEL)

### الخطوة 1: تحديث النظام

```bash
sudo yum update -y
```

### الخطوة 2: تثبيت المتطلبات

```bash
sudo yum install -y yum-utils
```

### الخطوة 3: إضافة مستودع Docker

```bash
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
```

### الخطوة 4: تثبيت Docker

```bash
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### الخطوة 5: تشغيل Docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### الخطوة 6: إضافة المستخدم لمجموعة Docker

```bash
sudo usermod -aG docker $USER
newgrp docker
```

### الخطوة 7: التحقق من التثبيت

```bash
docker --version
docker compose version
docker run hello-world
```

---

## ✅ التحقق النهائي

بعد التثبيت على أي نظام، تأكد من:

### 1. Docker يعمل
```bash
docker --version
# يجب أن يظهر: Docker version 24.x.x
```

### 2. Docker Compose يعمل
```bash
docker compose version
# أو
docker-compose --version
# يجب أن يظهر: Docker Compose version v2.x.x
```

### 3. يمكنك تشغيل حاويات
```bash
docker run hello-world
# يجب أن ترى: Hello from Docker!
```

### 4. يمكنك رؤية الحاويات
```bash
docker ps -a
# يجب أن ترى قائمة الحاويات
```

---

## 🚀 الخطوة التالية: تشغيل AutoPublisher AI

الآن بعد تثبيت Docker، يمكنك تشغيل المشروع:

### 1. استنساخ المشروع
```bash
git clone https://github.com/Qsweet/AutoPublisherAI.git
cd AutoPublisherAI
```

### 2. إنشاء ملف .env
```bash
cp .env.example .env
nano .env  # أو أي محرر نصوص
```

**أضف على الأقل:**
```env
OPENAI_API_KEY=sk-your-api-key-here
POSTGRES_PASSWORD=your-strong-password
JWT_SECRET_KEY=your-secret-key-min-32-characters
```

### 3. تشغيل المشروع
```bash
./quick_start.sh
```

أو يدوياً:
```bash
docker compose up -d
```

### 4. انتظر حتى تبدأ الخدمات (30 ثانية)

### 5. افتح المتصفح
- Dashboard: http://localhost:5173
- API Docs: http://localhost:8005/docs
- Flower: http://localhost:5555

---

## 📚 موارد إضافية

### الوثائق الرسمية
- Docker Desktop: https://docs.docker.com/desktop/
- Docker Engine: https://docs.docker.com/engine/
- Docker Compose: https://docs.docker.com/compose/

### دروس فيديو
- Docker للمبتدئين (عربي): https://www.youtube.com/results?search_query=docker+tutorial+arabic
- Docker Desktop Tutorial: https://www.youtube.com/watch?v=gAkwW2tuIqE

### الحصول على مساعدة
- Docker Community: https://forums.docker.com/
- Stack Overflow: https://stackoverflow.com/questions/tagged/docker

---

## 🎯 قائمة التحقق النهائية

- [ ] Docker مثبت
- [ ] Docker Compose مثبت
- [ ] `docker --version` يعمل
- [ ] `docker compose version` يعمل
- [ ] `docker run hello-world` يعمل
- [ ] استنسخت المشروع
- [ ] أنشأت ملف .env
- [ ] أضفت OPENAI_API_KEY
- [ ] **جاهز للتشغيل!** 🎉

---

## ❓ أسئلة شائعة

### س: هل Docker مجاني؟
**ج:** نعم، Docker Desktop مجاني للاستخدام الشخصي والتعليمي والشركات الصغيرة.

### س: كم مساحة يحتاج Docker؟
**ج:** حوالي 2-3 GB للتثبيت، و 5-10 GB للمشروع.

### س: هل يؤثر على أداء الجهاز؟
**ج:** قليلاً. يستخدم حوالي 2-4 GB RAM عند التشغيل.

### س: هل يمكن إيقاف Docker؟
**ج:** نعم، يمكنك إيقاف Docker Desktop متى شئت.

### س: كيف أحذف Docker؟
**ج:** 
- Windows/Mac: من Control Panel أو Applications
- Linux: `sudo apt remove docker-ce docker-ce-cli`

---

**تم! الآن أنت جاهز لتشغيل AutoPublisher AI! 🚀**

إذا واجهت أي مشكلة، راجع قسم "حل المشاكل الشائعة" أعلاه.

