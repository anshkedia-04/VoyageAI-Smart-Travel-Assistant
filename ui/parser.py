from __future__ import annotations

from dataclasses import dataclass
import html
import re


@dataclass(frozen=True)
class ItineraryDay:
    """Represents a parsed single day inside a travel itinerary."""

    day_number: str
    title: str
    items: list[str]


@dataclass(frozen=True)
class InfoSection:
    """Represents a non-day travel section (Hotels, Budget, Weather, etc.)."""

    heading: str
    lines: list[str]


@dataclass(frozen=True)
class ParsedItinerary:
    """Structured travel itinerary parsed from Markdown LLM output."""

    intro_lines: list[str]
    days: list[ItineraryDay]
    sections: list[InfoSection]


_DAY_HEADER_RE = re.compile(
    r"^(?:#{1,6}\s*)?(?:\*{1,2}|_{1,2})?\s*Day\s+(\d+)(?:\s*[:\-–—]\s*(.*?))?(?:\*{1,2}|_{1,2})?\s*$",
    re.IGNORECASE,
)

_SECTION_HEADER_RE = re.compile(
    r"^(?:#{1,6}\s*)?(?:\*{1,2}|_{1,2})?\s*"
    r"((?:Off[-\s]?Beat|Alternative|Recommended\s+)?(?:Hotels?|Accommodation|Stays?|"
    r"Places?\s+of\s+Attractions?|Attractions?|Sightseeing|"
    r"Restaurants?|Dining|Food|"
    r"Activities|Experiences|"
    r"Modes?\s+of\s+Transportation|Transportation|Getting\s+Around|"
    r"Detailed\s+Cost\s+Breakdown|Cost\s+Breakdown|Estimated\s+Cost|Budget|"
    r"Per\s+Day\s+Expense(?:\s+Budget)?|Daily\s+Budget|"
    r"Weather(?:\s+Details|\s+Forecast)?|Best\s+Time|Packing\s+Tips|Travel\s+Tips))"
    r"(?:\*{1,2}|_{1,2})?\s*[:\-–—]?\s*(.*)$",
    re.IGNORECASE,
)


def strip_markdown_emphasis(text: str) -> str:
    """Clean stray markdown wrappers while preserving readable inline emphasis."""
    cleaned = text.strip()
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned)
    return cleaned.strip()


def format_inline_markdown_safe(text: str) -> str:
    """Escape HTML first, then convert safe **bold** and *italic* markers."""
    escaped = html.escape(text, quote=True)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", escaped)
    return escaped


def parse_travel_plan(answer: str) -> ParsedItinerary:
    """Parse flexible LLM Markdown itineraries into days and travel logistics sections."""
    intro_lines: list[str] = []
    days: list[ItineraryDay] = []
    sections: list[InfoSection] = []

    current_day_num: str | None = None
    current_day_title: str = ""
    current_day_items: list[str] = []

    current_section_heading: str | None = None
    current_section_lines: list[str] = []

    def _flush_day() -> None:
        nonlocal current_day_num, current_day_title, current_day_items
        if current_day_num is not None:
            days.append(
                ItineraryDay(
                    day_number=current_day_num,
                    title=current_day_title,
                    items=current_day_items,
                )
            )
            current_day_num = None
            current_day_title = ""
            current_day_items = []

    def _flush_section() -> None:
        nonlocal current_section_heading, current_section_lines
        if current_section_heading is not None:
            sections.append(
                InfoSection(
                    heading=current_section_heading,
                    lines=current_section_lines,
                )
            )
            current_section_heading = None
            current_section_lines = []

    for raw_line in answer.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped in {"---", "***", "___"}:
            continue

        day_match = _DAY_HEADER_RE.match(stripped)
        if day_match:
            _flush_section()
            _flush_day()
            day_num = day_match.group(1).zfill(2)
            subtitle = (day_match.group(2) or "").strip(" :*-–—")
            current_day_num = day_num
            current_day_title = subtitle if subtitle else f"Day {int(day_num)} Plan"
            current_day_items = []
            continue

        section_match = _SECTION_HEADER_RE.match(stripped)
        if section_match:
            _flush_day()
            _flush_section()
            heading = strip_markdown_emphasis(section_match.group(1)).rstrip(":")
            inline_tail = section_match.group(2).strip()
            current_section_heading = heading
            current_section_lines = [inline_tail] if inline_tail else []
            continue

        cleaned_item = re.sub(r"^[-•*]\s+", "", stripped)
        cleaned_item = re.sub(r"^\d+\.\s+", "", cleaned_item)

        if current_day_num is not None:
            if cleaned_item:
                current_day_items.append(cleaned_item)
        elif current_section_heading is not None:
            current_section_lines.append(stripped)
        else:
            intro_lines.append(stripped)

    _flush_day()
    _flush_section()

    return ParsedItinerary(
        intro_lines=intro_lines,
        days=days,
        sections=sections,
    )


def compose_travel_prompt(
    destination: str,
    days: int,
    travelers: int,
    budget_tier: str,
    currency: str,
    interests: list[str],
    include_offbeat: bool,
    custom_notes: str = "",
) -> str:
    """Build a structured, high-signal travel planning prompt from form controls."""
    interests_text = ", ".join(interests) if interests else "balanced sightseeing and local food"
    offbeat_clause = (
        "Include both classic highlights and off-beat hidden gems nearby. "
        if include_offbeat
        else "Focus on the top curated experiences. "
    )
    notes_clause = f"Additional preferences: {custom_notes.strip()}" if custom_notes.strip() else ""

    return (
        f"Plan a {days}-day trip to {destination.strip()} for {travelers} "
        f"{'traveler' if travelers == 1 else 'travelers'} with a {budget_tier} budget "
        f"(show estimated costs in {currency}). "
        f"Interests: {interests_text}. "
        f"{offbeat_clause}"
        "Format clearly with Day 1, Day 2, ... headings, plus dedicated sections for "
        "Hotels, Restaurants, Activities, Transportation, Cost Breakdown, Per Day Budget, and Weather. "
        f"{notes_clause}"
    ).strip()


def estimate_trip_budget(
    days: int,
    travelers: int,
    stay_per_night: float,
    food_per_person_day: float,
    activities_per_person_day: float,
    transport_total: float,
) -> dict[str, float]:
    """Calculate itemized trip budget breakdown for the Travel Toolkit tab."""
    stay_total = max(days - 1, 1) * stay_per_night
    food_total = days * travelers * food_per_person_day
    activities_total = days * travelers * activities_per_person_day
    grand_total = stay_total + food_total + activities_total + transport_total
    return {
        "Stay & Lodging": round(stay_total, 2),
        "Dining & Food": round(food_total, 2),
        "Activities & Entry": round(activities_total, 2),
        "Flights & Local Transit": round(transport_total, 2),
        "Total Estimated": round(grand_total, 2),
        "Per Person": round(grand_total / max(travelers, 1), 2),
    }
