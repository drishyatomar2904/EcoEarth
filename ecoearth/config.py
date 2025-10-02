import os

class Config:
    # Reddit API credentials
    REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID', '')
    REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET', '')
    REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT', 'EcoEarthApp v1.0')
    
    # Groq AI
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # News API
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')
    
    # Subreddits to monitor
    ENVIRONMENTAL_SUBREDDITS = [
        'environment', 'climate', 'sustainability', 'renewableenergy',
        'ZeroWaste', 'permaculture', 'greeninvestor', 'climateaction',
        'ecology', 'conservation'
    ]
    
    # Primary data source
    PRIMARY_SOCIAL_SOURCE = 'reddit'
