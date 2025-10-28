from django.templatetags.static import static
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache


# ✅ Helper function to safely count unread messages
def get_unread_message_count():
    try:
        from apps.serviceapp.models import Contact
        return Contact.objects.filter(is_read=False).count()
    except Exception:
        return 0




UNFOLD = {
    "SITE_TITLE": "Fawz Cleaning & Gardening",
    "SITE_HEADER": "Fawz Cleaning",
    "SITE_SUBHEADER": "Appears under SITE_HEADER",
    "SITE_URL": "/",
    "SITE_SYMBOL": "vacuum",  # icon in header
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_BACK_BUTTON": True,
    "DASHBOARD_CALLBACK": "apps.serviceapp.views.dashboard_callback",
    "DASHBOARD_CARDS": ["unread_messages", "quote_requests", "completed_jobs"],

    "BORDER_RADIUS": "6px",

    # ✅ Custom colors (same as before)
    "COLORS": {
        "base": {
            "50": "oklch(98.5% .002 247.839)",
            "100": "oklch(96.7% .003 264.542)",
            "200": "oklch(92.8% .006 264.531)",
            "300": "oklch(87.2% .01 258.338)",
            "400": "oklch(70.7% .022 261.325)",
            "500": "oklch(55.1% .027 264.364)",
            "600": "oklch(44.6% .03 256.802)",
            "700": "oklch(37.3% .034 259.733)",
            "800": "oklch(27.8% .033 256.848)",
            "900": "oklch(21% .034 264.665)",
            "950": "oklch(13% .028 261.692)",
        },
        "primary": {
            "50": "oklch(97.7% .014 308.299)",
            "100": "oklch(94.6% .033 307.174)",
            "200": "oklch(90.2% .063 306.703)",
            "300": "oklch(82.7% .119 306.383)",
            "400": "oklch(71.4% .203 305.504)",
            "500": "oklch(62.7% .265 303.9)",
            "600": "oklch(55.8% .288 302.321)",
            "700": "oklch(49.6% .265 301.924)",
            "800": "oklch(43.8% .218 303.724)",
            "900": "oklch(38.1% .176 304.987)",
            "950": "oklch(29.1% .149 302.717)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },

    # ✅ Sidebar navigation organized
    "SIDEBAR": {
        "show_search": False,
        "command_search": False,
        "show_all_applications": False,
        "navigation": [
            # -------------------------------
            # 🧾 GENERAL MANAGEMENT
            # -------------------------------
            {
                "title": _("General Management"),
                "collapsible": False,
                "items": [
                    {"title": _("Home"), "icon": "dashboard", "link": reverse_lazy("admin:index")},
                    {"title": _("Quote Request"), "icon": "unknown_document", "link": reverse_lazy("admin:serviceapp_quoterequest_changelist")},
                    {"title": _("Quote"), "icon": "request_quote", "link": reverse_lazy("admin:serviceapp_quote_changelist")},
                    {"title": _("Invoice"), "icon": "picture_as_pdf", "link": reverse_lazy("admin:serviceapp_invoice_changelist")},
                    {"title": _("Users"), "icon": "people", "link": reverse_lazy("admin:auth_user_changelist")},
                ],
            },

            # -------------------------------
            # 🌐 WEBSITE CONTENT
            # -------------------------------
            {
                "title": _("Website Content"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": _("Hero Section"), "icon": "photo_library", "link": reverse_lazy("admin:serviceapp_herosection_changelist")},
                    {"title": _("Services"), "icon": "home_repair_service", "link": reverse_lazy("admin:serviceapp_service_changelist")},
                    {"title": _("Service Locations"), "icon": "location_on", "link": reverse_lazy("admin:serviceapp_servicelocation_changelist")},
                    {"title": _("Pricing"), "icon": "attach_money", "link": reverse_lazy("admin:serviceapp_pricing_changelist")},
                    {"title": _("FAQs"), "icon": "question_exchange", "link": reverse_lazy("admin:serviceapp_faq_changelist")},

                    # ✅ Dynamic unread contact count (auto updates every 60s)
            {
                    "title": _(f"📨 Contact ({get_unread_message_count()} Unread)"),  # ✅ actual icon visible
                    "icon": None,  # disable Unfold’s default icon handling for this item
                    "link": reverse_lazy("admin:serviceapp_contact_changelist"),
            },


                    {"title": _("Reviews"), "icon": "reviews", "link": reverse_lazy("admin:serviceapp_review_changelist")},
                    # {"title": _("Images"), "icon": "photo_library", "link": reverse_lazy("admin:serviceapp_imagegallery_changelist")},
                    # {"title": _("Team"), "icon": "groups", "link": reverse_lazy("admin:serviceapp_team_changelist")},
                    {"title": _("Company Details"), "icon": "article_person", "link": reverse_lazy("admin:serviceapp_mycompany_changelist")},
                    {"title": _("Page Content"), "icon": "lock", "link": reverse_lazy("admin:serviceapp_pagecontent_changelist")},
                    # {"title": _("Terms & Conditions"), "icon": "gavel", "link": "/admin/serviceapp/pagecontent/?page__exact=terms"},
                ],
            },

            # -------------------------------
            # 👷 CAREER MANAGEMENT
            # -------------------------------
            {
                "title": _("Career Management"),
                "separator": True,
                "collapsible": False,
                "items": [
                    {"title": _("Job Vacancies"), "icon": "cases", "link": reverse_lazy("admin:serviceapp_vacancy_changelist")},
                    {"title": _("Applications"), "icon": "work_history", "link": reverse_lazy("admin:serviceapp_application_changelist")},
                    {"title": _("Email Templates"), "icon": "mark_email_unread", "link": reverse_lazy("admin:serviceapp_emailmessagetemplate_changelist")},
                ],
            },
        ],
    },
}


# ---------------------------------------------------
# 🔴 OPTIONAL STYLE & SCRIPT CONFIGURATION
# ---------------------------------------------------
UNFOLD["STYLES"] = [
    lambda request: static("admin/css/admin.css"),
]

UNFOLD["SCRIPTS"] = [
    lambda request: static("admin/js/admin-refresh.js"),
]


