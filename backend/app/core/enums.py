"""Core enums for threat taxonomy, decisions, and system components."""

from enum import Enum


class AttackCategory(str, Enum):
    """10 Threat model categories for prompt injection & jailbreak detection."""
    BENIGN = "BENIGN"
    DIRECT_PROMPT_INJECTION = "DIRECT_PROMPT_INJECTION"
    JAILBREAK = "JAILBREAK"
    SYSTEM_PROMPT_LEAK = "SYSTEM_PROMPT_LEAK"
    INDIRECT_PROMPT_INJECTION = "INDIRECT_PROMPT_INJECTION"
    OBFUSCATED_ATTACK = "OBFUSCATED_ATTACK"
    ROLE_MANIPULATION = "ROLE_MANIPULATION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    TOOL_MANIPULATION = "TOOL_MANIPULATION"
    MULTI_TURN_MANIPULATION = "MULTI_TURN_MANIPULATION"


class FirewallDecision(str, Enum):
    """Firewall verdict states."""
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    REVIEW = "REVIEW"


class DetectionLayer(str, Enum):
    """Security layers responsible for detection."""
    RULE_ENGINE = "RULE_ENGINE"
    ML_CLASSIFIER = "ML_CLASSIFIER"
    BOTH = "BOTH"
    NONE = "NONE"


class RuleSeverity(str, Enum):
    """Severity ratings for rule violations."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @property
    def default_score(self) -> float:
        mapping = {
            "LOW": 0.25,
            "MEDIUM": 0.50,
            "HIGH": 0.80,
            "CRITICAL": 1.00,
        }
        return mapping.get(self.value, 0.50)


class PatternType(str, Enum):
    """Supported rule matching mechanisms."""
    KEYWORD = "keyword"
    PHRASE = "phrase"
    REGEX = "regex"
    STRUCTURAL = "structural"
    OBFUSCATION = "obfuscation"
    TEMPLATE = "template"
    ENCODED = "encoded"
    UNICODE = "unicode"


class UserRole(str, Enum):
    """User access control roles."""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class LLMProviderType(str, Enum):
    """Supported LLM backend providers."""
    MOCK = "mock"
    OLLAMA = "ollama"
    OPENAI = "openai"
    REST = "rest"
