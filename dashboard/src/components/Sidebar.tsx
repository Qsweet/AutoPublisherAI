import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  FileText, 
  PlusCircle, 
  Settings, 
  BarChart3,
  LogOut 
} from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { cn } from '@/utils/cn'

const menuItems = [
  {
    name: 'لوحة التحكم',
    path: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'إنشاء مقال',
    path: '/dashboard/create',
    icon: PlusCircle,
  },
  {
    name: 'المقالات',
    path: '/dashboard/articles',
    icon: FileText,
  },
  {
    name: 'الإحصائيات',
    path: '/dashboard/analytics',
    icon: BarChart3,
  },
  {
    name: 'الإعدادات',
    path: '/dashboard/settings',
    icon: Settings,
  },
]

export function Sidebar() {
  const location = useLocation()
  const { user, logout } = useAuthStore()

  return (
    <div className="flex flex-col h-full bg-white border-l border-gray-200">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-primary-600">
          AutoPublisher AI
        </h1>
        <p className="text-sm text-gray-600 mt-1">
          النشر الذكي
        </p>
      </div>

      {/* User Info */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-3 space-x-reverse">
          <div className="w-10 h-10 rounded-full bg-primary-100 flex items-center justify-center">
            <span className="text-primary-600 font-medium">
              {user?.email.charAt(0).toUpperCase()}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-gray-900 truncate">
              {user?.full_name || user?.email}
            </p>
            <p className="text-xs text-gray-500">
              {user?.subscription_tier === 'free' && 'الباقة المجانية'}
              {user?.subscription_tier === 'basic' && 'الباقة الأساسية'}
              {user?.subscription_tier === 'pro' && 'الباقة الاحترافية'}
              {user?.subscription_tier === 'enterprise' && 'باقة الأعمال'}
            </p>
          </div>
        </div>
      </div>

      {/* Menu Items */}
      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path
          
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center space-x-3 space-x-reverse px-4 py-3 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-gray-700 hover:bg-gray-50'
              )}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{item.name}</span>
            </Link>
          )
        })}
      </nav>

      {/* Usage Stats */}
      {user && (
        <div className="p-4 border-t border-gray-200">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-600">الاستخدام الشهري</span>
              <span className="text-sm font-medium text-gray-900">
                {user.articles_count} / {user.articles_limit}
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-primary-600 h-2 rounded-full transition-all"
                style={{
                  width: `${(user.articles_count / user.articles_limit) * 100}%`
                }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {user.remaining_articles} مقالة متبقية
            </p>
          </div>
        </div>
      )}

      {/* Logout */}
      <div className="p-4 border-t border-gray-200">
        <button
          onClick={logout}
          className="flex items-center space-x-3 space-x-reverse w-full px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
        >
          <LogOut className="w-5 h-5" />
          <span className="font-medium">تسجيل الخروج</span>
        </button>
      </div>
    </div>
  )
}

