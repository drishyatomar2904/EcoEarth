import groq
import json
import random

class GroqClient:
    def __init__(self, api_key):
        try:
            self.client = groq.Groq(api_key=api_key)
            self.authenticated = True
            print(" Groq AI connected successfully!")
        except Exception as e:
            print(f" Groq AI failed: {e}")
            self.authenticated = False
    
    def analyze_trends(self, posts, news):
        """Analyze environmental trends using Groq AI"""
        if not self.authenticated:
            return self._get_sample_analysis(posts, news)
        
        try:
            # Prepare data for AI analysis
            topics = [post['topic'] for post in posts]
            sentiments = [post['sentiment'] for post in posts]
            
            prompt = f"""
            Analyze this environmental social media data and provide insights:
            
            Social Media Posts: {len(posts)} posts
            Dominant Topics: {', '.join(set(topics))}
            Sentiment Distribution: Positive: {sentiments.count('positive')}, Negative: {sentiments.count('negative')}, Neutral: {sentiments.count('neutral')}
            News Articles: {len(news)} articles
            
            Please provide:
            1. A concise summary of current environmental discourse
            2. Key trends and patterns
            3. Actionable recommendations for environmental organizations
            4. Sentiment breakdown
            """
            
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama3-8b-8192",
                max_tokens=500,
                temperature=0.7
            )
            
            analysis_text = response.choices[0].message.content
            
            return {
                "summary": analysis_text.split('\n')[0] if analysis_text else "AI analysis unavailable",
                "dominant_topic": max(set(topics), key=topics.count) if topics else "environment",
                "sentiment_breakdown": {
                    "positive": sentiments.count("positive"),
                    "negative": sentiments.count("negative"), 
                    "neutral": sentiments.count("neutral")
                },
                "engagement_trend": random.choice(["rising", "stable", "falling"]),
                "recommendations": [
                    "Focus on practical solutions rather than just highlighting problems",
                    "Collaborate with local influencers to amplify reach",
                    "Share success stories to maintain positive momentum"
                ],
                "ai_generated": True
            }
            
        except Exception as e:
            print(f"Groq AI error: {e}")
            return self._get_sample_analysis(posts, news)
    
    def _get_sample_analysis(self, posts, news):
        """Generate sample AI analysis"""
        topics = list(set([post['topic'] for post in posts]))
        dominant_topic = max(topics, key=topics.count) if topics else "environment"
        
        sentiments = [post['sentiment'] for post in posts]
        positive_rate = sentiments.count("positive") / len(sentiments) * 100 if sentiments else 0
        
        analysis_templates = [
            f"Social media shows strong concern about {dominant_topic}, with {positive_rate:.1f}% positive sentiment. The conversation is primarily driven by grassroots activists sharing practical solutions.",
            f"Current environmental discourse focuses heavily on {dominant_topic}. Public sentiment is cautiously optimistic, with many users sharing success stories and calling for policy action.",
            f"Analysis reveals growing public awareness about {dominant_topic}. Social media engagement correlates with recent news coverage, suggesting media amplification of public concerns."
        ]
        
        return {
            "summary": random.choice(analysis_templates),
            "dominant_topic": dominant_topic,
            "sentiment_breakdown": {
                "positive": sentiments.count("positive"),
                "negative": sentiments.count("negative"), 
                "neutral": sentiments.count("neutral")
            },
            "engagement_trend": random.choice(["rising", "stable", "falling"]),
            "recommendations": [
                "Focus on practical solutions rather than just highlighting problems",
                "Collaborate with local influencers to amplify reach",
                "Share success stories to maintain positive momentum"
            ],
            "ai_generated": False
        }
