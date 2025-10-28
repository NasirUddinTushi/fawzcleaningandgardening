import os
from django.core.mail import EmailMessage
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Quote, QuoteItem,Contact, Invoice, QuoteRequest, EmailMessageTemplate
from django.core.cache import cache


@receiver(post_save, sender=QuoteItem)
def regenerate_docs_on_item_save(sender, instance, **kwargs):
    quote = instance.quote
    if quote.items.exists():
        quote.generate_quote()
        quote.refresh_from_db()
        
        # If the quote status is "replied" and email hasn't been sent yet, send the email
        if quote.status == "replied" and not quote.mail_sent:
            # Build email
            template = EmailMessageTemplate.objects.filter(type="quote", is_active=True).first()
            email = EmailMessage(
                subject= template.subject if template else "Your quote is ready",
                body= template.body if template else "Your quote is ready. Please find the attached PDF.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[quote.quote_request.email],
            )

            # Attach generated file
            if quote.quotation_file and hasattr(quote.quotation_file, "path"):
                file_path = quote.quotation_file.path
                if os.path.exists(file_path):
                    email.attach_file(file_path)

            email.send(fail_silently=False)
            
            # Mark mail as sent
            quote.mail_sent = True
            quote.save(update_fields=["mail_sent"])

# when a quote request is created, send a mail to the users
@receiver(post_save, sender=QuoteRequest)
def quote_request_recieved_alter(sender, instance, created, **kwargs):
    if created:
        template = EmailMessageTemplate.objects.filter(type="init", is_active=True).first()
        # send a mail - subject: Quote Request Recieved body: We have recieved your quote request. We will get back to you soon. Thanks
        mail = EmailMessage(
            subject= template.subject if template else "Quote Request Recieved",
            body= template.body if template else "We have recieved your quote request. We will get back to you soon. Thanks",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.email],
        )
        mail.send(fail_silently=False)


# Handle quote status changes and send emails accordingly
@receiver(post_save, sender=Quote)
def handle_quote_status(sender, instance, **kwargs):
    # Sync request status
    if instance.quote_request and instance.status == "replied":
        instance.quote_request.status = "replied"
        instance.quote_request.save(update_fields=["status"])

        # Check if the quote has items and email hasn't been sent yet
        if instance.items.exists() and not instance.mail_sent:
            # Generate Quote PDF
            instance.generate_quote()
            # Refresh instance from database to get updated quotation_file field
            instance.refresh_from_db()

            template = EmailMessageTemplate.objects.filter(type="quote", is_active=True).first()
            # Build email
            email = EmailMessage(
                subject= template.subject if template else "Your quote is ready",
                body= template.body if template else "Your quote is ready. Please find the attached PDF.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[instance.quote_request.email],
            )

            # Attach generated file
            if instance.quotation_file and hasattr(instance.quotation_file, "path"):
                file_path = instance.quotation_file.path
                if os.path.exists(file_path):
                    email.attach_file(file_path)

            email.send(fail_silently=False)
            
            # Mark mail as sent
            instance.mail_sent = True
            instance.save(update_fields=["mail_sent"])

    elif instance.quote_request and instance.status == "rejected":
        instance.quote_request.status = "rejected"
        instance.quote_request.save(update_fields=["status"])

    elif instance.quote_request and instance.status == "completed":
        instance.quote_request.status = "completed"
        instance.quote_request.save(update_fields=["status"])

        if instance.items.exists():
            # Get or create Invoice
            invoice, created = Invoice.objects.get_or_create(quote=instance)
            
            # Generate Invoice PDF
            invoice.generate_invoice()

            template = EmailMessageTemplate.objects.filter(type="invoice", is_active=True).first()
            # Build email
            email = EmailMessage(
                subject= template.subject if template else "Your invoice is ready",
                body= template.body if template else "Your invoice is ready. Please find the attached PDF.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[instance.quote_request.email],
            )

            # Attach generated file
            if invoice.invoice_file and hasattr(invoice.invoice_file, "path"):
                file_path = invoice.invoice_file.path
                if os.path.exists(file_path):
                    email.attach_file(file_path)

            email.send(fail_silently=False)
        

# save invoice: generate pdf when invoice is created and change quote status to completed
@receiver(post_save, sender=Invoice)
def handle_invoice_status(sender, instance, created, **kwargs):
    if created:
        # refresh database
        instance.refresh_from_db()
        # Generate Invoice PDF
        instance.generate_invoice()
        # Change quote status to completed
        instance.quote.status = "completed"
        instance.quote.save(update_fields=["status"])
        


# @receiver(post_save, sender=Quote)
# def handle_quote_status(sender, instance, **kwargs):
#     # Sync request status
#     if instance.quote_request and instance.status == "replied":
#         instance.quote_request.status = "replied"
#         instance.quote_request.save(update_fields=["status"])

#         if instance.items.exists():
#             # Generate Quote PDF
#             instance.generate_quote()

#             # Build email
#             email = EmailMessage(
#                 subject="Your quote is ready",
#                 body="Your quote is ready. Please find the attached PDF.",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 to=[instance.quote_request.email],
#             )

#             # Attach generated file
#             if instance.quotation_file and hasattr(instance.quotation_file, "path"):
#                 file_path = instance.quotation_file.path
#                 if os.path.exists(file_path):
#                     email.attach_file(file_path)

#             email.send(fail_silently=False)

#     elif instance.quote_request and instance.status == "rejected":
#         instance.quote_request.status = "rejected"
#         instance.quote_request.save(update_fields=["status"])

#     elif instance.quote_request and instance.status == "completed":
#         instance.quote_request.status = "completed"
#         instance.quote_request.save(update_fields=["status"])

#         if instance.items.exists():
#             # Get or create Invoice
#             invoice, created = Invoice.objects.get_or_create(quote=instance)
            
#             # Generate Invoice PDF
#             invoice.generate_invoice()

#             # Build email
#             email = EmailMessage(
#                 subject="Your invoice is ready",
#                 body="Your invoice is ready. Please find the attached PDF.",
#                 from_email=settings.DEFAULT_FROM_EMAIL,
#                 to=[instance.quote_request.email],
#             )

#             # Attach generated file
#             if invoice.invoice_file and hasattr(invoice.invoice_file, "path"):
#                 file_path = invoice.invoice_file.path
#                 if os.path.exists(file_path):
#                     email.attach_file(file_path)

#             email.send(fail_silently=False)





@receiver(post_save, sender=Contact)
def clear_unread_cache(sender, instance, **kwargs):
    # Whenever a contact changes (read/unread), clear the cached count
    cache.delete("unread_message_count")