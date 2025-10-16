"""
Content Strategy Generator

This module uses AI to generate comprehensive content strategies.
"""

import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta, date
import uuid
from openai import AsyncOpenAI

from ..models.strategy import (
    StrategyRequest,
    ContentStrategy,
    ArticleIdea,
    WeeklyPlan,
    TrafficProjection,
    KeywordCluster,
    ContentType,
    PublishingFrequency
)


logger = logging.getLogger(__name__)


class StrategyGenerator:
    """
    AI-powered content strategy generator.
    
    Uses GPT-4 to analyze market, competitors, and generate comprehensive
    content strategies with keyword research and traffic projections.
    """
    
    def __init__(self, openai_api_key: str):
        """
        Initialize strategy generator.
        
        Args:
            openai_api_key: OpenAI API key
        """
        self.client = AsyncOpenAI(api_key=openai_api_key)
        self.model = "gpt-4-turbo-preview"
    
    async def generate_strategy(self, request: StrategyRequest) -> ContentStrategy:
        """
        Generate complete content strategy.
        
        Args:
            request: Strategy request parameters
            
        Returns:
            Complete content strategy
        """
        logger.info(f"Generating content strategy for {request.industry}")
        
        # Step 1: Generate keyword clusters
        keyword_clusters = await self._generate_keyword_clusters(request)
        
        # Step 2: Generate article ideas
        article_ideas = await self._generate_article_ideas(request, keyword_clusters)
        
        # Step 3: Create weekly plans
        weekly_plans = self._create_weekly_plans(article_ideas, request)
        
        # Step 4: Project traffic growth
        traffic_projections = self._project_traffic(request, len(article_ideas))
        
        # Step 5: Generate recommendations
        recommendations = await self._generate_recommendations(request, keyword_clusters)
        
        # Create strategy
        strategy = ContentStrategy(
            strategy_id=str(uuid.uuid4()),
            created_at=datetime.utcnow(),
            industry=request.industry,
            target_audience=request.target_audience,
            duration_days=request.duration_days,
            total_articles=len(article_ideas),
            keyword_clusters=keyword_clusters,
            weekly_plans=weekly_plans,
            traffic_projections=traffic_projections,
            summary=self._create_summary(request, article_ideas, traffic_projections),
            recommendations=recommendations
        )
        
        logger.info(f"Strategy generated: {strategy.total_articles} articles planned")
        
        return strategy
    
    async def _generate_keyword_clusters(
        self,
        request: StrategyRequest
    ) -> List[KeywordCluster]:
        """Generate keyword clusters for the strategy."""
        
        prompt = f"""
You are an expert SEO strategist. Generate keyword clusters for a content strategy.

Industry: {request.industry.value}
Target Audience: {request.target_audience}
Main Topics: {', '.join(request.main_topics)}
Language: {request.language}

Generate 5-8 keyword clusters. For each cluster:
1. Choose a main keyword with good search volume
2. Find 5-10 related long-tail keywords
3. Estimate monthly search volume
4. Assess SEO difficulty (easy/medium/hard)
5. Suggest number of articles for this cluster

Return ONLY a valid JSON array of clusters with this structure:
[
  {{
    "cluster_name": "Cluster Name",
    "main_keyword": "main keyword",
    "related_keywords": ["keyword 1", "keyword 2", ...],
    "search_volume": 10000,
    "difficulty": "medium",
    "article_count": 12
  }}
]
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert SEO strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            clusters_data = json.loads(content)
            
            # Convert to KeywordCluster objects
            clusters = [KeywordCluster(**cluster) for cluster in clusters_data]
            
            return clusters
            
        except Exception as e:
            logger.error(f"Error generating keyword clusters: {e}")
            # Return default clusters
            return [
                KeywordCluster(
                    cluster_name=topic,
                    main_keyword=topic.lower(),
                    related_keywords=[f"{topic.lower()} tips", f"best {topic.lower()}"],
                    search_volume=5000,
                    difficulty="medium",
                    article_count=10
                )
                for topic in request.main_topics[:5]
            ]
    
    async def _generate_article_ideas(
        self,
        request: StrategyRequest,
        keyword_clusters: List[KeywordCluster]
    ) -> List[ArticleIdea]:
        """Generate article ideas based on keyword clusters."""
        
        # Calculate total articles needed
        frequency_map = {
            PublishingFrequency.DAILY: 1,
            PublishingFrequency.EVERY_OTHER_DAY: 2,
            PublishingFrequency.THREE_TIMES_WEEK: 2.33,
            PublishingFrequency.TWICE_WEEK: 3.5,
            PublishingFrequency.WEEKLY: 7
        }
        
        days_between_posts = frequency_map[request.publishing_frequency]
        total_articles = int(request.duration_days / days_between_posts)
        
        # Generate article ideas for each cluster
        all_articles = []
        
        for cluster in keyword_clusters:
            articles_for_cluster = min(cluster.article_count, total_articles - len(all_articles))
            
            if articles_for_cluster <= 0:
                break
            
            cluster_articles = await self._generate_cluster_articles(
                request,
                cluster,
                articles_for_cluster
            )
            
            all_articles.extend(cluster_articles)
        
        # Sort by priority
        all_articles.sort(key=lambda x: x.priority, reverse=True)
        
        # Assign publish dates
        start_date = date.today()
        for i, article in enumerate(all_articles):
            days_offset = int(i * days_between_posts)
            article.suggested_publish_date = start_date + timedelta(days=days_offset)
        
        return all_articles[:total_articles]
    
    async def _generate_cluster_articles(
        self,
        request: StrategyRequest,
        cluster: KeywordCluster,
        count: int
    ) -> List[ArticleIdea]:
        """Generate article ideas for a specific cluster."""
        
        prompt = f"""
