"""
Content filter for Pure Bhakti API
Protects sacred content from inappropriate queries
"""
from typing import Tuple, Set
import re
import os


class ContentFilter:
    """Filter inappropriate content from search queries"""

    # Cache for loaded blocked words
    _blocked_words_cache: Set[str] = None

    @classmethod
    def _load_blocked_words(cls) -> Set[str]:
        """Load blocked words from configuration file"""
        if cls._blocked_words_cache is not None:
            return cls._blocked_words_cache

        blocked_words = set()
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'data',
            'blocked_words.txt'
        )

        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip().lower()
                        # Skip comments and empty lines
                        if line and not line.startswith('#'):
                            blocked_words.add(line)
        except Exception as e:
            # Fallback to hardcoded list if file cannot be read
            print(f"Warning: Could not load blocked words file: {e}")
            blocked_words = {
                "sex", "porn", "xxx", "drug", "kill", "hate",
                "fuck", "shit", "damn"
            }

        cls._blocked_words_cache = blocked_words
        return blocked_words

    @classmethod
    def get_blocked_words(cls) -> Set[str]:
        """Get the set of blocked words"""
        return cls._load_blocked_words()

    # Additional pattern matching for variations
    BLOCKED_PATTERNS = [
        r'\b(f+u+c+k+)\b',  # Variations with repeated letters
        r'\b(s+h+i+t+)\b',
        r'\b(d+a+m+n+)\b',
        # Add more patterns as needed
    ]

    @classmethod
    def is_appropriate(cls, text: str) -> Tuple[bool, str]:
        """
        Check if the query text is appropriate for sacred content.

        Args:
            text: The search query text

        Returns:
            Tuple of (is_appropriate: bool, reason: str)
            - If appropriate: (True, "")
            - If inappropriate: (False, "reason message")
        """
        if not text or not text.strip():
            return False, "Empty query"

        text_lower = text.lower().strip()

        # Check against blocked words
        blocked_words = cls.get_blocked_words()
        words = re.findall(r'\b\w+\b', text_lower)
        for word in words:
            if word in blocked_words:
                return False, "Query contains inappropriate content"

        # Check against blocked patterns
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return False, "Query contains inappropriate content"

        # Check for excessive special characters (spam/abuse)
        special_char_ratio = sum(not c.isalnum() and not c.isspace() for c in text) / len(text)
        if special_char_ratio > 0.3:  # More than 30% special characters
            return False, "Query contains excessive special characters"

        # Check for repeated characters (spam)
        if re.search(r'(.)\1{5,}', text):  # 6+ repeated characters
            return False, "Query appears to be spam"

        # Query length limits
        if len(text) > 200:
            return False, "Query is too long (max 200 characters)"

        if len(text) < 2:
            return False, "Query is too short (min 2 characters)"

        return True, ""

    @classmethod
    def sanitize_query(cls, text: str) -> str:
        """
        Clean and sanitize the query text.

        Args:
            text: Raw query text

        Returns:
            Sanitized query text
        """
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())

        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())

        # Limit length
        if len(text) > 200:
            text = text[:200]

        return text
