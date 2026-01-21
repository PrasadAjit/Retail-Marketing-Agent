"""
Mock Email Service
Simulates email sending with tracking
"""
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class MockEmail:
    """Represents a sent email"""
    id: str
    campaign_id: str
    to_email: str
    to_name: str
    subject: str
    content: str
    sent_at: str
    opened: bool
    opened_at: Optional[str]
    clicked: bool
    clicked_at: Optional[str]
    converted: bool
    converted_at: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class MockEmailService:
    """Simulates email sending and tracking"""
    
    def __init__(self):
        self.emails: Dict[str, MockEmail] = {}
        self.campaigns: Dict[str, List[str]] = {}  # campaign_id -> email_ids
        self._email_counter = 0
    
    def send_email(
        self,
        to_email: str,
        to_name: str,
        subject: str,
        content: str,
        campaign_id: str
    ) -> MockEmail:
        """
        Send a mock email
        
        Args:
            to_email: Recipient email
            to_name: Recipient name
            subject: Email subject
            content: Email content/body
            campaign_id: Associated campaign ID
        
        Returns:
            MockEmail object
        """
        self._email_counter += 1
        email_id = f"EMAIL{self._email_counter:06d}"
        
        # Simulate realistic engagement rates
        opened = random.random() < 0.35  # 35% open rate
        clicked = opened and random.random() < 0.15  # 15% click-through of opens (5.25% overall)
        converted = clicked and random.random() < 0.20  # 20% conversion of clicks
        
        email = MockEmail(
            id=email_id,
            campaign_id=campaign_id,
            to_email=to_email,
            to_name=to_name,
            subject=subject,
            content=content,
            sent_at=datetime.now().isoformat(),
            opened=opened,
            opened_at=datetime.now().isoformat() if opened else None,
            clicked=clicked,
            clicked_at=datetime.now().isoformat() if clicked else None,
            converted=converted,
            converted_at=datetime.now().isoformat() if converted else None
        )
        
        self.emails[email_id] = email
        
        # Track by campaign
        if campaign_id not in self.campaigns:
            self.campaigns[campaign_id] = []
        self.campaigns[campaign_id].append(email_id)
        
        return email
    
    def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],  # [{"email": ..., "name": ...}, ...]
        subject: str,
        content: str,
        campaign_id: str
    ) -> List[MockEmail]:
        """
        Send bulk emails
        
        Args:
            recipients: List of recipient dicts with 'email' and 'name'
            subject: Email subject
            content: Email content
            campaign_id: Associated campaign ID
        
        Returns:
            List of MockEmail objects
        """
        emails = []
        for recipient in recipients:
            email = self.send_email(
                to_email=recipient["email"],
                to_name=recipient["name"],
                subject=subject,
                content=content,
                campaign_id=campaign_id
            )
            emails.append(email)
        
        return emails
    
    def get_email(self, email_id: str) -> Optional[MockEmail]:
        """Get email by ID"""
        return self.emails.get(email_id)
    
    def get_campaign_emails(self, campaign_id: str) -> List[MockEmail]:
        """Get all emails for a campaign"""
        email_ids = self.campaigns.get(campaign_id, [])
        return [self.emails[eid] for eid in email_ids if eid in self.emails]
    
    def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign email statistics"""
        emails = self.get_campaign_emails(campaign_id)
        
        if not emails:
            return {
                "total_sent": 0,
                "opened": 0,
                "clicked": 0,
                "converted": 0,
                "open_rate": 0.0,
                "click_rate": 0.0,
                "conversion_rate": 0.0
            }
        
        total = len(emails)
        opened = sum(1 for e in emails if e.opened)
        clicked = sum(1 for e in emails if e.clicked)
        converted = sum(1 for e in emails if e.converted)
        
        return {
            "total_sent": total,
            "opened": opened,
            "clicked": clicked,
            "converted": converted,
            "open_rate": round(opened / total * 100, 2) if total > 0 else 0,
            "click_rate": round(clicked / total * 100, 2) if total > 0 else 0,
            "conversion_rate": round(converted / total * 100, 2) if total > 0 else 0
        }
    
    def get_all_emails(self) -> List[MockEmail]:
        """Get all sent emails"""
        return list(self.emails.values())
    
    def get_recent_emails(self, limit: int = 50) -> List[MockEmail]:
        """Get most recent emails"""
        return sorted(
            self.emails.values(),
            key=lambda e: e.sent_at,
            reverse=True
        )[:limit]
