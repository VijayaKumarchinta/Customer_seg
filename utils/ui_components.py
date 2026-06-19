"""
UI Component Helpers
Consistent page headers, section titles, and other reusable UI patterns.
Reduces duplication across page files by centralizing common HTML strings.
"""

import re


def _strip_emoji(text: str) -> str:
    """Remove emoji characters from a string, leaving text and spaces."""
    # Covers most emoji ranges including pictographs, emoticons, symbols, modifiers
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F9FF"  # Misc Symbols, Pictographs, Emoticons, Supplemental
        "\U0001F600-\U0001F64F"  # Emoticons
        "\U0001F680-\U0001F6FF"  # Transport & Map
        "\U0001F1E0-\U0001F1FF"  # Flags
        "\U00002600-\U000027BF"  # Misc symbols
        "\U0000FE00-\U0000FE0F"  # Variation selectors
        "\U0000200D"             # Zero-width joiner
        "]+"
    )
    return emoji_pattern.sub("", text).strip()


def hero_header(title: str, subtitle: str) -> str:
    """
    Returns a dark gradient hero banner HTML string for page titles.

    Parameters
    ----------
    title : str
        The page title (e.g. "📊 Segment Overview")
    subtitle : str
        The page subtitle/description

    Returns
    -------
    str
        HTML string ready for st.markdown(..., unsafe_allow_html=True)
    """
    clean_title = _strip_emoji(title)
    return f"""
    <div class="hero-banner" role="region" aria-label="Page: {clean_title}"
         style="margin-bottom: 1.5rem; padding: 1.5rem;
                background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
                border-radius: 12px;">
        <h1 class="hero-title" style="margin: 0; font-size: 1.8rem; color: #FFFFFF;">{title}</h1>
        <p class="hero-subtitle" style="color: #94A3B8; margin: 0.3rem 0 0 0; font-size: 0.95rem;">
            {subtitle}
        </p>
    </div>
    """


def section_header(title: str) -> str:
    """
    Returns a section header HTML string with a red bottom border.

    Parameters
    ----------
    title : str
        Section title (e.g. "🎯 Key Metrics")

    Returns
    -------
    str
        HTML string ready for st.markdown(..., unsafe_allow_html=True)
    """
    return (
        '<h3 class="section-title" '
        'style="font-size: 1.15rem; font-weight: 700; '
        'color: #0F1419; padding-bottom: 0.6rem; '
        'border-bottom: 2px solid rgba(255,75,75,0.15); '
        f'margin-bottom: 1rem; letter-spacing: -0.01em;">{title}</h3>'
    )
