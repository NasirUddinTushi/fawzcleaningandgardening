import os
from django.contrib import admin
from django.db import models
from django.utils.html import format_html
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect


from unfold.admin import ModelAdmin, TabularInline
# import inline from unfol
from unfold.contrib.forms.widgets import WysiwygWidget


from . models import (
    Service,
    FAQ,
    Contact,
    Quote,
    Review,
    ImageGallery,
    Team,
    Blog,
    MyCompany,
    QuoteRequest,
    QuoteItem,
    Invoice,
    Vacancy,
    Application,
    EmailMessageTemplate,
    PageContent,
    ServiceLocation,
    Pricing,
    HeroSection,

)

@admin.register(MyCompany)
class MyCompanyAdmin(ModelAdmin):
    list_display = ('name', 'address', 'abn', 'reg_no', 'established')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'address', 'abn', 'reg_no', 'established')


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('name' , 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}

    formfield_overrides = {
        models.TextField: {
            "widget": WysiwygWidget,
        }
    }



@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ('service', 'question', 'is_general')
    search_fields = ('service', 'question')
    list_filter = ('is_general',)



@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "email", "phone", "created_at", "is_read")
    list_filter = ("is_read",)
    search_fields = ("first_name", "email", "phone", "message")

    # ✅ Admin cannot edit, only view/delete
    def has_change_permission(self, request, obj=None):
        return False

    # ✅ Auto mark message as read when viewed
    def change_view(self, request, object_id, form_url="", extra_context=None):
        obj = self.get_object(request, object_id)
        if obj and not obj.is_read:
            obj.is_read = True
            obj.save(update_fields=["is_read"])
        return super().change_view(request, object_id, form_url, extra_context)


@admin.register(QuoteRequest)
class QuoteRequestAdmin(ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'address', 'status', 'created_at')
    search_fields = ('name', 'email', 'phone', 'city', 'address')
    list_display_links = ('name', 'email', 'phone')
    list_filter = ('status', 'created_at')
    list_per_page = 20
    ordering = ('-created_at',)

    # def has_change_permission(self, request, obj = ...):
    #     return False


@admin.register(Invoice)
class InvoiceAdmin(ModelAdmin):
    list_display = ('invoice_id', 'quote', 'total', 'is_paid', 'view_invoice', 'send_invoice_button')
    search_fields = ('invoice_id', 'quote__quote_id')
    list_filter = ('is_paid', 'is_sent')
    list_per_page = 20
    ordering = ('-created_at',)
    readonly_fields = ('invoice_id',)
    # editable_fields = ('is_paid',)
    list_editable = ('is_paid',)


    def view_invoice(self, obj):
        if obj.invoice_file:
            return format_html('<a href="{}" target="_blank">View Invoice</a>', obj.invoice_file.url)
        return "No invoice"
    view_invoice.short_description = "Invoice"

    def send_invoice_button(self, obj):
        label = "Send" if not obj.is_sent else "Re-send"
        url = reverse('admin:send_invoice', args=[obj.pk])
        return format_html('<a class="button" href="{}">{}</a>', url, label)
    send_invoice_button.short_description = "Send Invoice"
    send_invoice_button.allow_tags = True

    # Add custom admin view
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('send-invoice/<int:invoice_id>/', self.admin_site.admin_view(self.send_invoice_view), name='send_invoice'),
        ]
        return custom_urls + urls

    def send_invoice_view(self, request, invoice_id, *args, **kwargs):
        invoice = self.get_object(request, invoice_id)
        if invoice and invoice.quote and invoice.quote.quote_request:
            # Generate a new PDF
            invoice.generate_invoice()
            invoice.refresh_from_db()
            
            template = EmailMessageTemplate.objects.filter(type="invoice", is_active=True).first()
            # Send the email with the PDF attached
            mail = EmailMessage(
                subject= template.subject if template else f"Your Invoice {invoice.invoice_id}",
                body= template.body if template else "Your invoice is ready. Please find the attached PDF.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[invoice.quote.quote_request.email],
            )
            if invoice.invoice_file and hasattr(invoice.invoice_file, "path"):
                file_path = invoice.invoice_file.path
                if os.path.exists(file_path):
                    mail.attach_file(file_path)
            mail.send(fail_silently=False)
            
            invoice.is_sent = True
            invoice.save()
            self.message_user(request, "Invoice sent successfully!")
        return redirect(request.META.get('HTTP_REFERER'))

    



@admin.register(QuoteItem)
class QuoteItemAdmin(ModelAdmin):
    pass

class QuoteItemInline(TabularInline):
    model = QuoteItem
    extra = 1

