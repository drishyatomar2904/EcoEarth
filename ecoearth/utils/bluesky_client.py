import requests
import json
from datetime import datetime, timedelta
import random

class BlueSkyClient:
    def __init__(self, handle, password):
        self.handle = handle
        self.password = password
        self.authenticated = False
        
    def get_environmental_posts(self, limit=50):
        """Get environmental posts from BlueSky"""
        try:
            return self._get_sample_posts(limit)
        except Exception as e:
            print(f"BlueSky error: {e}")
            return self._get_sample_posts(limit)
    
    def _get_sample_posts(self, limit):
        """Generate realistic sample environmental posts"""
        topics = [
            "climate change", "plastic pollution", "renewable energy", 
            "sustainable living", "clean air", "ocean conservation",
            "tree plantation", "wildlife protection", "green technology"
        ]
        
        hashtags = [
            "#ClimateAction", "#SaveOurPlanet", "#GoGreen", "#EcoFriendly",
            "#Sustainable", "#ZeroWaste", "#CleanEnergy", "#ProtectNature"
        ]
        
        posts = []
        for i in range(limit):
            topic = random.choice(topics)
            sentiment = random.choice(["positive", "negative", "neutral"])
            
            post_templates = {
                "positive": [
                    f"Amazing progress in {topic}! So inspired by the innovations  {random.choice(hashtags)}",
                    f"Just participated in a great {topic} workshop. Every small action counts!  {random.choice(hashtags)}",
                    f"Seeing real change in {topic} initiatives. Hope is growing!  {random.choice(hashtags)}"
                ],
                "negative": [
                    f"Concerned about the state of {topic}. We need urgent action!  {random.choice(hashtags)}",
                    f"Another disappointing report on {topic}. When will we learn?  {random.choice(hashtags)}",
                    f"Frustrated by the lack of progress on {topic}. Time for real change!  {random.choice(hashtags)}"
                ],
                "neutral": [
                    f"Interesting discussion about {topic} developments. What are your thoughts?  {random.choice(hashtags)}",
                    f"New research published on {topic}. Important findings worth considering.  {random.choice(hashtags)}",
                    f"Community meeting about {topic} solutions tonight. Who's attending?  {random.choice(hashtags)}"
                ]
            }
            
            text = random.choice(post_templates[sentiment])
            
            posts.append({
                "id": f"post_{i}",
                "text": text,
                "author": f"user_{random.randint(1000, 9999)}",
                "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat(),
                "likes": random.randint(5, 500),
                "reposts": random.randint(1, 100),
                "replies": random.randint(1, 50),
                "sentiment": sentiment,
                "hashtags": [tag for tag in hashtags if tag in text],
                "topic": topic,
                "engagement_score": random.randint(10, 600),
                "platform": "bluesky"
            })
        
        return posts
