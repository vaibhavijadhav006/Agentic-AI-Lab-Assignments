from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional


@dataclass
class Email:
    id: str
    sender: str
    subject: str
    body: str
    received_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EmailAnalysis:
    email_id: str
    category: str
    priority: str
    urgency_score: int
    action_items: List[str] = field(default_factory=list)
    follow_up_date: Optional[str] = None
    reply_required: bool = False
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Draft:
    email_id: str
    to: str
    subject: str
    body: str
    status: str = "PENDING_APPROVAL"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
