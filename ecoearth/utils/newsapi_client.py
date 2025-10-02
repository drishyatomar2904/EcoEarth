import requests
import random
from datetime import datetime, timedelta
import json

class NewsAPIClient:
    def __init__(self, api_key):
        self.api_key = api_key
    
    def get_environmental_news(self, query="environment", limit=20):
        """Get environmental news articles"""
        try:
            return self._get_sample_news(limit)
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return self._get_sample_news(limit)
    
    def _get_sample_news(self, limit):
        """Generate realistic sample news articles"""
        topics = [
            "Climate Change", "Renewable Energy", "Plastic Pollution", 
            "Wildlife Conservation", "Sustainable Development", "Clean Air",
            "Ocean Protection", "Green Technology", "Carbon Emissions"
        ]
        
        sources = [
            "Eco News Network", "Green Planet Daily", "Sustainable Times",
            "Environmental Digest", "Climate Today", "Earth Watch"
        ]
        
        news = []
        for i in range(limit):
            topic = random.choice(topics)
            sentiment = random.choice(["positive", "negative", "neutral"])
            
            title_templates = {
                "positive": [
                    f"Breakthrough in {topic} Offers New Hope",
                    f"Community Achieves Remarkable Success in {topic} Initiative",
                    f"Innovative Solution Transforms {topic} Landscape"
                ],
                "negative": [
                    f"Alarming Report Reveals {topic} Crisis Worsening",
                    f"Urgent Action Needed as {topic} Reaches Critical Levels",
                    f"New Study Shows Disturbing Trends in {topic}"
                ],
                "neutral": [
                    f"Experts Discuss Latest Developments in {topic}",
                    f"New Research Sheds Light on {topic} Challenges",
                    f"Global Summit Addresses {topic} Solutions"
                ]
            }
            
            title = random.choice(title_templates[sentiment])
            
            news.append({
                "id": f"news_{i}",
                "title": title,
                "source": random.choice(sources),
                "published_at": (datetime.now() - timedelta(hours=random.randint(0, 48))).isoformat(),
                "url": f"https://example.com/news/{i}",
                "sentiment": sentiment,
                "topic": topic,
                "impact_score": random.randint(1, 100)
            })
        
        return news
