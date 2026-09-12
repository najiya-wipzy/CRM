import uuid
from django.db import models
from django.contrib.auth.models import User


STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'In Active'),
]
SALUTATION_CHOICES = [
    ('mr', 'Mr.'),
    ('mrs', 'Mrs.'),
    ('ms', 'Ms.'),
    ('miss', 'Miss'),
    ('dr', 'Dr.'),
    ('master', 'Master.'),
    ('madam', 'Madam'),
    ('prof', 'Prof'),
    ('mx', 'Mx'),
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
    ('transgender', 'Transgender'),
    ('prefer_not_to_say', 'Prefer not to say'),
    ('genderqueer', 'Genderqueer'),
    ('non_conforming', 'Non-Conforming'),
]

EMPLOYEE_CHOICES = [
    ('1-10', '1-10'),
    ('11-50', '11-50'),
    ('51-200', '51-200'),
    ('201-500', '201-500'),
    ('501-1000', '501-1000'),
    ('1001+', '1001+'),
]
SOURCE_CHOICES = [
    ('advertisement', 'Advertisement'),
    ('campaign', 'Campaign'),
    ('cold_calling', 'Cold Calling'),
    ('customers_vendor', "Customer's Vendor"),
    ('email', 'Email'),
    ('exhibition', 'Exhibition'),
    ('existing_customer', 'Existing Customer'),
    ('facebook', 'Facebook'),
    ('website', 'Website'),
    ('web_form', 'Web Form'),
    ('walk_in', 'Walk In'),
    ('reference', 'Reference'),
    ('supplier_reference', 'Supplier Reference'),
    ('mass_mailing', 'Mass Mailing'),
]

INDUSTRY_CHOICES = [
    ('accounting', 'Accounting'),
    ('advertising', 'Advertising'),
    ('aerospace', 'Aerospace'),
    ('agriculture', 'Agriculture'),
    ('airline', 'Airline'),
    ('apparel_accessories', 'Apparel & Accessories'),
    ('automotive', 'Automotive'),
    ('banking', 'Banking'),
    ('beverage_tobacco', 'Beverage & Tobacco'),
    ('biotechnology', 'Biotechnology'),
    ('broadcasting', 'Broadcasting'),
    ('brokerage', 'Brokerage'),
    ('chemical', 'Chemical'),
    ('computer', 'Computer'),
    ('consulting', 'Consulting'),
    ('consumer_products', 'Consumer Products'),
    ('cosmetics', 'Cosmetics'),
    ('defense', 'Defense'),
    ('department_stores', 'Department Stores'),
    ('education', 'Education'),
]

LEAD_STATUS_CHOICES = [
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('nurture', 'Nurture'),
    ('qualified', 'Qualified'),
    ('unqualified', 'Unqualified'),
    ('junk', 'Junk'),
    ('converted', 'Converted'),
]

DEAL_STATUS_CHOICES = [
    ('demo_making', 'Demo/Making'),
    ('lost', 'Lost'),
    ('negotiation', 'Negotiation'),
    ('proposal_quotation', 'Proposal/Quotation'),
    ('qualification', 'Qualification'),
    ('ready_to_close', 'Ready to Close'),
    ('won', 'Won'),
]

CONTACT_STATUS_CHOICES = [
    ('passive', 'Passive'),
    ('open', 'Open'),
    ('replied', 'Replied'),
]

ADDRESS_TYPE_CHOICES = [
    ('billing', 'Billing'),
    ('shipping', 'Shipping'),
    ('home', 'Home'),
    ('office', 'Office'),
    ('other', 'Other'),
]

PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]

TASK_STATUS_CHOICES = [
    ('backlog', 'Backlog'),
    ('todo', 'Todo'),
    ('in_progress', 'In Progress'),
    ('done', 'Done'),
    ('canceled', 'Canceled'),
]

TELEPHONY_MEDIUM_CHOICES = [
    ('manual', 'Manual'),
    ('twilio', 'Twilio'),
    ('exotel', 'Exotel'),
]

CALL_TYPE_CHOICES = [
    ('incoming', 'Incoming'),
    ('outgoing', 'Outgoing'),
]

CALL_STATUS_CHOICES = [
    ('initiated', 'Initiated'),
    ('ringing', 'Ringing'),
    ('in_progress', 'In Progress'),
    ('completed', 'Completed'),
    ('failed', 'Failed'),
    ('busy', 'Busy'),
    ('no_answer', 'No Answer'),
    ('queued', 'Queued'),
    ('canceled', 'Canceled'),
]

ROLE_CHOICES = [
    ('admin', 'Admin'),
    ('manager', 'Manager'),
    ('sales', 'Sales'),
]


class Branch_db(models.Model):
    bizla_branch_id = models.CharField(max_length=20)
    uuid = models.UUIDField(default=uuid.uuid4, max_length=240)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Users_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='users')

    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)

    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='sales')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name


class Address_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='addresses')

    address_title = models.CharField(max_length=150)
    address_type = models.CharField(max_length=30, choices=ADDRESS_TYPE_CHOICES)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100, blank=True, null=True)
    city_town = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address_title


class Industry_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='industries')

    industry_name = models.CharField(max_length=150)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.industry_name


class Territory_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='territories')
    territory_manager = models.ForeignKey(Users_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_territories')
    old_parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='old_children')
    parent_crm_territory = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='child_territories')

    territory_name = models.CharField(max_length=150)
    is_group = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.territory_name


