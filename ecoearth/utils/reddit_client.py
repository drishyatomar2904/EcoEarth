import praw
import random
from datetime import datetime, timedelta
import re

class RedditClient:
    def __init__(self, client_id, client_secret, user_agent):
        self.authenticated = False
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        
        if client_id and client_secret:
            try:
                self.reddit = praw.Reddit(
                    client_id=client_id,
                    client_secret=client_secret,
                    user_agent=user_agent
                )
                # Test authentication
                self.reddit.user.me()
                self.authenticated = True
                print("✅ Reddit API connected successfully!")
            except Exception as e:
                print(f"❌ Reddit API failed: {e}")
                self.authenticated = False
        else:
            print("⚠️ Reddit credentials not provided - using sample data")
            self.authenticated = False
    
    def get_environmental_posts(self, limit=50):
        """Get environmental posts from Reddit"""
        if not self.authenticated:
            return self._get_sample_posts(limit)
        
        try:
            posts = []
            subreddits = ['environment', 'climate', 'sustainability', 'renewableenergy']
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    for post in subreddit.hot(limit=limit//len(subreddits)):
                        if len(posts) >= limit:
                            break
                            
                        posts.append({
                            'id': post.id,
                            'title': post.title,
                            'text': post.selftext,
                            'author': str(post.author),
                            'subreddit': subreddit_name,
                            'timestamp': datetime.fromtimestamp(post.created_utc).isoformat(),
                            'upvotes': post.score,
                            'comments': post.num_comments,
                            'url': post.url,
                            'sentiment': self._analyze_sentiment(post.title + " " + post.selftext),
                            'hashtags': self._extract_hashtags(post.title + " " + post.selftext),
                            'topic': self._classify_topic(post.title + " " + post.selftext),
                            'engagement_score': self._calculate_engagement(post.score, post.num_comments),
                            'platform': 'reddit',
                            'flair': post.link_flair_text
                        })
                except Exception as e:
                    print(f"Error fetching from r/{subreddit_name}: {e}")
                    continue
            
            print(f"✅ Fetched {len(posts)} real posts from Reddit")
            return posts
            
        except Exception as e:
            print(f"Reddit API error: {e}")
            return self._get_sample_posts(limit)
    
    def _get_sample_posts(self, max_results):
        """Generate realistic Reddit posts"""
        environmental_topics = [
            "climate change", "global warming", "plastic pollution", "renewable energy",
            "sustainable living", "carbon emissions", "clean energy", "biodiversity",
            "conservation", "green technology", "zero waste", "ocean conservation"
        ]
        
        subreddits = ['environment', 'climate', 'sustainability', 'renewableenergy', 'ZeroWaste']
        
        posts = []
        for i in range(max_results):
            topic = random.choice(environmental_topics)
            sentiment = random.choice(["positive", "negative", "neutral"])
            subreddit = random.choice(subreddits)
            
            post_templates = {
                "positive": [
                    f"Amazing progress in {topic}! Communities are making real change happen",
                    f"Inspiring innovations in {topic} that give me hope for the future",
                    f"Just learned about groundbreaking {topic} solutions making a difference",
                    f"Community-led {topic} initiatives are showing incredible results"
                ],
                "negative": [
                    f"Deeply concerned about the latest {topic} reports and lack of action",
                    f"Another devastating study on {topic} - when will policymakers listen?",
                    f"Frustrated by the slow progress on {topic} despite clear evidence",
                    f"Alarming data about {topic} that requires urgent attention"
                ],
                "neutral": [
                    f"New research on {topic} published today - important findings",
                    f"Discussion: What are your thoughts on recent {topic} developments?",
                    f"Community event about {topic} solutions happening this weekend",
                    f"Analysis of corporate initiatives for {topic} - your perspectives?"
                ]
            }
            
            title = random.choice(post_templates[sentiment])
            text = self._generate_post_text(topic, sentiment)
            
            posts.append({
                'id': f"reddit_{i}_{int(datetime.now().timestamp())}",
                'title': title,
                'text': text,
                'author': f"u/eco_enthusiast_{random.randint(1000, 9999)}",
                'subreddit': f"r/{subreddit}",
                'timestamp': (datetime.now() - timedelta(hours=random.randint(0, 72))).isoformat(),
                'upvotes': random.randint(10, 5000),
                'comments': random.randint(5, 200),
                'url': f"https://reddit.com/r/{subreddit}/comments/sample",
                'sentiment': sentiment,
                'hashtags': self._extract_hashtags(title + " " + text),
                'topic': topic.title(),
                'engagement_score': random.randint(50, 5000),
                'platform': 'reddit',
                'flair': random.choice([None, "Discussion", "News", "Question", "Achievement"])
            })
        
        print(f"📊 Generated {len(posts)} sample Reddit posts")
        return posts
    
    def _generate_post_text(self, topic, sentiment):
        """Generate realistic Reddit post text"""
        text_templates = {
            "positive": [
                f"I've been following {topic} developments closely and wanted to share some encouraging news. The recent community initiatives and technological breakthroughs are truly inspiring. What other positive developments have you seen in this area?",
                f"As someone passionate about {topic}, I'm excited to see the progress being made. From local community actions to global policy changes, there's a lot to be hopeful about. Let's discuss the most promising solutions!",
                f"I just attended a conference on {topic} and came away feeling optimistic. The innovation and dedication in this field are incredible. Share your own hopeful stories below!"
            ],
            "negative": [
                f"I'm growing increasingly concerned about {topic}. The latest reports show we're not moving fast enough, and the consequences could be severe. What concrete actions can we take to accelerate change?",
                f"The new data on {topic} is alarming, to say the least. We need urgent action from governments, corporations, and individuals. How can we mobilize more effectively?",
                f"After reading the latest research on {topic}, I'm frustrated by the lack of meaningful progress. We have the solutions - why aren't we implementing them at scale?"
            ],
            "neutral": [
                f"I've been researching {topic} and found some interesting developments. There are multiple approaches being explored, each with pros and cons. What are your thoughts on the current state of this field?",
                f"New study published on {topic} raises some important questions. The methodology seems sound, but I'm curious about the practical implications. Let's discuss!",
                f"Community meeting about {topic} solutions yielded diverse perspectives. I'm compiling the key takeaways and would appreciate additional insights from this community."
            ]
        }
        
        return random.choice(text_templates[sentiment])
    
    def _analyze_sentiment(self, text):
        """Simple sentiment analysis"""
        positive_words = ['amazing', 'great', 'hope', 'progress', 'inspired', 'solution', 'better', 'awesome', 'encouraging', 'optimistic', 'exciting']
        negative_words = ['concerned', 'alarming', 'frustrated', 'worried', 'problem', 'crisis', 'urgent', 'devastating', 'slow', 'lack']
        
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
        """Extract hashtags from text"""
        return re.findall(r'#\w+', text)
    
    def _classify_topic(self, text):
        """Classify post into environmental topics"""
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
        elif any(word in text_lower for word in ['biodiversity', 'wildlife', 'species', 'conservation']):
            return "Biodiversity"
        else:
            return "Environmental Awareness"
    
    def _calculate_engagement(self, upvotes, comments):
        """Calculate engagement score for Reddit"""
        return upvotes + (comments * 5)