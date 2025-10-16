# 🚀 دليل النشر على VPS

هذا الدليل يشرح كيفية نشر **AutoPublisherAI** على خادم VPS بشكل كامل.

---

## 📋 المتطلبات الأساسية

### 1. VPS Server
- **نظام التشغيل:** Ubuntu 22.04 LTS
- **الذاكرة:** 4GB RAM على الأقل (8GB موصى به)
- **المعالج:** 2 vCPU cores على الأقل
- **التخزين:** 50GB على الأقل
- **الوصول:** Root أو sudo access

### 2. المفاتيح المطلوبة
- OpenAI API Key
- WordPress credentials (اختياري)
- Instagram API tokens (اختياري)

### 3. Domain Name (اختياري)
- للحصول على SSL certificate
- يمكن استخدام IP مباشرة للبداية

---

## 🎯 طريقة النشر السريعة (5 دقائق)

### الخطوة 1: الاتصال بالـ VPS

```bash
ssh root@YOUR_VPS_IP
```

### الخطوة 2: تحميل سكريبت النشر

```bash
# تحميل المشروع
git clone https://github.com/Qsweet/AutoPublisherAI.git /opt/autopublisher
cd /opt/autopublisher

# تشغيل سكريبت النشر
chmod +x deploy.sh
./deploy.sh
```

### الخطوة 3: إعداد المفاتيح

```bash
# تحرير ملف البيئة
nano /opt/autopublisher/.env

# أضف مفتاح OpenAI
OPENAI_API_KEY=your_actual_openai_api_key_here

# احفظ واخرج (Ctrl+X, Y, Enter)
```

### الخطوة 4: إعادة تشغيل الخدمات

```bash
cd /opt/autopublisher
docker compose restart
```

### الخطوة 5: التحقق من التشغيل

```bash
# عرض حالة الخدمات
docker compose ps

# عرض السجلات
docker compose logs -f
```

---

## 📝 طريقة النشر اليدوية (خطوة بخطوة)

### 1. تحديث النظام

```bash
apt-get update -y
apt-get upgrade -y
```

### 2. تثبيت Docker

```bash
# إضافة مستودع Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# تشغيل Docker
systemctl start docker
systemctl enable docker

# التحقق من التثبيت
docker --version
```

### 3. تثبيت Docker Compose

```bash
# Docker Compose مضمن مع Docker الآن
docker compose version
```

### 4. إعداد Firewall

```bash
# تثبيت UFW
apt-get install -y ufw

# السماح بالمنافذ المطلوبة
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS

# تفعيل Firewall
ufw enable

# التحقق من الحالة
ufw status
```

### 5. استنساخ المشروع

```bash
# استنساخ من GitHub
git clone https://github.com/Qsweet/AutoPublisherAI.git /opt/autopublisher
cd /opt/autopublisher
```

### 6. إعداد ملف البيئة

```bash
# نسخ ملف المثال
cp .env.example .env

# توليد كلمات مرور قوية
POSTGRES_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -hex 32)
API_SECRET=$(openssl rand -hex 32)

# تحديث ملف .env
nano .env
```

**المتغيرات المطلوبة:**

```env
# OpenAI (إلزامي)
OPENAI_API_KEY=your_openai_api_key_here

# Database (تم توليدها تلقائياً)
POSTGRES_PASSWORD=your_generated_password

# Security (تم توليدها تلقائياً)
JWT_SECRET_KEY=your_generated_secret
API_SECRET_KEY=your_generated_api_key

# WordPress (اختياري)
WORDPRESS_URL=https://your-wordpress-site.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=your_app_password

# Instagram (اختياري)
INSTAGRAM_ACCESS_TOKEN=your_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
```

### 7. بناء وتشغيل الخدمات

```bash
cd /opt/autopublisher

# بناء الصور
docker compose build

# تشغيل الخدمات
docker compose up -d

# التحقق من الحالة
docker compose ps
```

### 8. إعداد SSL (اختياري)

```bash
# تثبيت Certbot
apt-get install -y certbot python3-certbot-nginx

# تثبيت Nginx
apt-get install -y nginx

# الحصول على شهادة SSL
certbot --nginx -d yourdomain.com

# التجديد التلقائي
certbot renew --dry-run
```

---

## 🔧 إعداد Nginx كـ Reverse Proxy

### إنشاء ملف إعداد Nginx

```bash
nano /etc/nginx/sites-available/autopublisher
```

