import os
import uuid
from django.conf import settings
from django.utils import timezone
from django.db import models
from django.utils.text import slugify
from django.template.loader import render_to_string
from weasyprint import HTML


from ckeditor.fields import RichTextField



class MyCompany(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    logo = models.ImageField(upload_to='serviceapp/images', blank=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    youtube = models.URLField(blank=True, null=True)

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)
    details = RichTextField(blank=True, null=True)
    abn = models.CharField(max_length=255, blank=True, null=True)
    account_name = models.CharField(max_length=255, blank=True, null=True)
    account_number = models.CharField(max_length=255, blank=True, null=True)
    bsb = models.CharField(max_length=255, blank=True, null=True)
    reg_no = models.CharField(max_length=255, blank=True, null=True)
    established = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.name
    


class HeroSection(models.Model):
    title = models.CharField(
        max_length=255, blank=True, null=True,
        help_text="Main heading (leave blank to use default)"
    )
    subtitle = models.TextField(
        blank=True, null=True,
        help_text="Subtext (leave blank to use default)"
    )
    image = models.ImageField(
        upload_to='hero_images/', blank=True, null=True,
        help_text="Hero background image"
    )
    overlay_color = models.CharField(
        max_length=100,
        default="from-black/70 via-black/60 to-transparent",
        help_text="Tailwind gradient overlay (optional)"
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title or "Default Hero Section"




class Service(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='serviceapp/images', blank=True)
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    # def get_absolute_url(self):
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)



class FAQ(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, blank=True, null=True)
    question = models.CharField(max_length=255)
    answer = models.TextField(blank=True)
    is_general = models.BooleanField(default=False)

    def __str__(self):
        return self.question
    

class Contact(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # count unread message
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


QUOTE_STATUS = (
    ('pending', 'Pending'),
    ('replied', 'Replied'),
    ('rejected', 'Rejected'),
    ('approved', 'Approved'),
    ('cancelled', 'Cancelled'),
    ('completed', 'Completed'),
)

class QuoteRequest(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255, blank=True)
    service = models.ManyToManyField(Service, blank=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    message = models.TextField(blank=True)
    status = models.CharField(max_length=255, choices=QUOTE_STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    


    def __str__(self):
        return f'{self.name} - {self.email}'


class Quote(models.Model):
    company = models.ForeignKey(MyCompany, on_delete=models.CASCADE, blank=True, null=True)
    quote_request = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, blank=True, null=True)

    quote_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Quote ID")
    city = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    # message = RichTextField(blank=True, null=True)
    status = models.CharField(max_length=255, choices=QUOTE_STATUS, default="pending")
    mail_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    expiry_date = models.DateField(blank=True, null=True)
    reference = models.CharField(max_length=255, blank=True, null=True)

    quotation_file = models.FileField(upload_to="serviceapp/quotes", blank=True, null=True)
    # invoice_file = models.FileField(upload_to="serviceapp/invoices", blank=True, null=True)

    def __str__(self):
        return f'{self.quote_id} - {self.quote_request.email}'

    @property
    def total(self):
        return sum(item.amount for item in self.items.all())

    @property
    def gst_amount(self):
        from decimal import Decimal
        return self.total * Decimal('0.1')

    @property
    def total_with_gst(self):
        return self.total + self.gst_amount

    def generate_quote(self):
        quotes_dir = os.path.join(settings.MEDIA_ROOT, "serviceapp/quotes")
        os.makedirs(quotes_dir, exist_ok=True)

        filename = f"quote_{self.quote_id}.pdf"
        path = os.path.join(quotes_dir, filename)

        html = render_to_string("quotes/quote.html", {"quote": self})
        HTML(string=html).write_pdf(path)

        Quote.objects.filter(pk=self.pk).update(quotation_file=f"serviceapp/quotes/{filename}")
        return path

    def save(self, *args, **kwargs):
        if not self.quote_id:
            self.quote_id = f"fwz-{uuid.uuid4().hex[:6]}"
            if self.status == 'pending':
                self.status = 'replied'
                if self.quote_request:
                    self.quote_request.status = 'replied'
                    self.quote_request.save()
            if not self.company:
                self.company = MyCompany.objects.first()
        super().save(*args, **kwargs)


class Invoice(models.Model):
    invoice_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="Invoice ID")
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="invoice")
    message = RichTextField(blank=True, null=True)
    invoice_file = models.FileField(upload_to="serviceapp/invoices", blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_sent = models.BooleanField(default=False)

    pay = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    due = models.DecimalField(default=0, decimal_places=2, max_digits=10)
    due_date = models.DateField(blank=True, null=True)
    payment_term = models.CharField(max_length=255, blank=True, null=True, help_text="e.g., 'Due within 3 days', 'Due on receipt'")

    def __str__(self):
        return str(self.invoice_id)
    
    @property
    def total(self):
        return self.quote.total

    @property
    def gst_amount(self):
        return self.quote.gst_amount

    @property
    def total_with_gst(self):
        return self.quote.total_with_gst

    def save(self, *args, **kwargs):
        # if pay deduct from due
        if self.pay:    
            self.due = self.total_with_gst - self.pay
        else:
            self.due = self.quote.total_with_gst

        
        if not self.invoice_id:
            self.invoice_id = f"fwz-inv-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

        self.generate_invoice()

    def generate_invoice(self):
        invoices_dir = os.path.join(settings.MEDIA_ROOT, "serviceapp/invoices")
        os.makedirs(invoices_dir, exist_ok=True)

        filename = f"invoice_{self.invoice_id}.pdf"
        path = os.path.join(invoices_dir, filename)

        html = render_to_string("invoices/invoice.html", {"invoice": self})
        HTML(string=html).write_pdf(path)

        Invoice.objects.filter(pk=self.pk).update(invoice_file=f"serviceapp/invoices/{filename}")
        return path







class QuoteItem(models.Model):
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name="items")
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)


