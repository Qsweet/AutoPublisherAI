"""
Content Generator Service

This is the CORE ENGINE of the content service.
It orchestrates AI models to create professional, SEO-optimized articles.

This module implements techniques used by senior content strategists
with 15+ years of experience in SEO and content marketing.
"""

import logging
import asyncio
from typing import Optional, List
from openai import AsyncOpenAI
from datetime import datetime

from app.core.config import settings
from app.models.article import (
    ArticleGenerationRequest,
    ArticleGenerationResponse,
    ArticleSection,
    FAQItem,
    GeneratedImage,
    ArticleMetadata,
    KeywordAnalysis
)
from app.services.seo_analyzer import SEOAnalyzer

logger = logging.getLogger(__name__)


class ContentGenerator:
    """
    Advanced AI-powered content generation engine.
    
    This class is the heart of the content service. It combines:
    - Advanced prompt engineering
    - SEO best practices
    - Content structure optimization
    - Multi-step generation pipeline
    """
    
    def __init__(self):
        """Initialize the content generator."""
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.seo_analyzer = SEOAnalyzer()
        
    async def generate_article(
        self, 
        request: ArticleGenerationRequest
    ) -> ArticleGenerationResponse:
        """
        Generate a complete, SEO-optimized article.
        
        This is the main entry point. It orchestrates the entire
        content generation pipeline.
        
        Args:
            request: Article generation request with all parameters
            
        Returns:
            Complete article with all metadata and content
        """
        logger.info(f"Starting article generation for topic: {request.topic}")
        
        # Step 1: SEO Analysis
        logger.info("Step 1/5: Performing SEO analysis...")
        keyword_analysis = await self.seo_analyzer.analyze_topic(
            request.topic,
            request.language.value,
            request.seo_level
        )
        
        # Step 2: Generate Article Structure
        logger.info("Step 2/5: Creating article structure...")
        structure = await self._create_article_structure(
            request,
            keyword_analysis
        )
        
        # Step 3: Generate Main Content
        logger.info("Step 3/5: Generating main content...")
        content = await self._generate_main_content(
            request,
            keyword_analysis,
            structure
        )
        
        # Step 4: Generate FAQ (if requested)
        faq = None
        if request.include_faq:
            logger.info("Step 4/5: Generating FAQ section...")
            faq = await self._generate_faq(request, keyword_analysis)
        else:
            logger.info("Step 4/5: Skipping FAQ (not requested)")
        
        # Step 5: Generate Featured Image (if requested)
        featured_image = None
        if request.include_image:
            logger.info("Step 5/5: Generating featured image...")
            featured_image = await self._generate_featured_image(
                request.topic,
                keyword_analysis.primary_keyword
            )
        else:
            logger.info("Step 5/5: Skipping image (not requested)")
        
        # Create metadata
        metadata = self._create_metadata(
            content['title'],
            keyword_analysis,
            request.language.value
        )
        
        # Calculate statistics
        total_text = content['introduction'] + content['conclusion']
        for section in content['sections']:
            total_text += section.content
        
        word_count = len(total_text.split())
        reading_time = max(1, word_count // 200)  # Average reading speed
        
        # Assemble final response
        response = ArticleGenerationResponse(
            title=content['title'],
            introduction=content['introduction'],
            sections=content['sections'],
            conclusion=content['conclusion'],
            faq=faq,
            metadata=metadata,
            keyword_analysis=keyword_analysis,
            featured_image=featured_image,
            word_count=word_count,
            estimated_reading_time=reading_time,
            language=request.language
        )
        
        logger.info(f"Article generation completed! Word count: {word_count}")
        return response
    
    async def _create_article_structure(
        self,
        request: ArticleGenerationRequest,
        keywords: KeywordAnalysis
    ) -> List[str]:
        """
        Create an optimal article structure based on SEO analysis.
        
        This uses the "inverted pyramid" and "topic clustering" techniques
        that are proven to work in modern SEO.
        """
        # Use SEO analyzer to suggest structure
        suggested_headings = self.seo_analyzer.suggest_headings_structure(
            request.topic,
            [keywords.primary_keyword] + keywords.secondary_keywords,
            request.language.value
        )
        
        # Extract H2 headings (main sections)
        main_sections = [
            h['text'] for h in suggested_headings 
            if h['level'] == 'h2' and 'أسئلة' not in h['text'] and 'FAQ' not in h['text']
        ]
        
        return main_sections[:5]  # Limit to 5 main sections
    
    async def _generate_main_content(
        self,
        request: ArticleGenerationRequest,
        keywords: KeywordAnalysis,
        structure: List[str]
    ) -> dict:
        """
        Generate the main article content using advanced prompt engineering.
        
        This is where the MAGIC happens. The prompt is carefully crafted
        based on years of experience with GPT models and SEO.
        """
        # Construct the MEGA PROMPT
        prompt = self._build_content_generation_prompt(
            request,
            keywords,
            structure
        )
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(request.language.value)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS
            )
            
            # Parse the response
            generated_text = response.choices[0].message.content
            
            # Structure the content
            parsed_content = self._parse_generated_content(
                generated_text,
                structure
            )
            
            return parsed_content
            
        except Exception as e:
            logger.error(f"Error generating content: {e}", exc_info=True)
            raise
    
    def _build_content_generation_prompt(
        self,
        request: ArticleGenerationRequest,
        keywords: KeywordAnalysis,
        structure: List[str]
    ) -> str:
        """
        Build the ultimate content generation prompt.
        
        This prompt incorporates advanced techniques:
        - Role assignment (persona)
        - Context setting
        - Constraint specification
        - Output format definition
        - SEO requirements
        """
        lang_name = "العربية" if request.language.value == "ar" else "English"
        
        prompt = f"""أنت كاتب محتوى محترف ومتخصص في تحسين محركات البحث (SEO) بخبرة تزيد عن 15 عامًا.

**المهمة:**
اكتب مقالًا احترافيًا ومفصلًا حول الموضوع التالي: "{request.topic}"

**المتطلبات الإلزامية:**

1. **اللغة:** {lang_name}
2. **عدد الكلمات المستهدف:** {request.target_length} كلمة تقريبًا
3. **الأسلوب:** {request.tone.value}
4. **الجمهور المستهدف:** {request.target_audience or 'عام'}

**تحسين SEO:**

- **الكلمة المفتاحية الرئيسية:** {keywords.primary_keyword}
- **كلمات مفتاحية ثانوية:** {', '.join(keywords.secondary_keywords[:5])}
- **كلمات مفتاحية طويلة الذيل:** {', '.join(keywords.long_tail_keywords[:3])}

يجب دمج هذه الكلمات بشكل طبيعي في المحتوى بكثافة 1-2%.

**البنية المطلوبة:**

1. **عنوان جذاب** (يحتوي على الكلمة المفتاحية الرئيسية)
2. **مقدمة قوية** (100-150 كلمة) تجيب مباشرة على السؤال الرئيسي
3. **الأقسام الرئيسية:**
"""
        
        for i, section_title in enumerate(structure, 1):
            prompt += f"\n   {i}. {section_title}"
        
        prompt += f"""

4. **خاتمة موجزة** (80-100 كلمة) تلخص النقاط الرئيسية

**معايير الجودة:**

- استخدم فقرات قصيرة (2-3 جمل لكل فقرة)
- أضف أمثلة عملية وواقعية
- استخدم قوائم نقطية عند الحاجة
- اكتب بأسلوب واضح ومباشر
- تجنب الحشو والتكرار
- كل قسم يجب أن يحتوي على 200-300 كلمة

**التنسيق:**

استخدم التنسيق التالي بدقة:

```
العنوان: [العنوان هنا]

المقدمة:
[نص المقدمة]

## [عنوان القسم الأول]
[محتوى القسم]

## [عنوان القسم الثاني]
[محتوى القسم]

[... بقية الأقسام]

الخاتمة:
[نص الخاتمة]
```

ابدأ الآن بكتابة المقال:"""
        
        return prompt
    
    def _get_system_prompt(self, language: str) -> str:
        """Get the system prompt that defines the AI's role."""
        if language == "ar":
            return """أنت كاتب محتوى محترف متخصص في إنشاء مقالات عالية الجودة ومحسّنة لمحركات البحث.
لديك خبرة واسعة في كتابة المحتوى العربي بأسلوب احترافي وجذاب.
تلتزم دائمًا بأفضل ممارسات SEO وتكتب محتوى يفيد القارئ ويحقق نتائج ممتازة في محركات البحث."""
        else:
            return """You are a professional content writer specialized in creating high-quality, SEO-optimized articles.
You have extensive experience in writing engaging and professional content.
You always follow SEO best practices and create content that benefits readers and ranks well in search engines."""
    
    def _parse_generated_content(
        self,
        generated_text: str,
        structure: List[str]
    ) -> dict:
        """
        Parse the generated text into structured components.
        
        This extracts title, introduction, sections, and conclusion.
        """
        lines = generated_text.split('\n')
        
        # Extract title
        title = ""
        for line in lines:
            if line.strip().startswith('العنوان:') or line.strip().startswith('Title:'):
                title = line.split(':', 1)[1].strip()
                break
            elif line.strip() and not line.strip().startswith('#'):
                title = line.strip()
                break
        
        # Extract introduction
        intro_start = -1
        intro_end = -1
        for i, line in enumerate(lines):
            if 'مقدمة' in line.lower() or 'introduction' in line.lower():
                intro_start = i + 1
            elif intro_start > 0 and line.strip().startswith('##'):
                intro_end = i
                break
        
        introduction = ""
        if intro_start > 0 and intro_end > intro_start:
            introduction = '\n'.join(lines[intro_start:intro_end]).strip()
        
        # Extract sections
        sections = []
        current_section = None
        current_content = []
        
        for line in lines:
            if line.strip().startswith('##'):
                # Save previous section
                if current_section:
                    sections.append(ArticleSection(
                        heading=current_section,
                        content='\n'.join(current_content).strip(),
                        heading_level=2
                    ))
                # Start new section
                current_section = line.replace('##', '').strip()
                current_content = []
            elif current_section and line.strip() and not line.strip().startswith('خاتمة') and not line.strip().startswith('Conclusion'):
                current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections.append(ArticleSection(
                heading=current_section,
                content='\n'.join(current_content).strip(),
                heading_level=2
            ))
        
        # Extract conclusion
        conclusion = ""
        for i, line in enumerate(lines):
            if 'خاتمة' in line.lower() or 'conclusion' in line.lower():
                conclusion = '\n'.join(lines[i+1:]).strip()
                break
        
        return {
            'title': title or "مقال بدون عنوان",
            'introduction': introduction or "مقدمة قيد الإنشاء...",
            'sections': sections,
            'conclusion': conclusion or "خاتمة قيد الإنشاء..."
        }
    
    async def _generate_faq(
        self,
        request: ArticleGenerationRequest,
        keywords: KeywordAnalysis
    ) -> List[FAQItem]:
        """
        Generate FAQ section based on "People Also Ask" strategy.
        
        This is a powerful SEO technique that targets featured snippets.
        """
        prompt = f"""بناءً على الموضوع "{request.topic}" والكلمة المفتاحية "{keywords.primary_keyword}"،
اكتب 5 أسئلة شائعة (FAQ) مع إجابات مختصرة ومفيدة.

التنسيق:
س: [السؤال]
ج: [الإجابة]

س: [السؤال التالي]
ج: [الإجابة]

اكتب الأسئلة والأجوبة الآن:"""
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt(request.language.value)},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            faq_text = response.choices[0].message.content
            
            # Parse FAQ
            faq_items = []
            lines = faq_text.split('\n')
            current_q = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('س:') or line.startswith('Q:'):
                    current_q = line.split(':', 1)[1].strip()
                elif (line.startswith('ج:') or line.startswith('A:')) and current_q:
                    answer = line.split(':', 1)[1].strip()
                    faq_items.append(FAQItem(question=current_q, answer=answer))
                    current_q = None
            
            return faq_items[:5]
            
        except Exception as e:
            logger.error(f"Error generating FAQ: {e}")
            return []
    
    async def _generate_featured_image(
        self,
        topic: str,
        primary_keyword: str
    ) -> Optional[GeneratedImage]:
        """
        Generate a featured image using DALL-E 3.
        
        The image prompt is carefully crafted to create professional,
        relevant images that enhance the article.
        """
        # Create image prompt
        image_prompt = f"Professional, modern illustration representing: {primary_keyword}. Clean, minimalist style, high quality, suitable for blog article header."
        
        try:
            response = await self.client.images.generate(
                model=settings.OPENAI_IMAGE_MODEL,
                prompt=image_prompt,
                size="1792x1024",
                quality="standard",
                n=1
            )
            
            image_url = response.data[0].url
            
            return GeneratedImage(
                url=image_url,
                prompt=image_prompt,
                alt_text=f"صورة توضيحية عن {primary_keyword}",
                width=1792,
                height=1024
            )
            
        except Exception as e:
            logger.error(f"Error generating image: {e}")
            return None
    
    def _create_metadata(
        self,
        title: str,
        keywords: KeywordAnalysis,
        language: str
    ) -> ArticleMetadata:
        """Create SEO metadata for the article."""
        
        meta_description = self.seo_analyzer.generate_meta_description(
            title,
            keywords.primary_keyword,
            language
        )
        
        slug = self.seo_analyzer.generate_slug(title, language)
        
        tags = [keywords.primary_keyword] + keywords.secondary_keywords[:5]
        
        return ArticleMetadata(
            title=title[:60],  # Ensure within limit
            meta_description=meta_description,
            slug=slug,
            tags=tags,
            categories=[keywords.primary_keyword]
        )