class Organization_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='organizations')
    address = models.ForeignKey(Address_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='organizations')
    industry = models.ForeignKey(Industry_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='organizations')
    territory = models.ForeignKey(Territory_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='organizations')

    organization_name = models.CharField(max_length=200)
    website = models.URLField(max_length=255, blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    no_of_employees = models.CharField(max_length=20, choices=EMPLOYEE_CHOICES, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization_name


class Lead_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='leads')
    organization = models.ForeignKey(Organization_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    industry = models.ForeignKey(Industry_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    lead_owner = models.ForeignKey(Users_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')
    territory = models.ForeignKey(Territory_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='leads')

    salutation = models.CharField(max_length=20, choices=SALUTATION_CHOICES, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)

    website = models.URLField(max_length=255, blank=True, null=True)
    no_of_employees = models.CharField( max_length=20, choices=EMPLOYEE_CHOICES, blank=True,null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    lead_status = models.CharField(max_length=30, choices=LEAD_STATUS_CHOICES, default='new')
    source = models.CharField(max_length=100, choices=SOURCE_CHOICES, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Deal_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='deals')
    lead = models.ForeignKey(Lead_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    organization = models.ForeignKey(Organization_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    industry = models.ForeignKey(Industry_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    deal_owner = models.ForeignKey(Users_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')
    territory = models.ForeignKey(Territory_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='deals')

    website = models.URLField(max_length=255, blank=True, null=True)
    no_of_employees = models.CharField(max_length=20, choices=EMPLOYEE_CHOICES, blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    salutation = models.CharField(max_length=20, choices=SALUTATION_CHOICES, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    primary_email = models.EmailField(blank=True, null=True)
    primary_mobile_no = models.CharField(max_length=20, blank=True, null=True)
    gender = models.CharField( max_length=20, choices=GENDER_CHOICES, blank=True, null=True)

    deal_status = models.CharField(max_length=50, choices=DEAL_STATUS_CHOICES, default='qualification')
    probability = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organization.organization_name if self.organization else "Deal"


class Contact_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='contacts')
    company_name = models.ForeignKey(Organization_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')
    address = models.ForeignKey(Address_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='contacts')

    salutation = models.CharField(max_length=20, choices=SALUTATION_CHOICES, blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    mobile_no = models.CharField(max_length=20, blank=True,null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    designation = models.CharField(max_length=150, blank=True, null=True)
    contact_status = models.CharField(max_length=20, choices=CONTACT_STATUS_CHOICES, default='open')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()


class Note_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='notes')
    lead = models.ForeignKey(Lead_db, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    deal = models.ForeignKey(Deal_db, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')

    title = models.CharField(max_length=200)
    content = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class Task_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='tasks')
    lead = models.ForeignKey(Lead_db, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    deal = models.ForeignKey(Deal_db, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    assigned_to = models.ForeignKey(Users_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='low')
    due_date = models.DateTimeField(blank=True, null=True)
    task_status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='backlog')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CallLog_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='call_logs')
    lead = models.ForeignKey(Lead_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='call_logs')
    deal = models.ForeignKey(Deal_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='call_logs')
    caller = models.ForeignKey(Users_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='outgoing_call_logs')
    call_received_by = models.ForeignKey(Users_db, on_delete=models.SET_NULL, null=True, blank=True, related_name='received_call_logs')

    telephony_medium = models.CharField(max_length=30, choices=TELEPHONY_MEDIUM_CHOICES, default='manual')
    call_type = models.CharField(max_length=20, choices=CALL_TYPE_CHOICES)
    to_number = models.CharField(max_length=30)
    from_number = models.CharField(max_length=30)
    call_status = models.CharField(max_length=30, choices=CALL_STATUS_CHOICES)
    duration = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.call_type} - {self.to_number}"


class Product_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='products')

    naming_series = models.CharField(max_length=100, blank=True, null=True)
    product_code = models.CharField(max_length=100)
    product_name = models.CharField(max_length=200, blank=True, null=True)
    disabled = models.BooleanField(default=False)
    standard_selling_rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name or self.product_code


class DealProduct_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='deal_products')
    deal = models.ForeignKey(Deal_db, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product_db, on_delete=models.CASCADE, related_name='deal_products')

    quantity = models.PositiveIntegerField(default=1)
    rate = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name or self.product.product_code


class Attachment_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='attachments')
    lead = models.ForeignKey(Lead_db, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    deal = models.ForeignKey(Deal_db, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')

    file = models.FileField(upload_to='attachments/')
    file_name = models.CharField(max_length=255, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_name or self.file.name


class Comment_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='comments')
    lead = models.ForeignKey(Lead_db, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')
    deal = models.ForeignKey(Deal_db, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')

    comment = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.comment[:50]


class Email_db(models.Model):

    branch = models.ForeignKey(Branch_db, on_delete=models.CASCADE, related_name='emails')
    lead = models.ForeignKey(Lead_db, on_delete=models.CASCADE, null=True, blank=True, related_name='emails')
    deal = models.ForeignKey(Deal_db, on_delete=models.CASCADE, null=True, blank=True, related_name='emails')

    to_email = models.EmailField()
    subject = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    email_status = models.CharField(max_length=30, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subject