class Review(models.Model):
    name = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    rating = models.IntegerField(blank=True, null=True)
    is_active = models.BooleanField(default=True)  # ✅ Must exist
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.name




class ImageGallery(models.Model):
    service_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='serviceapp/images', blank=True)

    def __str__(self):
        return self.service_name


class Team(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='serviceapp/images', blank=True)
    designation = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Blog(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='serviceapp/images', blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            super().save(*args, **kwargs)



class Career(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255, blank=True)
    resume = models.FileField(upload_to='serviceapp/resumes', blank=True)
    message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


JOB_TYPE =(
    ('full-time', 'Full Time'),
    ('part-time', 'Part Time'),
    ('contract', 'Contract'),
    ('internship', 'Internship'),
    ('volunteer', 'Volunteer'),
    ('other', 'Other'),
)
class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    image = models.ImageField(upload_to='serviceapp/images', blank=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary = models.CharField(max_length=255, blank=True, null=True)
    job_type = models.CharField(max_length=255, choices=JOB_TYPE, default='full-time')
    description = RichTextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    expired_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    
    def is_expired(self):
        if self.expired_at and self.expired_at < timezone.now().date():
            return True
        return False
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            self.save()
        if self.is_expired():
            self.is_active = False
            self.save()
        super().save(*args, **kwargs)


APPLICATION_STATUS = (
    ('pending', 'PENDING'),
    ('shortlist','SHORT LISTED'),
    ('selected', 'SELECTED'),
    ('rejected', 'REJECTED')
)
class Application(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name="applications")
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255, blank=True)
    resume = models.FileField(upload_to='serviceapp/resumes', blank=True)
    message = models.TextField(blank=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    status = models.CharField(max_length=255, choices=APPLICATION_STATUS, default='pending')


    def __str__(self):
        return self.name



MESSAGE_TYPE =(
    ('init', 'Initial Reply'),
    ('quote', 'Quote Sent'),
    ('invoice', 'Invoice Sent'),
    ('shortlist', 'Shortlist Sent'),
    ('selected', 'Selected'),
    ('rejected', 'Rejected'),
)
class EmailMessageTemplate(models.Model):
    type = models.CharField(max_length=255, choices=MESSAGE_TYPE, default='init')
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.subject
    class Meta:
        verbose_name = "Email Message Template"
        verbose_name_plural = "Email Message Templates"


class PageContent(models.Model):
    PAGE_CHOICES = [
        ('privacy', 'Privacy Policy'),
        ('terms', 'Terms & Conditions'),
        ('contact', 'Contact Page'),
        ('about', 'About Page'),  
        ]

    page = models.CharField(max_length=50, choices=PAGE_CHOICES, unique=True)
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=500, blank=True, null=True)
    hero_image = models.ImageField(upload_to='page_heroes/', blank=True, null=True)
    content = RichTextField(blank=True, null=True)  # better for formatting
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_page_display()}"





class ServiceLocation(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Service Location"
        verbose_name_plural = "Service Locations"
        ordering = ['name']

    def __str__(self):
        return self.name



class Pricing(models.Model):
    title = models.CharField(max_length=255)
    price = models.CharField(max_length=100, help_text="Example: 'from $99' or 'POA'")
    features = models.TextField(help_text="List each feature on a new line")
    button_text = models.CharField(max_length=50, default="Get Quote")
    button_link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["order"]
