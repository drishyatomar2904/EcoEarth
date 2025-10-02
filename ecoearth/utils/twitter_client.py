import tweepy
import random
from datetime import datetime, timedelta
import re

class TwitterClient:
    def __init__(self, bearer_token):
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.authenticated = False
        
        try:
            # Test authentication
            test_tweets = self.client.search_recent_tweets("environment", max_results=1)
            self.authenticated = True
            print("✅ Twitter API connected successfully!")
        except Exception as e:
            print(f"❌ Twitter API failed: {e}")
            self.authenticated = False
    
    def get_environmental_tweets(self, query="environment", max_results=50):
        """Get real environmental tweets from Twitter API"""
        if not self.authenticated:
            return self._get_sample_tweets(max_results)
        
        try:
            # Twitter API v2 search
            response = self.client.search_recent_tweets(
                query=f"{query} -is:retweet",
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'text'],
                user_fields=['username', 'name'],
                expansions=['author_id']
            )
            
            if not response.data:
                return self._get_sample_tweets(max_results)
                
            tweets = []
            users = {user.id: user for user in response.includes['users']} if response.includes else {}
            
            for tweet in response.data:
                user = users.get(tweet.author_id)
                tweets.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author': user.username if user else 'unknown',
                    'author_name': user.name if user else 'Unknown',
                    'timestamp': tweet.created_at.isoformat(),
                    'likes': tweet.public_metrics['like_count'],
                    'retweets': tweet.public_metrics['retweet_count'],
                    'replies': tweet.public_metrics['reply_count'],
                    'sentiment': self._analyze_sentiment(tweet.text),
                    'hashtags': self._extract_hashtags(tweet.text),
                    'topic': self._classify_topic(tweet.text),
                    'engagement_score': self._calculate_engagement(tweet.public_metrics),
                    'platform': 'twitter'
                })
            
            print(f"✅ Fetched {len(tweets)} real tweets from Twitter")
            return tweets
            
        except Exception as e:
            print(f"Twitter API error: {e}")
            return self._get_sample_tweets(max_results)
    
    def _get_sample_tweets(self, max_results):
        """Generate realistic sample tweets"""
        environmental_keywords = [
            "climate change", "global warming", "plastic pollution", "renewable energy",
            "sustainable", "eco friendly", "carbon emissions", "clean energy",
            "environment", "planet", "green", "recycle", "sustainability"
        ]
        
        hashtags = [
            "#ClimateAction", "#Environment", "#Sustainability", "#GoGreen",
            "#EcoFriendly", "#SaveThePlanet", "#ClimateChange", "#GreenEnergy",
            "#ZeroWaste", "#PlanetEarth", "#Nature", "#EcoWarrior"
        ]
        
        tweets = []
        for i in range(max_results):
            keyword = random.choice(environmental_keywords)
            sentiment = random.choice(["positive", "negative", "neutral"])
            
            tweet_templates = {
                "positive": [
                    f"Amazing to see progress in {keyword}! The future looks bright 🌱 {random.choice(hashtags)}",
                    f"Inspired by the innovations in {keyword}. Every small action counts! 💚 {random.choice(hashtags)}",
                    f"Just learned about incredible {keyword} solutions. Hope is growing! 🌍 {random.choice(hashtags)}"
                ],
                "negative": [
                    f"Deeply concerned about {keyword}. We need urgent action now! 😔 {random.choice(hashtags)}",
                    f"Another alarming report on {keyword}. When will we wake up? 😠 {random.choice(hashtags)}",
                    f"Frustrated by the slow progress on {keyword}. Time for real change! ⏰ {random.choice(hashtags)}"
                ],
                "neutral": [
                    f"Interesting discussion about {keyword} developments. What are your thoughts? 💭 {random.choice(hashtags)}",
                    f"New research on {keyword} published today. Important findings. 📊 {random.choice(hashtags)}",
                    f"Community event about {keyword} solutions this weekend. Who's going? 🗓️ {random.choice(hashtags)}"
                ]
            }
            
            text = random.choice(tweet_templates[sentiment])
            
            tweets.append({
                'id': f"twitter_{i}_{int(datetime.now().timestamp())}",
                'text': text,
                'author': f"user_{random.randint(10000, 99999)}",
                'author_name': f"Eco Enthusiast {random.randint(1, 1000)}",
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat(),
                'likes': random.randint(5, 1000),
                'retweets': random.randint(1, 200),
                'replies': random.randint(1, 50),
                'sentiment': sentiment,
                'hashtags': [tag for tag in hashtags if tag in text],
                'topic': keyword,
                'engagement_score': random.randint(10, 1200),
                'platform': 'twitter'
            })
        
        print(f"📊 Generated {len(tweets)} sample tweets")
        return tweets
    
    def _analyze_sentiment(self, text):
        """Simple sentiment analysis"""
        positive_words = ['amazing', 'great', 'love', 'hope', 'progress', 'inspired', 'solution', 'better', 'awesome', 'brilliant']
        negative_words = ['concerned', 'alarming', 'frustrated', 'worried', 'problem', 'crisis', 'urgent', 'terrible', 'disaster']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    def _extract_hashtags(self, text):
        """Extract hashtags from tweet text"""
        return re.findall(r'#\w+', text)
    
    def _classify_topic(self, text):
        """Classify tweet into environmental topics"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['climate', 'warming', 'carbon', 'emission', 'temperature']):
            return "Climate Change"
        elif any(word in text_lower for word in ['plastic', 'pollution', 'waste', 'recycle', 'garbage']):
            return "Plastic Pollution"
        elif any(word in text_lower for word in ['energy', 'renewable', 'solar', 'wind', 'clean energy']):
            return "Renewable Energy"
        elif any(word in text_lower for word in ['sustainable', 'eco', 'green', 'environmental']):
            return "Sustainability"
        elif any(word in text_lower for word in ['ocean', 'sea', 'marine', 'water']):
            return "Ocean Conservation"
        else:
            return "Environmental Awareness"
    
    def _calculate_engagement(self, metrics):
        """Calculate engagement score"""
        return (metrics['like_count'] + 
                metrics['retweet_count'] * 2 + 
                metrics['reply_count'] * 3)