Generate {count} article ideas for this keyword cluster:

Cluster: {cluster.cluster_name}
Main Keyword: {cluster.main_keyword}
Related Keywords: {', '.join(cluster.related_keywords[:5])}
Industry: {request.industry.value}
Target Audience: {request.target_audience}
Language: {request.language}

For each article, provide:
1. Compelling, SEO-optimized title
2. Brief description (2-3 sentences)
3. Content type (blog_post, tutorial, guide, listicle, case_study, review, news, opinion)
4. Target keywords (3-5)
5. Estimated word count (800-3000)
6. SEO difficulty (easy/medium/hard)
7. Estimated monthly traffic potential
8. Priority score (1-10, based on traffic potential and difficulty)

Return ONLY a valid JSON array:
[
  {{
    "title": "Article Title",
    "description": "Brief description",
    "content_type": "blog_post",
    "keywords": ["keyword1", "keyword2"],
    "estimated_word_count": 1500,
    "difficulty": "medium",
    "estimated_traffic": 500,
    "priority": 8
  }}
]
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            articles_data = json.loads(content)
            
            # Convert to ArticleIdea objects
            articles = []
            for article_data in articles_data:
                article_data["suggested_publish_date"] = date.today()  # Temporary, will be updated
                articles.append(ArticleIdea(**article_data))
            
            return articles
            
        except Exception as e:
            logger.error(f"Error generating cluster articles: {e}")
            return []
    
    def _create_weekly_plans(
        self,
        articles: List[ArticleIdea],
        request: StrategyRequest
    ) -> List[WeeklyPlan]:
        """Create weekly content plans."""
        
        weeks = []
        start_date = date.today()
        articles_by_week = {}
        
        # Group articles by week
        for article in articles:
            week_num = (article.suggested_publish_date - start_date).days // 7 + 1
            if week_num not in articles_by_week:
                articles_by_week[week_num] = []
            articles_by_week[week_num].append(article)
        
        # Create weekly plans
        for week_num in sorted(articles_by_week.keys()):
            week_start = start_date + timedelta(days=(week_num - 1) * 7)
            week_end = week_start + timedelta(days=6)
            week_articles = articles_by_week[week_num]
            
            # Determine focus topic (most common keyword)
            all_keywords = []
            for article in week_articles:
                all_keywords.extend(article.keywords)
            focus_topic = max(set(all_keywords), key=all_keywords.count) if all_keywords else "General"
            
            # Calculate estimated traffic
            estimated_traffic = sum(article.estimated_traffic for article in week_articles)
            
            weeks.append(WeeklyPlan(
                week_number=week_num,
                start_date=week_start,
                end_date=week_end,
                articles=week_articles,
                focus_topic=focus_topic,
                estimated_traffic=estimated_traffic
            ))
        
        return weeks
    
    def _project_traffic(
        self,
        request: StrategyRequest,
        total_articles: int
    ) -> List[TrafficProjection]:
        """Project traffic growth over time."""
        
        current_traffic = request.current_traffic or 100
        months = request.duration_days // 30
        
        projections = []
        
        for month in range(1, months + 1):
            # Calculate articles in this month
            articles_per_month = total_articles // months
            
            # Estimate traffic growth (compound growth)
            # Assume each article brings 200-500 visitors/month after 30 days
            avg_traffic_per_article = 350
            new_traffic = articles_per_month * avg_traffic_per_article
            
            # Add cumulative effect (older articles gain more traffic)
            cumulative_boost = (month - 1) * 0.2  # 20% boost per month
            estimated_traffic = int(current_traffic + new_traffic * (1 + cumulative_boost))
            
            # Calculate growth percentage
            if month == 1:
                growth_percentage = (estimated_traffic - current_traffic) / current_traffic * 100
            else:
                prev_traffic = projections[-1].estimated_traffic
                growth_percentage = (estimated_traffic - prev_traffic) / prev_traffic * 100
            
            projections.append(TrafficProjection(
                month=month,
                estimated_traffic=estimated_traffic,
                growth_percentage=round(growth_percentage, 2),
                new_articles=articles_per_month
            ))
            
            current_traffic = estimated_traffic
        
        return projections
    
    async def _generate_recommendations(
        self,
        request: StrategyRequest,
        keyword_clusters: List[KeywordCluster]
    ) -> List[str]:
        """Generate strategic recommendations."""
        
        prompt = f"""
Based on this content strategy, provide 5-7 actionable recommendations:

Industry: {request.industry.value}
Target Audience: {request.target_audience}
Main Topics: {', '.join(request.main_topics)}
Publishing Frequency: {request.publishing_frequency.value}
Keyword Clusters: {len(keyword_clusters)}

Provide specific, actionable recommendations for:
1. Content optimization
2. SEO best practices
3. Audience engagement
4. Distribution channels
5. Performance tracking

Return ONLY a JSON array of strings:
["Recommendation 1", "Recommendation 2", ...]
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert content strategist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            recommendations = json.loads(content)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [
                "Focus on long-tail keywords with lower competition",
                "Maintain consistent publishing schedule",
                "Optimize articles for featured snippets",
                "Build internal linking structure",
                "Track performance with Google Analytics"
            ]
    
    def _create_summary(
        self,
        request: StrategyRequest,
        articles: List[ArticleIdea],
        projections: List[TrafficProjection]
    ) -> Dict[str, Any]:
        """Create strategy summary."""
        
        total_words = sum(article.estimated_word_count for article in articles)
        avg_words = total_words // len(articles) if articles else 0
        
        final_traffic = projections[-1].estimated_traffic if projections else 0
        total_growth = projections[-1].growth_percentage if projections else 0
        
        return {
            "duration_days": request.duration_days,
            "total_articles": len(articles),
            "total_words": total_words,
            "avg_words_per_article": avg_words,
            "publishing_frequency": request.publishing_frequency.value,
            "estimated_final_traffic": final_traffic,
            "total_growth_percentage": total_growth,
            "content_types": {
                content_type.value: len([a for a in articles if a.content_type == content_type])
                for content_type in ContentType
            }
        }

