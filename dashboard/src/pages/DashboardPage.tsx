import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { api } from '@/services/api'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Button } from '@/components/Button'
import { FileText, TrendingUp, Users, PlusCircle } from 'lucide-react'
import type { UsageStats } from '@/types/user'

export function DashboardPage() {
  const { user } = useAuthStore()
  const [usageStats, setUsageStats] = useState<UsageStats | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadUsageStats()
  }, [])

  const loadUsageStats = async () => {
    try {
      const stats = await api.getUsageStats()
      setUsageStats(stats)
    } catch (error) {
      console.error('Failed to load usage stats:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const stats = [
    {
      name: 'المقالات المنشورة',
      value: user?.articles_count || 0,
      icon: FileText,
      color: 'bg-blue-500',
    },
    {
      name: 'المقالات المتبقية',
      value: user?.remaining_articles || 0,
      icon: TrendingUp,
      color: 'bg-green-500',
    },
    {
      name: 'نسبة الاستخدام',
      value: `${usageStats?.usage_percentage || 0}%`,
      icon: Users,
      color: 'bg-purple-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            مرحباً، {user?.full_name || user?.email}!
          </h1>
          <p className="text-gray-600 mt-1">
            إليك نظرة عامة على نشاطك اليوم
          </p>
        </div>
        <Link to="/dashboard/create">
          <Button>
            <PlusCircle className="w-5 h-5 ml-2" />
            إنشاء مقال جديد
          </Button>
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.name}>
              <CardBody>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">{stat.name}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">
                      {stat.value}
                    </p>
                  </div>
                  <div className={`${stat.color} p-3 rounded-lg`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                </div>
              </CardBody>
            </Card>
          )
        })}
      </div>

      {/* Subscription Info */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-bold text-gray-900">باقتك الحالية</h2>
        </CardHeader>
        <CardBody>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-lg font-medium text-gray-900">
                {user?.subscription_tier === 'free' && 'الباقة المجانية'}
                {user?.subscription_tier === 'basic' && 'الباقة الأساسية'}
                {user?.subscription_tier === 'pro' && 'الباقة الاحترافية'}
                {user?.subscription_tier === 'enterprise' && 'باقة الأعمال'}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {user?.articles_limit} مقالة شهرياً
              </p>
            </div>
            {user?.subscription_tier === 'free' && (
              <Link to="/dashboard/settings?tab=subscription">
                <Button variant="outline">
                  ترقية الباقة
                </Button>
              </Link>
            )}
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-sm mb-2">
              <span className="text-gray-600">الاستخدام الشهري</span>
              <span className="font-medium text-gray-900">
                {user?.articles_count} / {user?.articles_limit}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div
                className="bg-primary-600 h-3 rounded-full transition-all"
                style={{
                  width: `${usageStats?.usage_percentage || 0}%`
                }}
              />
            </div>
          </div>
        </CardBody>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-bold text-gray-900">إجراءات سريعة</h2>
        </CardHeader>
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Link
              to="/dashboard/create"
              className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <div className="bg-primary-100 p-3 rounded-lg ml-4">
                <PlusCircle className="w-6 h-6 text-primary-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">إنشاء مقال جديد</h3>
                <p className="text-sm text-gray-600">
                  ابدأ في كتابة محتوى جديد بالذكاء الاصطناعي
                </p>
              </div>
            </Link>

            <Link
              to="/dashboard/articles"
              className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <div className="bg-green-100 p-3 rounded-lg ml-4">
                <FileText className="w-6 h-6 text-green-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">عرض المقالات</h3>
                <p className="text-sm text-gray-600">
                  تصفح وإدارة مقالاتك المنشورة
                </p>
              </div>
            </Link>
          </div>
        </CardBody>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <h2 className="text-xl font-bold text-gray-900">النشاط الأخير</h2>
        </CardHeader>
        <CardBody>
          <div className="text-center py-8 text-gray-500">
            <FileText className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>لا توجد أنشطة حديثة</p>
            <p className="text-sm mt-1">ابدأ بإنشاء مقالك الأول!</p>
          </div>
        </CardBody>
      </Card>
    </div>
  )
}

