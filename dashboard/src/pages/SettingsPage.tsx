import { useState } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { api } from '@/services/api'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { User, Lock, CreditCard, Globe } from 'lucide-react'

type Tab = 'profile' | 'security' | 'subscription' | 'integrations'

export function SettingsPage() {
  const { user, fetchUser } = useAuthStore()
  const [activeTab, setActiveTab] = useState<Tab>('profile')
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null)

  // Profile form
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  })

  // Password form
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: '',
  })

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setMessage(null)

    try {
      await api.updateProfile(profileData)
      await fetchUser()
      setMessage({ type: 'success', text: 'تم تحديث الملف الشخصي بنجاح' })
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'فشل التحديث' })
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpdatePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordData.new_password !== passwordData.confirm_password) {
      setMessage({ type: 'error', text: 'كلمات المرور غير متطابقة' })
      return
    }

    setIsLoading(true)
    setMessage(null)

    try {
      await api.updatePassword(passwordData.current_password, passwordData.new_password)
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' })
      setMessage({ type: 'success', text: 'تم تحديث كلمة المرور بنجاح' })
    } catch (error: any) {
      setMessage({ type: 'error', text: error.response?.data?.detail || 'فشل التحديث' })
    } finally {
      setIsLoading(false)
    }
  }

  const tabs = [
    { id: 'profile' as Tab, name: 'الملف الشخصي', icon: User },
    { id: 'security' as Tab, name: 'الأمان', icon: Lock },
    { id: 'subscription' as Tab, name: 'الاشتراك', icon: CreditCard },
    { id: 'integrations' as Tab, name: 'الربط', icon: Globe },
  ]

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">الإعدادات</h1>
        <p className="text-gray-600 mt-1">
          إدارة حسابك وتفضيلاتك
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 space-x-reverse">
          {tabs.map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => {
                  setActiveTab(tab.id)
                  setMessage(null)
                }}
                className={`
                  flex items-center px-1 py-4 border-b-2 font-medium text-sm transition-colors
                  ${activeTab === tab.id
                    ? 'border-primary-600 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="w-5 h-5 ml-2" />
                {tab.name}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Messages */}
      {message && (
        <div className={`
          px-4 py-3 rounded-lg
          ${message.type === 'success' ? 'bg-green-50 border border-green-200 text-green-700' : 'bg-red-50 border border-red-200 text-red-700'}
        `}>
          {message.text}
        </div>
      )}

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <Card>
          <CardHeader>
            <h2 className="text-xl font-bold text-gray-900">المعلومات الشخصية</h2>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleUpdateProfile} className="space-y-4">
              <Input
                label="الاسم الكامل"
                type="text"
                value={profileData.full_name}
                onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                placeholder="أحمد محمد"
              />

              <Input
                label="البريد الإلكتروني"
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({ ...profileData, email: e.target.value })}
                placeholder="example@email.com"
                disabled
              />

              <p className="text-sm text-gray-500">
                لتغيير البريد الإلكتروني، يرجى التواصل مع الدعم
              </p>

              <Button type="submit" isLoading={isLoading}>
                حفظ التغييرات
              </Button>
            </form>
          </CardBody>
        </Card>
      )}

      {/* Security Tab */}
      {activeTab === 'security' && (
        <Card>
          <CardHeader>
            <h2 className="text-xl font-bold text-gray-900">تغيير كلمة المرور</h2>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleUpdatePassword} className="space-y-4">
              <Input
                label="كلمة المرور الحالية"
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
                placeholder="••••••••"
              />

              <Input
                label="كلمة المرور الجديدة"
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                placeholder="••••••••"
              />

              <Input
                label="تأكيد كلمة المرور الجديدة"
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                placeholder="••••••••"
              />

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">متطلبات كلمة المرور:</h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• 8 أحرف على الأقل</li>
                  <li>• حرف كبير واحد على الأقل</li>
                  <li>• حرف صغير واحد على الأقل</li>
                  <li>• رقم واحد على الأقل</li>
                </ul>
              </div>

              <Button type="submit" isLoading={isLoading}>
                تحديث كلمة المرور
              </Button>
            </form>
          </CardBody>
        </Card>
      )}

      {/* Subscription Tab */}
      {activeTab === 'subscription' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-bold text-gray-900">باقتك الحالية</h2>
            </CardHeader>
            <CardBody>
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">
                    {user?.subscription_tier === 'free' && 'الباقة المجانية'}
                    {user?.subscription_tier === 'basic' && 'الباقة الأساسية'}
                    {user?.subscription_tier === 'pro' && 'الباقة الاحترافية'}
                    {user?.subscription_tier === 'enterprise' && 'باقة الأعمال'}
                  </h3>
                  <p className="text-gray-600">{user?.articles_limit} مقالة شهرياً</p>
                </div>
                <div className="text-left">
                  <p className="text-3xl font-bold text-gray-900">
                    {user?.subscription_tier === 'free' && '$0'}
                    {user?.subscription_tier === 'basic' && '$29'}
                    {user?.subscription_tier === 'pro' && '$99'}
                    {user?.subscription_tier === 'enterprise' && '$299'}
                  </p>
                  <p className="text-gray-600">/شهرياً</p>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-gray-600">الاستخدام هذا الشهر</span>
                  <span className="font-medium">{user?.articles_count} / {user?.articles_limit}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${((user?.articles_count || 0) / (user?.articles_limit || 1)) * 100}%` }}
                  />
                </div>
              </div>

              {user?.subscription_tier === 'free' && (
                <Button className="w-full">
                  ترقية الباقة
                </Button>
              )}
            </CardBody>
          </Card>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { name: 'الأساسية', price: 29, articles: 50, tier: 'basic' },
              { name: 'الاحترافية', price: 99, articles: 200, tier: 'pro', popular: true },
              { name: 'الأعمال', price: 299, articles: 'غير محدود', tier: 'enterprise' },
            ].map((plan) => (
              <Card key={plan.tier} className={plan.popular ? 'border-2 border-primary-600' : ''}>
                {plan.popular && (
                  <div className="bg-primary-600 text-white text-center py-2 text-sm font-medium rounded-t-lg">
                    الأكثر شعبية
                  </div>
                )}
                <CardBody>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="mb-4">
                    <span className="text-4xl font-bold text-gray-900">${plan.price}</span>
                    <span className="text-gray-600">/شهر</span>
                  </div>
                  <p className="text-gray-600 mb-6">{plan.articles} مقالة شهرياً</p>
                  <Button
                    className="w-full"
                    variant={plan.popular ? 'primary' : 'outline'}
                    disabled={user?.subscription_tier === plan.tier}
                  >
                    {user?.subscription_tier === plan.tier ? 'الباقة الحالية' : 'اختر هذه الباقة'}
                  </Button>
                </CardBody>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* Integrations Tab */}
      {activeTab === 'integrations' && (
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <h2 className="text-xl font-bold text-gray-900">WordPress</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <Input
                label="رابط الموقع"
                type="url"
                placeholder="https://example.com"
              />
              <Input
                label="اسم المستخدم"
                type="text"
                placeholder="admin"
              />
              <Input
                label="كلمة مرور التطبيق"
                type="password"
                placeholder="xxxx xxxx xxxx xxxx"
              />
              <Button>حفظ الإعدادات</Button>
            </CardBody>
          </Card>

          <Card>
            <CardHeader>
              <h2 className="text-xl font-bold text-gray-900">Instagram</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <Input
                label="Access Token"
                type="text"
                placeholder="IGQVJXXXXXXXXXXXXXXXXXXx"
              />
              <Input
                label="Instagram Business Account ID"
                type="text"
                placeholder="1234567890"
              />
              <Button>حفظ الإعدادات</Button>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  )
}

