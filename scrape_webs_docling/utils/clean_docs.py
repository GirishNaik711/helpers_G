import re

COMMON_NOISE_PHRASES = {
    "home", "menu", "navigation", "nav", "logo", "search",
    "skip to main content", "sign in", "sign up", "contact us",
    "privacy policy", "terms of service", "legal", "cookies",
    "cookie preferences", "language", "about us", "follow us",
    "newsletter", "support", "back to top", "subscribe",
}

def is_noise_text(text: str) -> bool:
    """Returns True if text appears to be layout/navigation/footer noise."""
    t = text.lower().strip()

    if len(t) <= 2:
        return True  # very short fragments like "›", "|", "*"

    # Common boilerplate sections found across most websites
    for phrase in COMMON_NOISE_PHRASES:
        if phrase in t:
            return True

    # Looks like a social media label
    if t in {"facebook", "instagram", "twitter", "x", "linkedin", "youtube"}:
        return True

    # Looks like cookie text
    if "cookie" in t and ("policy" in t or "settings" in t):
        return True

    # Looks like legal/copyright
    if "©" in t or "copyright" in t:
        return True

    return False


def clean_text_value(text: str) -> str:
    """Removes Docling metadata & strange artifacts."""
    cleaned = text

    # Remove Docling repr-like patterns
    cleaned = re.sub(r"RefItem\(.*?\)", "", cleaned)
    cleaned = re.sub(r"content_layer=<.*?>", "", cleaned)
    cleaned = re.sub(r"<ContentLayer\.[^>]+>", "", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def extract_clean_text_generic(doc):
    """
    Extract human-readable text from ANY DoclingDocument.
    Removes menu/footer/UI fluff + Docling metadata.
    """
    clean_lines = []

    # Grab readable text elements
    for item in getattr(doc, "texts", []):
        text = getattr(item, "text", None)
        if not text:
            continue

        cleaned = clean_text_value(text)

        if not cleaned or is_noise_text(cleaned):
            continue

        clean_lines.append(cleaned)

    # Also scan group children (headers, list items)
    for group in getattr(doc, "groups", []):
        for child in getattr(group, "children", []):
            obj = getattr(child, "obj", None)
            if not obj:
                continue
            text = getattr(obj, "text", None)

            if not text:
                continue

            cleaned = clean_text_value(text)

            if cleaned and not is_noise_text(cleaned):
                clean_lines.append(cleaned)

    # Remove duplicates in order
    seen = set()
    deduped = []
    for line in clean_lines:
        if line not in seen:
            seen.add(line)
            deduped.append(line)

    return deduped
