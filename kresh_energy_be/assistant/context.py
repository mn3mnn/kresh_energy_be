"""Build a compact, locale-aware knowledge snapshot for the assistant.

The catalog is small, so instead of a vector store we inject the whole active
catalogue (services, FAQs, coverage cities, featured projects, calculator
assumptions) as plain text. The model is instructed to answer only from this.
"""

from __future__ import annotations

from kresh_energy_be.catalog.models import FAQ
from kresh_energy_be.catalog.models import CalculatorConfig
from kresh_energy_be.catalog.models import Project
from kresh_energy_be.catalog.models import Service
from kresh_energy_be.catalog.models import ServiceArea
from kresh_energy_be.common.serializers import DEFAULT_LANGUAGE

# Keep the snapshot bounded so prompts stay cheap.
MAX_FAQS = 20
MAX_SERVICES = 12
MAX_PROJECTS = 6


def _t(instance, field: str, lang: str) -> str:
    """Return ``<field>_<lang>`` with a fallback to the default language."""
    return getattr(instance, f"{field}_{lang}", "") or getattr(
        instance,
        f"{field}_{DEFAULT_LANGUAGE}",
        "",
    )


def build_knowledge_snapshot(lang: str) -> str:
    """Assemble the grounding context in the given 2-letter language."""
    blocks: list[str] = []

    services = Service.objects.filter(is_active=True).order_by("order", "id")[
        :MAX_SERVICES
    ]
    if services:
        lines = [
            f"- {_t(s, 'title', lang)}: {_t(s, 'summary', lang)}".strip()
            for s in services
        ]
        blocks.append("SERVICES:\n" + "\n".join(lines))

    faqs = FAQ.objects.filter(is_active=True).order_by("category", "order", "id")[
        :MAX_FAQS
    ]
    if faqs:
        lines = [
            f"Q: {_t(f, 'question', lang)}\nA: {_t(f, 'answer', lang)}" for f in faqs
        ]
        blocks.append("FAQ:\n" + "\n\n".join(lines))

    areas = ServiceArea.objects.filter(is_active=True).order_by("order", "name")
    if areas:
        names = ", ".join(a.name for a in areas)
        blocks.append("COVERAGE AREAS (cities served):\n" + names)

    projects = Project.objects.filter(is_active=True, is_featured=True).order_by(
        "order",
        "-date_completed",
    )[:MAX_PROJECTS]
    if projects:
        lines = [
            f"- {_t(p, 'title', lang)} ({p.city}): {p.size_kwp} kWp, "
            f"{p.panel_count} panels"
            for p in projects
        ]
        blocks.append("FEATURED PROJECTS:\n" + "\n".join(lines))

    cfg = CalculatorConfig.get_instance()
    blocks.append(
        "SOLAR SIZING ASSUMPTIONS (German market, for rough sizing ballparks "
        "only, no pricing — always direct users to the on-site calculator at "
        "/calculator for sizing and to /quote for pricing):\n"
        f"- Specific yield: {cfg.specific_yield} kWh per kWp per year\n"
        f"- Module size: {cfg.panel_kwp} kWp (~{cfg.panel_area_m2} m² each)\n"
        f"- Household base load: {cfg.base_consumption} kWh/yr "
        f"+ {cfg.per_member_consumption} kWh/yr per person\n"
        f"- EV adds ~{cfg.ev_consumption} kWh/yr\n"
        f"- Self-consumption: {cfg.self_consumption_no_battery} without battery, "
        f"{cfg.self_consumption_with_battery} with battery",
    )

    return "\n\n".join(blocks)
