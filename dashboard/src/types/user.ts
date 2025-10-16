export enum SubscriptionTier {
  FREE = 'free',
  BASIC = 'basic',
  PRO = 'pro',
  ENTERPRISE = 'enterprise',
}

export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  subscription_tier: SubscriptionTier
  articles_count: number
  articles_limit: number
  remaining_articles: number
  created_at: string
  last_login: string | null
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  password: string
  full_name?: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UsageStats {
  articles_count: number
  articles_limit: number
  remaining_articles: number
  subscription_tier: SubscriptionTier
  usage_percentage: number
}

