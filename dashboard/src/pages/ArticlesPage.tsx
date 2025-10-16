import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '@/services/api'
import { Card, CardBody } from '@/components/Card'
import { Button } from '@/components/Button'
import { FileText, Calendar, Eye, PlusCircle } from 'lucide-react'

export function ArticlesPage() {
  const [articles, setArticles] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadArticles()
  }, [])

  const loadArticles = async () => {
    try {
      const data = await api.getArticles()
      setArticles(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'فشل في تحميل المقالات')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">مقالاتي</h1>
          <p className="text-gray-600 mt-1">
            إدارة ومراجعة جميع مقالاتك المنشورة
          </p>
        </div>
        <Link to="/dashboard/create">
          <Button>
            <PlusCircle className="w-5 h-5 ml-2" />
            إنشاء مقال جديد
          </Button>
        </Link>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Articles List */}
      {articles.length === 0 ? (
        <Card>
          <CardBody>
            <div className="text-center py-12">
              <FileText className="w-16 h-16 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                لا توجد مقالات بعد
              </h3>
              <p className="text-gray-600 mb-6">
                ابدأ بإنشاء مقالك الأول باستخدام الذكاء الاصطناعي
              </p>
              <Link to="/dashboard/create">
                <Button>
                  <PlusCircle className="w-5 h-5 ml-2" />
                  إنشاء مقال جديد
                </Button>
              </Link>
            </div>
          </CardBody>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {articles.map((article) => (
            <Card key={article.id} className="hover:shadow-md transition-shadow">
              <CardBody>
                {article.featured_image && (
                  <div className="aspect-video rounded-lg overflow-hidden bg-gray-100 mb-4">
                    <img
                      src={article.featured_image}
                      alt={article.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}

                <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">
                  {article.title}
                </h3>

                <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                  {article.excerpt || article.content?.substring(0, 150)}
                </p>

                <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
                  <div className="flex items-center">
                    <Calendar className="w-4 h-4 ml-1" />
                    {new Date(article.created_at).toLocaleDateString('ar-SA')}
                  </div>
                  <div className="flex items-center">
                    <Eye className="w-4 h-4 ml-1" />
                    {article.views || 0}
                  </div>
                </div>

                {article.tags && article.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {article.tags.slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs"
                      >
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}

                <div className="flex gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                  >
                    عرض
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="flex-1"
                  >
                    تعديل
                  </Button>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