**محتوى الملف:**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Dashboard
    location / {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Content Service API
    location /api/content {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Publishing Service API
    location /api/publish {
        proxy_pass http://localhost:8002;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Orchestrator Service API
    location /api/workflow {
        proxy_pass http://localhost:8003;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Flower (Celery Monitor)
    location /flower {
        proxy_pass http://localhost:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**تفعيل الإعداد:**

```bash
# إنشاء رابط رمزي
ln -s /etc/nginx/sites-available/autopublisher /etc/nginx/sites-enabled/

# اختبار الإعداد
nginx -t

# إعادة تشغيل Nginx
systemctl restart nginx
```

---

## 🔍 التحقق من التشغيل

### 1. فحص الخدمات

```bash
# عرض الخدمات العاملة
docker compose ps

# يجب أن ترى:
# - postgres (running)
# - redis (running)
# - content-service (running)
# - publishing-service (running)
# - orchestrator-service (running)
# - celery-worker (running)
# - celery-beat (running)
# - flower (running)
```

### 2. فحص السجلات

```bash
# عرض جميع السجلات
docker compose logs -f

# عرض سجلات خدمة معينة
docker compose logs -f content-service
```

### 3. فحص Health Checks

```bash
# Content Service
curl http://localhost:8001/health

# Publishing Service
curl http://localhost:8002/health

# Orchestrator Service
curl http://localhost:8003/health
```

### 4. الوصول إلى الواجهات

افتح المتصفح وانتقل إلى:

- **Dashboard:** `http://YOUR_VPS_IP:8080`
- **Content Service API Docs:** `http://YOUR_VPS_IP:8001/docs`
- **Publishing Service API Docs:** `http://YOUR_VPS_IP:8002/docs`
- **Orchestrator Service API Docs:** `http://YOUR_VPS_IP:8003/docs`
- **Flower (Celery Monitor):** `http://YOUR_VPS_IP:5555`

---

## 🛠️ الصيانة والإدارة

### إعادة تشغيل الخدمات

```bash
cd /opt/autopublisher

# إعادة تشغيل جميع الخدمات
docker compose restart

# إعادة تشغيل خدمة معينة
docker compose restart content-service
```

### إيقاف الخدمات

```bash
cd /opt/autopublisher

# إيقاف جميع الخدمات
docker compose down

# إيقاف وحذف البيانات
docker compose down -v
```

### تحديث المشروع

```bash
cd /opt/autopublisher

# سحب آخر التحديثات
git pull

# إعادة بناء وتشغيل
docker compose up -d --build
```

### عرض استخدام الموارد

```bash
# استخدام Docker
docker stats

# استخدام النظام
htop
```

### النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
docker compose exec postgres pg_dump -U autopublisher autopublisher_db > backup_$(date +%Y%m%d).sql

# نسخ احتياطي لملف .env
cp /opt/autopublisher/.env /opt/autopublisher/.env.backup
```

### الاستعادة من النسخ الاحتياطي

```bash
# استعادة قاعدة البيانات
docker compose exec -T postgres psql -U autopublisher autopublisher_db < backup_20241016.sql
```

---

## 🔒 أمان الإنتاج

### 1. تغيير المنفذ الافتراضي لـ SSH

```bash
nano /etc/ssh/sshd_config

# غيّر:
Port 22
# إلى:
Port 2222

# أعد تشغيل SSH
systemctl restart sshd

# حدّث Firewall
ufw allow 2222/tcp
ufw delete allow 22/tcp
```

### 2. تعطيل تسجيل الدخول بـ Root

```bash
nano /etc/ssh/sshd_config

# غيّر:
PermitRootLogin yes
# إلى:
PermitRootLogin no

# أعد تشغيل SSH
systemctl restart sshd
```

### 3. إعداد Fail2Ban

```bash
# تثبيت Fail2Ban
apt-get install -y fail2ban

# إنشاء ملف إعداد
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# تفعيل الحماية
systemctl enable fail2ban
systemctl start fail2ban
```

### 4. تحديثات الأمان التلقائية

```bash
# تثبيت unattended-upgrades
apt-get install -y unattended-upgrades

# تفعيل التحديثات التلقائية
dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 المراقبة والتنبيهات

### إعداد Monitoring مع Prometheus (اختياري)

```yaml
# إضافة إلى docker-compose.yml
prometheus:
  image: prom/prometheus
  ports:
    - "9090:9090"
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
```

---

## ❓ حل المشاكل الشائعة

### المشكلة: الخدمات لا تبدأ

```bash
# فحص السجلات
docker compose logs

# فحص استخدام الذاكرة
free -h

# فحص المساحة
df -h
```

### المشكلة: لا يمكن الوصول إلى الخدمات

```bash
# فحص Firewall
ufw status

# فحص المنافذ
netstat -tulpn | grep LISTEN

# فحص Docker network
docker network ls
docker network inspect autopublisher_default
```

### المشكلة: OpenAI API لا يعمل

```bash
# فحص المفتاح في .env
cat /opt/autopublisher/.env | grep OPENAI_API_KEY

# اختبار الاتصال
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_API_KEY"
```

---

## 📞 الدعم

إذا واجهت أي مشاكل:

1. فحص السجلات: `docker compose logs -f`
2. فحص الـ Issues على GitHub
3. إنشاء Issue جديد مع تفاصيل المشكلة

---

## ✅ قائمة التحقق النهائية

- [ ] VPS مُعد بنظام Ubuntu 22.04
- [ ] Docker و Docker Compose مثبتان
- [ ] Firewall مُعد ومُفعّل
- [ ] المشروع مستنسخ في `/opt/autopublisher`
- [ ] ملف `.env` مُعد بالمفاتيح الصحيحة
- [ ] جميع الخدمات تعمل (`docker compose ps`)
- [ ] Health checks تعمل
- [ ] يمكن الوصول إلى Dashboard
- [ ] SSL مُعد (إذا كان لديك domain)
- [ ] النسخ الاحتياطية مُعدة

---

**تهانينا! 🎉 AutoPublisherAI الآن يعمل على VPS الخاص بك!**

