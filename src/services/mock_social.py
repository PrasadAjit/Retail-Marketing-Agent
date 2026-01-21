"""
Mock Social Media Service
Simulates posting to Facebook, Instagram, Twitter with engagement tracking
"""
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum


class Platform(Enum):
    """Social media platforms"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"


@dataclass
class MockSocialPost:
    """Represents a social media post"""
    id: str
    campaign_id: str
    platform: str
    content: str
    image_url: Optional[str]
    hashtags: List[str]
    posted_at: str
    impressions: int
    likes: int
    comments: int
    shares: int
    clicks: int
    engagement_rate: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class MockSocialComment:
    """Represents a comment on a social post"""
    id: str
    post_id: str
    author_name: str
    content: str
    sentiment: str  # positive, neutral, negative
    created_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MockSocialMediaService:
    """Simulates social media posting and engagement"""
    
    POSITIVE_COMMENTS = [
        "Love this! 😍",
        "Great deal! Thanks for sharing!",
        "Just ordered mine! 🎉",
        "This is amazing! 💯",
        "Can't wait to visit!",
        "Awesome! When does this start?",
        "Perfect timing! Just what I needed!",
        "Your store is the best! ❤️",
        "This looks great! 👍",
        "Definitely checking this out!"
    ]
    
    NEUTRAL_COMMENTS = [
        "What are the store hours?",
        "Is this available online?",
        "Do you ship?",
        "More info please?",
        "Interesting...",
        "How long is this offer valid?",
        "What colors do you have?",
        "Is this still available?",
        "Where is your location?",
        "Can I use this with other offers?"
    ]
    
    NEGATIVE_COMMENTS = [
        "Wish the prices were better",
        "Out of stock again? 😞",
        "Shipping takes too long",
        "Had a bad experience last time",
        "Too expensive",
        "Not interested",
        "Meh...",
        "Already have this",
        "Seen better elsewhere"
    ]
    
    COMMENT_AUTHORS = [
        "Sarah Johnson", "Mike Williams", "Emily Davis", "James Brown", "Jessica Miller",
        "David Wilson", "Ashley Taylor", "Chris Anderson", "Amanda Thomas", "Ryan Martinez",
        "Jennifer Lopez", "Kevin Garcia", "Laura Rodriguez", "Brian Lee", "Nicole White"
    ]
    
    def __init__(self):
        self.posts: Dict[str, MockSocialPost] = {}
        self.comments: Dict[str, List[MockSocialComment]] = {}  # post_id -> comments
        self.campaigns: Dict[str, List[str]] = {}  # campaign_id -> post_ids
        self._post_counter = 0
        self._comment_counter = 0
    
    def create_post(
        self,
        platform: str,
        content: str,
        campaign_id: str,
        image_url: Optional[str] = None,
        hashtags: Optional[List[str]] = None
    ) -> MockSocialPost:
        """
        Create a social media post
        
        Args:
            platform: Social media platform (facebook, instagram, twitter)
            content: Post content/caption
            campaign_id: Associated campaign ID
            image_url: Optional image URL
            hashtags: Optional list of hashtags
        
        Returns:
            MockSocialPost object
        """
        self._post_counter += 1
        post_id = f"{platform.upper()}{self._post_counter:06d}"
        
        # Generate realistic engagement based on platform
        if platform == "facebook":
            base_impressions = random.randint(1000, 5000)
            engagement_multiplier = 0.05  # 5% engagement rate
        elif platform == "instagram":
            base_impressions = random.randint(2000, 8000)
            engagement_multiplier = 0.08  # 8% engagement rate
        else:  # twitter
            base_impressions = random.randint(500, 3000)
            engagement_multiplier = 0.03  # 3% engagement rate
        
        impressions = base_impressions
        total_engagements = int(impressions * engagement_multiplier)
        
        # Distribute engagements
        likes = int(total_engagements * random.uniform(0.6, 0.75))
        comments_count = int(total_engagements * random.uniform(0.05, 0.15))
        shares = int(total_engagements * random.uniform(0.05, 0.15))
        clicks = int(total_engagements * random.uniform(0.10, 0.25))
        
        engagement_rate = round((likes + comments_count + shares) / impressions * 100, 2)
        
        post = MockSocialPost(
            id=post_id,
            campaign_id=campaign_id,
            platform=platform,
            content=content,
            image_url=image_url,
            hashtags=hashtags or [],
            posted_at=datetime.now().isoformat(),
            impressions=impressions,
            likes=likes,
            comments=comments_count,
            shares=shares,
            clicks=clicks,
            engagement_rate=engagement_rate
        )
        
        self.posts[post_id] = post
        
        # Track by campaign
        if campaign_id not in self.campaigns:
            self.campaigns[campaign_id] = []
        self.campaigns[campaign_id].append(post_id)
        
        # Generate some mock comments
        self._generate_comments(post_id, comments_count)
        
        return post
    
    def _generate_comments(self, post_id: str, count: int):
        """Generate mock comments for a post"""
        self.comments[post_id] = []
        
        for _ in range(count):
            self._comment_counter += 1
            comment_id = f"COMMENT{self._comment_counter:06d}"
            
            # Random sentiment distribution: 60% positive, 30% neutral, 10% negative
            sentiment_choice = random.random()
            if sentiment_choice < 0.6:
                sentiment = "positive"
                content = random.choice(self.POSITIVE_COMMENTS)
            elif sentiment_choice < 0.9:
                sentiment = "neutral"
                content = random.choice(self.NEUTRAL_COMMENTS)
            else:
                sentiment = "negative"
                content = random.choice(self.NEGATIVE_COMMENTS)
            
            comment = MockSocialComment(
                id=comment_id,
                post_id=post_id,
                author_name=random.choice(self.COMMENT_AUTHORS),
                content=content,
                sentiment=sentiment,
                created_at=datetime.now().isoformat()
            )
            
            self.comments[post_id].append(comment)
    
    def get_post(self, post_id: str) -> Optional[MockSocialPost]:
        """Get post by ID"""
        return self.posts.get(post_id)
    
    def get_post_comments(self, post_id: str) -> List[MockSocialComment]:
        """Get comments for a post"""
        return self.comments.get(post_id, [])
    
    def get_campaign_posts(self, campaign_id: str) -> List[MockSocialPost]:
        """Get all posts for a campaign"""
        post_ids = self.campaigns.get(campaign_id, [])
        return [self.posts[pid] for pid in post_ids if pid in self.posts]
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign social media statistics"""
        posts = self.get_campaign_posts(campaign_id)
        
        if not posts:
            return {
                "total_posts": 0,
                "total_impressions": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "total_clicks": 0,
                "avg_engagement_rate": 0.0,
                "by_platform": {}
            }
        
        total_impressions = sum(p.impressions for p in posts)
        total_likes = sum(p.likes for p in posts)
        total_comments = sum(p.comments for p in posts)
        total_shares = sum(p.shares for p in posts)
        total_clicks = sum(p.clicks for p in posts)
        avg_engagement = round(sum(p.engagement_rate for p in posts) / len(posts), 2)
        
        # Stats by platform
        by_platform = {}
        for platform in ["facebook", "instagram", "twitter"]:
            platform_posts = [p for p in posts if p.platform == platform]
            if platform_posts:
                by_platform[platform] = {
                    "posts": len(platform_posts),
                    "impressions": sum(p.impressions for p in platform_posts),
                    "engagement_rate": round(
                        sum(p.engagement_rate for p in platform_posts) / len(platform_posts), 2
                    )
                }
        
        return {
            "total_posts": len(posts),
            "total_impressions": total_impressions,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_clicks": total_clicks,
            "avg_engagement_rate": avg_engagement,
            "by_platform": by_platform
        }
    
    def get_all_posts(self) -> List[MockSocialPost]:
        """Get all posts"""
        return list(self.posts.values())
    
    def get_recent_posts(self, limit: int = 50) -> List[MockSocialPost]:
        """Get most recent posts"""
        return sorted(
            self.posts.values(),
            key=lambda p: p.posted_at,
            reverse=True
        )[:limit]
    
    def get_sentiment_analysis(self, campaign_id: str) -> Dict[str, Any]:
        """Analyze sentiment of comments for a campaign"""
        posts = self.get_campaign_posts(campaign_id)
        all_comments = []
        
        for post in posts:
            all_comments.extend(self.get_post_comments(post.id))
        
        if not all_comments:
            return {
                "total_comments": 0,
                "positive": 0,
                "neutral": 0,
                "negative": 0,
                "positive_percent": 0.0,
                "negative_percent": 0.0
            }
        
        positive = len([c for c in all_comments if c.sentiment == "positive"])
        neutral = len([c for c in all_comments if c.sentiment == "neutral"])
        negative = len([c for c in all_comments if c.sentiment == "negative"])
        total = len(all_comments)
        
        return {
            "total_comments": total,
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
            "positive_percent": round(positive / total * 100, 2),
            "negative_percent": round(negative / total * 100, 2)
        }
