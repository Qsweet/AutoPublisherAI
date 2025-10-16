import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Card, CardBody, CardHeader } from '@/components/Card'

export function RegisterPage() {
  const navigate = useNavigate()
  const { register, isLoading, error, clearError } = useAuthStore()
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    full_name: '',
  })
  
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})
  const [acceptTerms, setAcceptTerms] = useState(false)

  const validateForm = () => {
    const errors: Record<string, string> = {}
    
    if (!formData.email) {
      errors.email = 'البريد الإلكتروني مطلوب'
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      errors.email = 'البريد الإلكتروني غير صالح'
    }
    
    if (!formData.password) {
      errors.password = 'كلمة المرور مطلوبة'
    } else if (formData.password.length < 8) {
      errors.password = 'كلمة المرور يجب أن تكون 8 أحرف على الأقل'
    } else if (!/[A-Z]/.test(formData.password)) {
      errors.password = 'كلمة المرور يجب أن تحتوي على حرف كبير'
    } else if (!/[a-z]/.test(formData.password)) {
      errors.password = 'كلمة المرور يجب أن تحتوي على حرف صغير'
    } else if (!/[0-9]/.test(formData.password)) {
      errors.password = 'كلمة المرور يجب أن تحتوي على رقم'
    }
    
    if (!formData.confirmPassword) {
      errors.confirmPassword = 'تأكيد كلمة المرور مطلوب'
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = 'كلمات المرور غير متطابقة'
    }
    
    if (!acceptTerms) {
      errors.terms = 'يجب الموافقة على الشروط والأحكام'
    }
    
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    clearError()
    
    if (!validateForm()) return

    try {
      await register({
        email: formData.email,
        password: formData.password,
        full_name: formData.full_name || undefined,
      })
      navigate('/dashboard')
    } catch (error) {
      // Error is handled by the store
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // Clear error for this field
    if (formErrors[name]) {
      setFormErrors(prev => ({ ...prev, [name]: '' }))
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-primary-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary-900 mb-2">
            AutoPublisher AI
          </h1>
          <p className="text-gray-600">
            ابدأ رحلتك في النشر الذكي
          </p>
        </div>

        <Card>
          <CardHeader>
            <h2 className="text-2xl font-bold text-gray-900">إنشاء حساب جديد</h2>
            <p className="text-sm text-gray-600 mt-1">
              انضم إلينا وابدأ في إنشاء محتوى احترافي
            </p>
          </CardHeader>

          <CardBody>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <Input
                label="الاسم الكامل (اختياري)"
                type="text"
                name="full_name"
                value={formData.full_name}
                onChange={handleChange}
                placeholder="أحمد محمد"
                autoComplete="name"
              />

              <Input
                label="البريد الإلكتروني"
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                error={formErrors.email}
                placeholder="example@email.com"
                autoComplete="email"
              />

              <Input
                label="كلمة المرور"
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                error={formErrors.password}
                placeholder="••••••••"
                autoComplete="new-password"
              />

              <Input
                label="تأكيد كلمة المرور"
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                error={formErrors.confirmPassword}
                placeholder="••••••••"
                autoComplete="new-password"
              />

              <div className="space-y-2">
                <label className="flex items-start">
                  <input
                    type="checkbox"
                    checked={acceptTerms}
                    onChange={(e) => {
                      setAcceptTerms(e.target.checked)
                      if (formErrors.terms) {
                        setFormErrors(prev => ({ ...prev, terms: '' }))
                      }
                    }}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 mt-1"
                  />
                  <span className="mr-2 text-sm text-gray-700">
                    أوافق على{' '}
                    <Link to="/terms" className="text-primary-600 hover:underline">
                      شروط الخدمة
                    </Link>{' '}
                    و{' '}
                    <Link to="/privacy" className="text-primary-600 hover:underline">
                      سياسة الخصوصية
                    </Link>
                  </span>
                </label>
                {formErrors.terms && (
                  <p className="text-sm text-red-600">{formErrors.terms}</p>
                )}
              </div>

              <Button
                type="submit"
                className="w-full"
                isLoading={isLoading}
              >
                إنشاء الحساب
              </Button>
            </form>

            <div className="mt-6 text-center">
              <p className="text-sm text-gray-600">
                لديك حساب بالفعل؟{' '}
                <Link
                  to="/login"
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  سجل الدخول
                </Link>
              </p>
            </div>
          </CardBody>
        </Card>

        <div className="mt-6 bg-white rounded-lg p-4 border border-gray-200">
          <h3 className="font-medium text-gray-900 mb-2">الباقة المجانية تشمل:</h3>
          <ul className="space-y-1 text-sm text-gray-600">
            <li className="flex items-center">
              <svg className="w-4 h-4 text-green-500 ml-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              5 مقالات شهرياً
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 text-green-500 ml-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              توليد محتوى بالذكاء الاصطناعي
            </li>
            <li className="flex items-center">
              <svg className="w-4 h-4 text-green-500 ml-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              نشر على WordPress وInstagram
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

