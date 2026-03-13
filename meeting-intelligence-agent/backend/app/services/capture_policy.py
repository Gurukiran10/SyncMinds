"""
Capture Policy Service
Evaluates whether a meeting should be recorded based on user-defined rules.
"""
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

DEFAULT_POLICY: Dict[str, Any] = {
    "smart_recording_enabled": False,
    "min_team_size": 2,
    "include_keywords": [],
    "exclude_keywords": [],
    "required_tags": [],
    "exclude_platforms": [],
    "record_all": True,
}


def evaluate_meeting(meeting_data: Dict[str, Any], policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Evaluate whether a meeting should be captured/recorded.

    Args:
        meeting_data: Dict with keys: title, description, attendee_count, tags, platform
        policy: User's capture policy dict (defaults to record all)

    Returns:
        {"should_record": bool, "reason": str}
    """
    if not policy:
        policy = DEFAULT_POLICY

    if not policy.get("smart_recording_enabled", False):
        return {"should_record": True, "reason": "Smart recording disabled — recording all meetings"}

    title = str(meeting_data.get("title", "")).lower()
    description = str(meeting_data.get("description", "")).lower()
    attendee_count = int(meeting_data.get("attendee_count", 0))
    tags: List[str] = [str(t).lower() for t in (meeting_data.get("tags") or [])]
    platform = str(meeting_data.get("platform", "")).lower()

    # Check excluded platforms
    excluded_platforms: List[str] = [p.lower() for p in (policy.get("exclude_platforms") or [])]
    if platform in excluded_platforms:
        return {"should_record": False, "reason": f"Platform '{platform}' is excluded from recording"}

    # Check minimum team size
    min_size = int(policy.get("min_team_size", 2))
    if attendee_count < min_size:
        return {
            "should_record": False,
            "reason": f"Meeting has {attendee_count} attendees, below minimum {min_size}",
        }

    # Check excluded keywords in title/description
    exclude_keywords: List[str] = [k.lower() for k in (policy.get("exclude_keywords") or [])]
    for keyword in exclude_keywords:
        if keyword in title or keyword in description:
            return {
                "should_record": False,
                "reason": f"Excluded keyword '{keyword}' found in meeting title/description",
            }

    # Check required tags (if any required tags set, at least one must match)
    required_tags: List[str] = [t.lower() for t in (policy.get("required_tags") or [])]
    if required_tags and not any(rt in tags for rt in required_tags):
        return {
            "should_record": False,
            "reason": f"Meeting missing required tags: {required_tags}",
        }

    # Check include keywords (if set, at least one must be present)
    include_keywords: List[str] = [k.lower() for k in (policy.get("include_keywords") or [])]
    if include_keywords:
        matched = any(k in title or k in description for k in include_keywords)
        if not matched:
            return {
                "should_record": False,
                "reason": "Meeting does not match any include keywords",
            }

    return {"should_record": True, "reason": "Meeting matches capture policy rules"}


def get_default_policy() -> Dict[str, Any]:
    return dict(DEFAULT_POLICY)


def merge_policy(user_policy: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge user policy with defaults (user values override defaults)."""
    merged = dict(DEFAULT_POLICY)
    if user_policy:
        merged.update({k: v for k, v in user_policy.items() if v is not None})
    return merged