@admin.register(Quote)
class QuoteAdmin(ModelAdmin):
    list_display = ('quote_id', "get_quote_request_name", 'city', 'address', 'status', 'quote_link', 'created_at', 'total', 'mail_sent', 'resend_mail')
    search_fields = ('quote_id', 'quote_request__name', 'city', 'address')
    list_per_page = 20
    ordering = ('-created_at',)
    readonly_fields = ('quote_id',)

    fieldsets = (
        ("Quote Information", {
            "fields": ("quote_request", "quote_id", "city", "postal_code", "address", "expiry_date", "reference")
        }),
        ("Files", {
            "fields": ("quotation_file",)
        }),
        # ("Timestamps", {
        #     "fields": ("created_at", "updated_at"),
        # }),
    )

    def get_quote_request_name(self, obj):
        return obj.quote_request.name if obj.quote_request else "-"
    get_quote_request_name.short_description = "Quote Request"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)

        # Hide company field and set default
        if "company" in form.base_fields:
            form.base_fields["company"].initial = MyCompany.objects.first()
            form.base_fields["company"].widget = admin.widgets.AdminHiddenInput()

        # Limit QuoteRequest dropdown to pending requests and the currently associated request
        if "quote_request" in form.base_fields:
            if obj and obj.quote_request:
                # For existing quotes, include the current quote request and all pending requests
                form.base_fields["quote_request"].queryset = QuoteRequest.objects.filter(
                    models.Q(status="pending") | models.Q(pk=obj.quote_request.pk)
                )
            else:
                # For new quotes, only include pending requests
                form.base_fields["quote_request"].queryset = QuoteRequest.objects.filter(status="pending")

        # Hide status field
        if "status" in form.base_fields:
            form.base_fields["status"].widget = admin.widgets.AdminHiddenInput()

        return form
    class Media:
        js = ("admin/js/quote_autofill.js",)  # attach custom JS


    inlines = [QuoteItemInline]

    # # link to show invoice in new tab
    # def invoice_link(self, obj):
    #     if obj.invoice_file:
    #         return format_html('<a href="{}" target="_blank">View Invoice</a>', obj.invoice_file.url)
    #     return "No invoice"
    # invoice_link.short_description = "Invoice"

    def quote_link(self, obj):
        if not obj.quotation_file: 
            return "No quote"
        return format_html(
            '<a href="{}" target="_blank">View Quote</a>', obj.quotation_file.url
        )
    quote_link.short_description = "Quote"

    def resend_mail(self, obj):
        if obj.quote_request:
            url = reverse('admin:resend_quote_mail', args=[obj.pk])
            return format_html('<a class="button" href="{}">Resend Mail</a>', url)
        return "No quote request"
    resend_mail.short_description = "Resend Mail"
    resend_mail.allow_tags = True

    # Add custom admin view
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('resend-mail/<int:quote_id>/', self.admin_site.admin_view(self.resend_quote_mail_view), name='resend_quote_mail'),
        ]
        return custom_urls + urls

    def resend_quote_mail_view(self, request, quote_id, *args, **kwargs):
        from django.http import HttpResponseRedirect
        from django.contrib import messages
        from .models import Quote
        
        quote = self.get_object(request, quote_id)
        if quote and quote.quote_request:
            # Generate a new PDF
            quote.generate_quote()
            quote.refresh_from_db()
            
            template = EmailMessageTemplate.objects.filter(type="quote", is_active=True).first()
            # Send the email
            mail = EmailMessage(
                subject= template.subject if template else "Your Quote is Ready",
                body= template.body if template else "Your quote is ready. Please find the attached PDF.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[quote.quote_request.email],
            )
            if quote.quotation_file and hasattr(quote.quotation_file, "path"):
                file_path = quote.quotation_file.path
                if os.path.exists(file_path):
                    mail.attach_file(file_path)
            mail.send(fail_silently=False)
            
            messages.success(request, "Email resent successfully!")
        else:
            messages.error(request, "Unable to resend email. Quote request not found.")
            
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/'))
@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ("name", "rating", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("name", "message")
    list_filter = ("is_active", "rating")



@admin.register(HeroSection)
class HeroSectionAdmin(ModelAdmin):
    list_display = ("title", "is_active")
    list_editable = ("is_active",)



@admin.register(ImageGallery)
class ImageGalleryAdmin(ModelAdmin):
    list_display = ('service_name', 'image')
    search_fields = ('service_name',)


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ('name', 'designation', 'is_active')
    search_fields = ('name',)


@admin.register(Blog)
class BlogAdmin(ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title',)


@admin.register(Vacancy)
class VacancyAdmin(ModelAdmin):
    list_display = ('title', 'is_active')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_active',)


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    list_display = ('name', 'email', 'phone', 'vacancy', 'review_resume', 'status')
    search_fields = ('name', 'email', 'phone', 'vacancy__title')
    list_filter = ('status', 'vacancy')
    list_per_page = 20
    # ordering = ('-created_at',)
    readonly_fields = ('vacancy',)

    def review_resume(self, obj):
        if obj.resume:
            return format_html('<a href="{}" target="_blank">View Resume</a>', obj.resume.url)
        return "No resume"
    review_resume.short_description = "Resume"

    # def get_urls(self):
    #     from django.urls import path
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path('send-application/<int:application_id>/', self.admin_site.admin_view(self.send_application_view), name='send_application'),
    #     ]
    #     return custom_urls + urls

@admin.register(EmailMessageTemplate)
class EmailMessageTemplateAdmin(ModelAdmin):
    list_display = ('type', 'subject')
    search_fields = ('type', 'subject')
    # formfield_overrides = {
    #     models.TextField: {
    #         "widget": WysiwygWidget,
    #     }
    # }



@admin.register(PageContent)
class PageContentAdmin(ModelAdmin):
    list_display = ("page", "title", "updated_at")
    list_filter = ("page",)




@admin.register(ServiceLocation)
class ServiceLocationAdmin(ModelAdmin):
    list_display = ("name", "description", "is_active")
    list_editable = ("is_active",)
    search_fields = ("name", "description")


@admin.register(Pricing)
class PricingAdmin(ModelAdmin):
    list_display = ("title", "price", "is_active", "order")
    list_editable = ("is_active", "order")