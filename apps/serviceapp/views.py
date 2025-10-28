from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.safestring import mark_safe
import json
from datetime import datetime
from django.http import JsonResponse


from .models import (
    Quote, QuoteRequest, Service, Vacancy, Contact, MyCompany,
    FAQ, ServiceLocation, Pricing, Review, PageContent, HeroSection
)
from .forms import QuoteRequestForm, ApplicationForm, ContactForm


# ================================================
# 🧩 Common Context Helper
# ================================================
def base_context():
    """Return common footer context for all pages."""
    return {
        "company": MyCompany.objects.first(),
        "services": Service.objects.filter(is_active=True),
    }


# ================================================
# 📊 Dashboard (Admin Analytics)
# ================================================
def dashboard_callback(request, context):
    print("=== DASHBOARD CALLBACK DEBUG ===")

    try:
        from .models import QuoteRequest, Contact  # ✅ Safe import
        total_requests = QuoteRequest.objects.count()
        total_replied = QuoteRequest.objects.filter(status="replied").count()
        total_completed = QuoteRequest.objects.filter(status="completed").count()
        unread_messages = Contact.objects.filter(is_read=False).count()  # ✅ Unread message count

        quote_requests = QuoteRequest.objects.all()

        status_colors = {
            "pending": "#3b82f6",
            "replied": "#facc15",
            "completed": "#16a34a",
        }

        events = []
        for qr in quote_requests:
            events.append({
                "id": str(qr.id),
                "title": f"{qr.name} - {qr.city or 'No City'}",
                "start": qr.created_at.strftime('%Y-%m-%d'),
                "backgroundColor": status_colors.get(qr.status, "#3b82f6"),
                "extendedProps": {
                    "email": qr.email,
                    "phone": qr.phone,
                    "service": ", ".join([s.name for s in qr.service.all()]),
                    "city": qr.city or "N/A",
                    "postal_code": qr.postal_code or "N/A",
                    "address": qr.address or "N/A",
                    "message": qr.message or "N/A",
                    "status": qr.status,
                },
            })

        events_json = mark_safe(json.dumps(events))

    except Exception as e:
        print(f"Error in dashboard callback: {e}")
        import traceback
        traceback.print_exc()
        total_requests = total_replied = total_completed = unread_messages = 0
        quote_requests = []
        events_json = mark_safe("[]")

    # ✅ Add all to context for Unfold Dashboard
    context.update({
        "total_requests": total_requests,
        "total_replied": total_replied,
        "total_completed": total_completed,
        "quote_requests": quote_requests,
        "events": events_json,
        "site_title": "Service Dashboard",
        "unread_messages": unread_messages,

        # ✅ Dashboard cards (with fixed working icon)
        "cards": [
            {
                "title": "Total Quote Requests",
                "icon": "request_quote",
                "color": "blue",
                "value": total_requests,
                "link": reverse_lazy("admin:serviceapp_quoterequest_changelist"),
            },
            {
                "title": "Pending Reply",
                "icon": "hourglass_empty",
                "color": "amber",
                "value": total_replied,
                "link": reverse_lazy("admin:serviceapp_quoterequest_changelist"),
            },
            {
                "title": "Total Completed",
                "icon": "check_circle",
                "color": "green",
                "value": total_completed,
                "link": reverse_lazy("admin:serviceapp_quote_changelist"),
            },
            {
                "title": "Unread Messages",
                "icon": "mail",  # ✅ fixed icon, works in all Unfold versions
                "color": "red",
                "value": unread_messages,
                "link": reverse_lazy("admin:serviceapp_contact_changelist"),
                "attr": {"data-card": "unread"},
            },
        ],
    })

    print("=== END DEBUG ===")
    return context





# ================================================
# 🧾 Quote Request
# ================================================
def quete_request(request):
    if request.method == "POST":
        form = QuoteRequestForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your quote request has been submitted successfully!')
            return redirect('home')
    else:
        form = QuoteRequestForm()
    context = base_context()
    context["form"] = form
    return render(request, 'quote_request.html', context)


# ================================================
# 🏠 Home Page
# ================================================
def home(request):
    hero = HeroSection.objects.filter(is_active=True).first()
    company = MyCompany.objects.first()
    services = Service.objects.filter(is_active=True)
    reviews = Review.objects.filter(is_active=True)
    pricing = Pricing.objects.filter(is_active=True)
    locations = ServiceLocation.objects.filter(is_active=True)
    popular_services = Service.objects.filter(is_popular=True)
    faqs = FAQ.objects.filter(is_general=True)

    return render(request, "index.html", {
        "hero": hero,
        "company": company,
        "services": services,
        "reviews": reviews,
        "pricing": pricing,
        "locations": locations,
        "popular_services": popular_services,
        "faqs": faqs,
    })


# ================================================
# 📄 Static Pages
# ================================================
def about(request):
    company = MyCompany.objects.first()
    page = PageContent.objects.filter(page='about').first()
    services = Service.objects.filter(is_active=True)
    return render(request, 'about.html', {
        'company': company,
        'page': page,
        'services': services,
    })


def services(request):
    context = base_context()
    return render(request, "services.html", context)


def contact(request):
    form = ContactForm(request.POST or None)
    contact_page = PageContent.objects.filter(page='contact').first()

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your message has been sent successfully!")
        return redirect("contact")

    context = base_context()
    context.update({
        "form": form,
        "contact_page": contact_page,
    })
    return render(request, "contact.html", context)


def privacy_policy(request):
    page = PageContent.objects.filter(page='privacy').first()
    context = base_context()
    context["page"] = page
    return render(request, "privacy_policy.html", context)


def terms_conditions(request):
    page = PageContent.objects.filter(page='terms').first()
    context = base_context()
    context["page"] = page
    return render(request, "terms_conditions.html", context)


# ================================================
# 👷 Careers
# ================================================
def career(request):
    context = base_context()
    context["vacancies"] = Vacancy.objects.filter(is_active=True)
    return render(request, "career.html", context)


# ================================================
# 📝 Job Application
# ================================================
def job_application(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.vacancy = vacancy
            application.save()
            messages.success(request, 'Your application has been submitted successfully!')
            return redirect('career')
    else:
        form = ApplicationForm()

    context = base_context()
    context.update({
        "form": form,
        "vacancy": vacancy,
    })
    return render(request, "job_application.html", context)


# ================================================
# 🔍 Service Detail
# ================================================
def service_detail(request, slug):
    service = get_object_or_404(Service, slug=slug)
    context = base_context()
    context["service"] = service
    return render(request, "service_detail.html", context)




def unread_count_api(request):

    try:
        from .models import Contact
        count = Contact.objects.filter(is_read=False).count()
    except Exception:
        count = 0
    return JsonResponse({"unread": count})
