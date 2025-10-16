import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import { Card, CardBody, CardHeader } from '@/components/Card'
import { Button } from '@/components/Button'
import { Input } from '@/components/Input'
import { Sparkles, Image, CheckCircle } from 'lucide-react'

export function CreateArticlePage() {
  const navigate = useNavigate()
  const [topic, setTopic] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [generatedArticle, setGeneratedArticle] = useState<any>(null)

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!topic.trim()) {
      setError('الرجاء إدخال موضوع المقال')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      const article = await api.generateArticle(topic)
      setGeneratedArticle(article)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'فشل في توليد المقال')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePublish = async (platforms: string[]) => {
    if (!generatedArticle) return

    try {
      await api.publishArticle(generatedArticle.id, platforms)
      navigate('/dashboard/articles')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'فشل في نشر المقال')
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">إنشاء مقال جديد</h1>
        <p className="text-gray-600 mt-1">
          استخدم الذكاء الاصطناعي لإنشاء محتوى احترافي ومحسّن لمحركات البحث
        </p>
      </div>

      {/* Topic Input */}
      {!generatedArticle && (
        <Card>
          <CardHeader>
            <div className="flex items-center">
              <Sparkles className="w-6 h-6 text-primary-600 ml-2" />
              <h2 className="text-xl font-bold text-gray-900">
                ما هو موضوع مقالك؟
              </h2>
            </div>
          </CardHeader>
          <CardBody>
            <form onSubmit={handleGenerate} className="space-y-4">
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              <div>
                <Input
                  label="موضوع المقال"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="مثال: أفضل استراتيجيات التسويق الرقمي في 2024"
                  disabled={isGenerating}
                />
                <p className="text-sm text-gray-500 mt-2">
                  اكتب موضوعاً واضحاً ومحدداً للحصول على أفضل النتائج
                </p>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h3 className="font-medium text-blue-900 mb-2">
                  💡 نصائح للحصول على أفضل النتائج:
                </h3>
                <ul className="text-sm text-blue-800 space-y-1">
                  <li>• كن محدداً في الموضوع</li>
                  <li>• استخدم كلمات مفتاحية واضحة</li>
                  <li>• حدد الجمهور المستهدف إن أمكن</li>
                </ul>
              </div>

              <Button
                type="submit"
                className="w-full"
                isLoading={isGenerating}
              >
                {isGenerating ? 'جاري التوليد...' : 'توليد المقال'}
              </Button>
            </form>
          </CardBody>
        </Card>
      )}

      {/* Generated Article Preview */}
      {generatedArticle && (
        <div className="space-y-6">
          {/* Success Message */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center">
            <CheckCircle className="w-6 h-6 text-green-600 ml-3" />
            <div>
              <h3 className="font-medium text-green-900">
                تم توليد المقال بنجاح!
              </h3>
              <p className="text-sm text-green-700">
                يمكنك الآن مراجعة المقال ونشره على المنصات المختلفة
              </p>
            </div>
          </div>

          {/* Article Content */}
          <Card>
            <CardHeader>
              <h2 className="text-2xl font-bold text-gray-900">
                {generatedArticle.title}
              </h2>
            </CardHeader>
            <CardBody className="space-y-4">
              {generatedArticle.featured_image && (
                <div className="relative aspect-video rounded-lg overflow-hidden bg-gray-100">
                  <img
                    src={generatedArticle.featured_image}
                    alt={generatedArticle.title}
                    className="w-full h-full object-cover"
                  />
                </div>
              )}

              <div className="prose max-w-none">
                <div dangerouslySetInnerHTML={{ __html: generatedArticle.content }} />
              </div>

              {generatedArticle.tags && generatedArticle.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-4 border-t">
                  {generatedArticle.tags.map((tag: string) => (
                    <span
                      key={tag}
                      className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                    >
                      #{tag}
                    </span>
                  ))}
                </div>
              )}
            </CardBody>
          </Card>

          {/* Publishing Options */}
          <Card>
            <CardHeader>
              <h2 className="text-xl font-bold text-gray-900">نشر المقال</h2>
            </CardHeader>
            <CardBody className="space-y-4">
              <p className="text-gray-600">
                اختر المنصات التي تريد النشر عليها:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <button
                  onClick={() => handlePublish(['wordpress'])}
                  className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <div className="bg-blue-100 p-3 rounded-lg ml-4">
                    <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12.158 12.786L9.46 20.625c.806.237 1.657.366 2.54.366 1.047 0 2.051-.18 2.986-.51-.024-.037-.046-.078-.065-.123l-2.763-7.572zm-5.14 3.63c-.858-1.568-1.343-3.37-1.343-5.29 0-1.928.487-3.74 1.346-5.313L9.5 16.416l-2.482 6.003zm11.292-9.12c0 1.513-.544 2.563-1.01 3.378-.622 1.015-1.206 1.872-1.206 2.887 0 1.13.867 2.184 2.097 2.184.056 0 .109-.007.163-.01-2.22 2.033-5.186 3.28-8.445 3.28-3.06 0-5.76-1.095-7.897-2.916.44.015.855.022 1.21.022 1.964 0 5.008-.239 5.008-.239.999-.058 1.118 1.41.119 1.528 0 0-1.006.118-2.125.176l6.76 20.103 4.062-12.178-2.89-7.925c-1-.058-1.947-.176-1.947-.176-.999-.059-1.118-1.586-.119-1.528 0 0 3.103.239 4.947.239 1.964 0 5.008-.239 5.008-.239.999-.058 1.118 1.41.119 1.528 0 0-1.006.118-2.125.176l6.71 19.963 1.853-6.19c.804-2.575 1.417-4.429 1.417-6.021z"/>
                    </svg>
                  </div>
                  <div className="text-right">
                    <h3 className="font-medium text-gray-900">WordPress</h3>
                    <p className="text-sm text-gray-600">نشر على موقعك</p>
                  </div>
                </button>

                <button
                  onClick={() => handlePublish(['instagram'])}
                  className="flex items-center p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
                >
                  <div className="bg-pink-100 p-3 rounded-lg ml-4">
                    <svg className="w-6 h-6 text-pink-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </div>
                  <div className="text-right">
                    <h3 className="font-medium text-gray-900">Instagram</h3>
                    <p className="text-sm text-gray-600">نشر كمنشور</p>
                  </div>
                </button>
              </div>

              <Button
                onClick={() => handlePublish(['wordpress', 'instagram'])}
                className="w-full"
                variant="primary"
              >
                نشر على جميع المنصات
              </Button>

              <Button
                onClick={() => setGeneratedArticle(null)}
                className="w-full"
                variant="outline"
              >
                إنشاء مقال جديد
              </Button>
            </CardBody>
          </Card>
        </div>
      )}
    </div>
  )
}

