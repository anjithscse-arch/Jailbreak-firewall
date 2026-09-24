"""Core constants, security thresholds, and character mappings."""

from app.core.enums import AttackCategory

# Risk scoring formula constants
CATEGORY_CONSISTENCY_BONUS = 0.05
OBFUSCATION_BONUS = 0.05
HIGH_SEVERITY_AUTO_BLOCK = 0.80

DEFAULT_BLOCKED_MESSAGE = "This prompt was blocked by the AI security firewall."
DEFAULT_REVIEW_MESSAGE = "This prompt requires administrative review before processing."

# Zero-width & invisible Unicode codepoints commonly used in evasion
ZERO_WIDTH_CHARS = {
    "\u200B",  # Zero-width space
    "\u200C",  # Zero-width non-joiner
    "\u200D",  # Zero-width joiner
    "\uFEFF",  # Byte order mark / zero-width no-break space
    "\u2060",  # Word joiner
    "\u180E",  # Mongolian vowel separator
    "\u200E",  # Left-to-right mark
    "\u200F",  # Right-to-left mark
    "\u202A",  # Left-to-right embedding
    "\u202B",  # Right-to-left embedding
    "\u202C",  # Pop directional formatting
    "\u202D",  # Left-to-right override
    "\u202E",  # Right-to-left override
    "\u00AD",  # Soft hyphen
}

# Standard Leetspeak mapping for heuristic normalization
LEET_MAPPINGS = {
    "@": "a",
    "4": "a",
    "8": "b",
    "3": "e",
    "1": "i",
    "!": "i",
    "0": "o",
    "5": "s",
    "$": "s",
    "7": "t",
    "+": "t",
    "2": "z",
}

# Threat Category Metadata
CATEGORY_DESCRIPTIONS = {
    AttackCategory.BENIGN: "Legitimate user prompt requesting standard conversational or computational assistance.",
    AttackCategory.DIRECT_PROMPT_INJECTION: "Explicit instruction override attempting to force the model to disregard prior instructions or safety rules.",
    AttackCategory.JAILBREAK: "Roleplay, persona emulation, or fictional framing designed to bypass content policy and ethical safeguards.",
    AttackCategory.SYSTEM_PROMPT_LEAK: "Attempts to extract, print, or exfiltrate hidden system directives, developer instructions, or internal configuration.",
    AttackCategory.INDIRECT_PROMPT_INJECTION: "Adversarial instructions embedded within external untrusted content (documents, emails, comments, search results).",
    AttackCategory.OBFUSCATED_ATTACK: "Attempts to disguise adversarial instructions via encoding, character insertion, homoglyphs, or leetspeak.",
    AttackCategory.ROLE_MANIPULATION: "Hostile redefinition of model authority, priority, or identity to assume administrative privileges.",
    AttackCategory.DATA_EXFILTRATION: "Attempts to extract environment variables, API secrets, proprietary context, or sensitive internal data.",
    AttackCategory.TOOL_MANIPULATION: "Attempts to coerce tool-augmented LLMs to execute unauthorized terminal commands, delete files, or trigger APIs.",
    AttackCategory.MULTI_TURN_MANIPULATION: "Progressive, multi-step priming aimed at gradually eroding safety boundaries over multiple conversational turns.",
}

CATEGORY_REMEDIATIONS = {
    AttackCategory.BENIGN: "No remediation required. The prompt complies with security policy.",
    AttackCategory.DIRECT_PROMPT_INJECTION: "Remove instruction-override directives (e.g., 'ignore previous instructions') and submit a standard task request.",
    AttackCategory.JAILBREAK: "Rephrase the prompt without persona evasion, unrestricted roleplay, or fictional policy circumvention.",
    AttackCategory.SYSTEM_PROMPT_LEAK: "System instructions and developer configuration are confidential and cannot be revealed. Please focus on application-level queries.",
    AttackCategory.INDIRECT_PROMPT_INJECTION: "Sanitize external references and ensure quoted documents do not contain directive commands targeting the assistant.",
    AttackCategory.OBFUSCATED_ATTACK: "Submit queries using standard, plaintext UTF-8 characters without artificial separators, zero-width characters, or encoded segments.",
    AttackCategory.ROLE_MANIPULATION: "Interact with the assistant under standard user permissions without asserting developer or administrative overrides.",
    AttackCategory.DATA_EXFILTRATION: "Avoid querying internal environment secrets, system files, or sensitive configuration data.",
    AttackCategory.TOOL_MANIPULATION: "Tool execution is restricted to authorized operations. Rephrase the query without unauthorized command execution requests.",
    AttackCategory.MULTI_TURN_MANIPULATION: "Ensure conversation state adheres to established safety policies across all interaction turns.",
}
