import axios, { AxiosInstance, AxiosError } from 'axios'
import type { LoginCredentials, RegisterData, TokenResponse, User, UsageStats } from '@/types/user'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8005'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as any

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true

          try {
            const refreshToken = localStorage.getItem('refresh_token')
            if (refreshToken) {
              const response = await this.refreshToken(refreshToken)
              localStorage.setItem('access_token', response.access_token)
              localStorage.setItem('refresh_token', response.refresh_token)

              originalRequest.headers.Authorization = `Bearer ${response.access_token}`
              return this.client(originalRequest)
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            window.location.href = '/login'
            return Promise.reject(refreshError)
          }
        }

        return Promise.reject(error)
      }
    )
  }

  // Auth endpoints
  async register(data: RegisterData): Promise<User> {
    const response = await this.client.post<User>('/api/v1/auth/register', data)
    return response.data
  }

  async login(credentials: LoginCredentials): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/api/v1/auth/login', credentials)
    return response.data
  }

  async refreshToken(refreshToken: string): Promise<TokenResponse> {
    const response = await this.client.post<TokenResponse>('/api/v1/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/v1/auth/me')
    return response.data
  }

  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await this.client.put<User>('/api/v1/auth/me', data)
    return response.data
  }

  async updatePassword(currentPassword: string, newPassword: string): Promise<void> {
    await this.client.put('/api/v1/auth/me/password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  }

  async getUsageStats(): Promise<UsageStats> {
    const response = await this.client.get<UsageStats>('/api/v1/auth/me/usage')
    return response.data
  }

  // Content endpoints (to be implemented)
  async generateArticle(topic: string): Promise<any> {
    const response = await this.client.post('/api/content/generate', { topic })
    return response.data
  }

  async getArticles(): Promise<any[]> {
    const response = await this.client.get('/api/articles')
    return response.data
  }

  async publishArticle(articleId: string, platforms: string[]): Promise<any> {
    const response = await this.client.post('/api/publish', {
      article_id: articleId,
      platforms,
    })
    return response.data
  }
}

export const api = new ApiService()

