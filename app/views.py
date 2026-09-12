from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import *
from decimal import Decimal
from django.db import transaction
from django.http import JsonResponse
import re
from django.db.models import (Avg, Sum, Count,F, Value, ExpressionWrapper, DecimalField, DurationField)
from django.db.models.functions import TruncDate
from datetime import timedelta
from django.utils import timezone
import json


def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")

        try:

            branch = Branch_db.objects.filter(
                username=username,
                password=password
            ).first()

            user = Users_db.objects.filter(
                username=username,
                password=password
            ).first()

            if branch:

                if branch.status != 'active':
                    messages.error(request, "Your account is inactive")
                    return redirect('login')

                request.session['B_id'] = branch.id
                request.session['user_type'] = 'branch'
                return redirect('dashboard')

            elif user:

                if user.status != 'active':
                    messages.error(request, "Your account is inactive")
                    return redirect('login')

                request.session['B_id'] = user.branch.id
                request.session['U_id'] = user.id
                request.session['user_type'] = 'user'
                return redirect('dashboard')

            else:
                messages.error(request, "Invalid Username and Password")
                return redirect('login')

        except Exception:
            messages.error(request, "Something went wrong")
            return redirect('login')
    return render(request, "login.html")


def dashboard(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']
        branch = Branch_db.objects.filter(id=B_id)

        return render(request, 'dashboard.html')
    else:
        return redirect('login')


def leads(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        # Leads
        if request.session['user_type'] == 'branch':

            leads_list = Lead_db.objects.filter(
                branch=branch,
                status="active"
            ).select_related(
                "organization",
                "industry",
                "lead_owner",
                "territory"
            ).order_by("-created_at")

        else:

            U_id = request.session['U_id']

            leads_list = Lead_db.objects.filter(
                branch=branch,
                lead_owner_id=U_id,
                status="active"
            ).select_related(
                "organization",
                "industry",
                "lead_owner",
                "territory"
            ).order_by("-created_at")

        # Dropdown Data

        organizations = Organization_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("organization_name")

        industries = Industry_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("industry_name")

        territories = Territory_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("territory_name")

        users = Users_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("full_name")

        addresses = Address_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("address_title")

        return render(request, "lead.html", {

            "leads": leads_list,

            "organizations": organizations,
            "industries": industries,
            "territories": territories,
            "users": users,
            "addresses": addresses,

            "salutation_choices":
                Lead_db._meta.get_field("salutation").choices,

            "gender_choices":
                Lead_db._meta.get_field("gender").choices,

            "employee_choices":
                Lead_db._meta.get_field("no_of_employees").choices,

            "lead_status_choices":
                Lead_db._meta.get_field("lead_status").choices,

            "source_choices":
                Lead_db._meta.get_field("source").choices,

            "address_type_choices":
                Address_db._meta.get_field("address_type").choices,

            "branch": branch
        })

    else:
        return redirect('login')


def add_lead(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            salutation = request.POST.get("salutation")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            email = request.POST.get("email")
            mobile_no = request.POST.get("mobile_no")
            gender = request.POST.get("gender")

            organization_id = request.POST.get("organization")
            website = request.POST.get("website")
            no_of_employees = request.POST.get("no_of_employees")
            territory_id = request.POST.get("territory")
            annual_revenue = request.POST.get("annual_revenue") or 0
            industry_id = request.POST.get("industry")

            lead_status = request.POST.get("lead_status", "new")
            source = request.POST.get("source")

            if request.session['user_type'] == 'branch':

                lead_owner_id = request.POST.get("lead_owner")

            else:

                lead_owner_id = request.session['U_id']

            Lead_db.objects.create(
                branch=branch,
                salutation=salutation,
                first_name=first_name,
                last_name=last_name,
                email=email,
                mobile_no=mobile_no,
                gender=gender,
                organization_id=organization_id or None,
                website=website,
                no_of_employees=no_of_employees,
                annual_revenue=annual_revenue,
                industry_id=industry_id or None,
                territory_id=territory_id or None,
                lead_status=lead_status,
                source=source,
                lead_owner_id=lead_owner_id or None,
                status="active"
            )

            messages.success(request, "Lead created successfully.")

            return redirect('leads')

        return redirect('leads')

    else:
        return redirect('login')


def lead_detail(request, lead_id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        # ================================
        # LEAD
        # ================================

        if request.session['user_type'] == 'branch':

            lead = get_object_or_404(
                Lead_db.objects.select_related(
                    "organization",
                    "industry",
                    "lead_owner",
                    "territory"
                ),
                id=lead_id,
                branch=branch,
                status="active"
            )

        else:

            U_id = request.session['U_id']

            lead = get_object_or_404(
                Lead_db.objects.select_related(
                    "organization",
                    "industry",
                    "lead_owner",
                    "territory"
                ),
                id=lead_id,
                branch=branch,
                lead_owner_id=U_id,
                status="active"
            )


        # ================================
        # CONTACTS
        # ================================

        contacts = Contact_db.objects.filter(
            branch=branch,
            status="active",
            company_name=lead.organization
        )


        # ================================
        # EMAILS
        # ================================

        emails_list = Email_db.objects.filter(
            branch=branch,
            lead=lead,
            status="active"
        ).order_by("-created_at")


        # ================================
        # COMMENTS
        # ================================

        comments_list = Comment_db.objects.filter(
            branch=branch,
            lead=lead,
            status="active"
        ).order_by("-created_at")


        # ================================
        # CALLS
        # ================================

        calls_list = CallLog_db.objects.filter(
            branch=branch,
            lead=lead,
            status="active"
        ).select_related(
            "caller",
            "call_received_by"
        ).order_by("-created_at")


        # ================================
        # TASKS
        # ================================

        tasks_list = Task_db.objects.filter(
            branch=branch,
            lead=lead,
            status="active"
        ).select_related(
            "assigned_to"
        ).order_by("-created_at")


        # ================================
        # NOTES
        # ================================

        notes_list = Note_db.objects.filter(
            branch=branch,
            lead=lead,
            status="active"
        ).order_by("-created_at")


        # ================================
        # ATTACHMENTS
        # ================================

        attachments_list = Attachment_db.objects.filter(
            branch=branch,
            lead=lead,
            status="active"
        ).order_by("-created_at")


        # ================================
        # CONTEXT
        # ================================

        return render(
            request,
            "lead_detail.html",
            {
                "branch": branch,
                "lead": lead,
                "contacts": contacts,

                "emails": emails_list,
                "comments": comments_list,
                "calls": calls_list,
                "tasks": tasks_list,
                "notes": notes_list,
                "attachments": attachments_list,
            }
        )

    else:
        return redirect('login')


def delete_lead(request, lead_id):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.session['user_type'] == 'branch':

            lead = get_object_or_404(
                Lead_db,
                id=lead_id,
                branch=branch,
                status="active"
            )

        else:

            U_id = request.session['U_id']

            lead = get_object_or_404(
                Lead_db,
                id=lead_id,
                branch=branch,
                lead_owner_id=U_id,
                status="active"
            )

        lead.status = "inactive"
        lead.save()

        messages.success(request, "Lead deleted successfully.")

        return redirect('leads')

    else:
        return redirect('login')


def add_lead_organization(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            organization_name = request.POST.get(
                "organization_name", ""
            ).strip()

            website = request.POST.get(
                "website", ""
            ).strip()

            annual_revenue = request.POST.get(
                "annual_revenue", "0"
            ) or "0"

            no_of_employees = request.POST.get(
                "no_of_employees"
            ) or None

            territory_id = request.POST.get(
                "territory"
            ) or None

            industry_id = request.POST.get(
                "industry"
            ) or None

            address_id = request.POST.get(
                "address"
            ) or None

            if not organization_name:
                return JsonResponse({
                    "success": False,
                    "message": "Organization name is required."
                })

            territory = None

            if territory_id:
                territory = Territory_db.objects.filter(
                    id=territory_id,
                    branch=branch,
                    status="active"
                ).first()

            industry = None

            if industry_id:
                industry = Industry_db.objects.filter(
                    id=industry_id,
                    branch=branch,
                    status="active"
                ).first()

            address = None

            if address_id:
                address = Address_db.objects.filter(
                    id=address_id,
                    branch=branch,
                    status="active"
                ).first()

            organization = Organization_db.objects.create(
                branch=branch,
                organization_name=organization_name,
                website=website or None,
                annual_revenue=annual_revenue,
                no_of_employees=no_of_employees,
                territory=territory,
                industry=industry,
                address=address,
                status="active"
            )

            return JsonResponse({
                "success": True,
                "id": organization.id,
                "name": organization.organization_name
            })

        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        })

    else:
        return redirect("login")


def add_address(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "message": "Invalid request."
            })

        address_title = request.POST.get("address_title", "").strip()
        address_type = request.POST.get("address_type", "").strip()
        address_line1 = request.POST.get("address_line1", "").strip()
        address_line2 = request.POST.get("address_line2", "").strip()
        country = request.POST.get("country", "").strip()
        state_province = request.POST.get("state_province", "").strip()
        city_town = request.POST.get("city_town", "").strip()
        postal_code = request.POST.get("postal_code", "").strip()

        if not address_title:
            return JsonResponse({
                "success": False,
                "message": "Address title is required."
            })

        if not address_type:
            return JsonResponse({
                "success": False,
                "message": "Address type is required."
            })

        if not address_line1:
            return JsonResponse({
                "success": False,
                "message": "Address Line 1 is required."
            })

        if not country:
            return JsonResponse({
                "success": False,
                "message": "Country is required."
            })

        if not city_town:
            return JsonResponse({
                "success": False,
                "message": "City/Town is required."
            })

        address = Address_db.objects.create(
            branch=branch,
            address_title=address_title,
            address_type=address_type,
            address_line1=address_line1,
            address_line2=address_line2 or None,
            country=country,
            state_province=state_province or None,
            city_town=city_town,
            postal_code=postal_code or None,
            status="active"
        )

        return JsonResponse({
            "success": True,
            "id": address.id,
            "name": address.address_title,
            "country": address.country,
            "state": address.state_province or "",
            "city": address.city_town
        })

    else:
        return redirect("login")


def add_territory(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "message": "Invalid request."
            })

        name = request.POST.get(
            "territory_name",
            request.POST.get("name", "")
        ).strip()

        if not name:
            return JsonResponse({
                "success": False,
                "message": "Territory name is required."
            })

        manager_id = request.POST.get(
            "territory_manager"
        ) or None

        territory_manager = None

        if manager_id:
            territory_manager = Users_db.objects.filter(
                id=manager_id,
                branch=branch,
                status="active"
            ).first()

        old_parent_id = request.POST.get(
            "old_parent"
        ) or None

        old_parent = None

        if old_parent_id:
            old_parent = Territory_db.objects.filter(
                id=old_parent_id,
                branch=branch,
                status="active"
            ).first()

        parent_id = request.POST.get(
            "parent_crm_territory"
        ) or None

        parent_crm_territory = None

        if parent_id:
            parent_crm_territory = Territory_db.objects.filter(
                id=parent_id,
                branch=branch,
                status="active"
            ).first()

        is_group_value = request.POST.get(
            "is_group",
            "false"
        ).lower()

        is_group = is_group_value in [
            "true",
            "1",
            "yes",
            "on"
        ]

        territory = Territory_db.objects.filter(
            branch=branch,
            territory_name=name
        ).first()

        if territory:
            return JsonResponse({
                "success": False,
                "message": "This territory already exists."
            })

        territory = Territory_db.objects.create(
            branch=branch,
            territory_manager=territory_manager,
            old_parent=old_parent,
            parent_crm_territory=parent_crm_territory,
            territory_name=name,
            is_group=is_group,
            status="active"
        )

        return JsonResponse({
            "success": True,
            "id": territory.id,
            "name": territory.territory_name
        })

    else:
        return redirect("login")


def add_industry(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            name = request.POST.get("name", "").strip()

            if not name:
                return JsonResponse({
                    "success": False,
                    "message": "Industry name is required."
                })

            industry, created = Industry_db.objects.get_or_create(
                branch=branch,
                industry_name=name,
                defaults={
                    "status": "active"
                }
            )

            return JsonResponse({
                "success": True,
                "id": industry.id,
                "name": industry.industry_name
            })

        return JsonResponse({
            "success": False,
            "message": "Invalid request."
        })

    else:
        return redirect("login")


def deals(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        deals_list = Deal_db.objects.filter(
            branch=branch,
            status="active"
        ).select_related(
            "organization",
            "lead",
            "industry",
            "deal_owner",
            "territory"
        ).order_by("-created_at")

        organizations = Organization_db.objects.filter(
            branch=branch,
            status="active"
        ).select_related(
            "industry",
            "territory"
        ).order_by("organization_name")

        industries = Industry_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("industry_name")

        territories = Territory_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("territory_name")

        users = Users_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("full_name")

        leads = Lead_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by(
            "first_name",
            "last_name"
        )

        return render(
            request,
            "deals.html",
            {
                "deals": deals_list,
                "organizations": organizations,
                "industries": industries,
                "territories": territories,
                "users": users,
                "leads": leads,

                "employee_choices":
                    Deal_db._meta.get_field(
                        "no_of_employees"
                    ).choices,

                "salutation_choices":
                    Deal_db._meta.get_field(
                        "salutation"
                    ).choices,

                "gender_choices":
                    Deal_db._meta.get_field(
                        "gender"
                    ).choices,

                "deal_status_choices":
                    Deal_db._meta.get_field(
                        "deal_status"
                    ).choices,

                "branch": branch,
            }
        )

    else:
        return redirect("login")


def add_deal(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method != "POST":
            return redirect("deals")


        # ================================
        # FORM VALUES
        # ================================

        organization_id = request.POST.get(
            "organization"
        ) or None

        lead_id = request.POST.get(
            "lead"
        ) or None

        industry_id = request.POST.get(
            "industry"
        ) or None

        territory_id = request.POST.get(
            "territory"
        ) or None

        deal_owner_id = request.POST.get(
            "deal_owner"
        ) or None


        website = request.POST.get(
            "website",
            ""
        ).strip()

        no_of_employees = request.POST.get(
            "no_of_employees"
        ) or None

        annual_revenue = request.POST.get(
            "annual_revenue",
            "0"
        ) or 0


        salutation = request.POST.get(
            "salutation"
        ) or None

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip()

        primary_email = request.POST.get(
            "primary_email",
            ""
        ).strip()

        primary_mobile_no = request.POST.get(
            "primary_mobile_no",
            ""
        ).strip()

        gender = request.POST.get(
            "gender"
        ) or None


        deal_status = request.POST.get(
            "deal_status"
        ) or "qualification"


        probability = request.POST.get(
            "probability",
            "0"
        ) or 0


        # ================================
        # ORGANIZATION
        # ================================

        organization = None

        if organization_id:

            organization = Organization_db.objects.filter(
                id=organization_id,
                branch=branch,
                status="active"
            ).first()


        # ================================
        # LEAD
        # ================================

        lead = None

        if lead_id:

            lead = Lead_db.objects.filter(
                id=lead_id,
                branch=branch,
                status="active"
            ).first()


        # ================================
        # INDUSTRY
        # ================================

        industry = None

        if industry_id:

            industry = Industry_db.objects.filter(
                id=industry_id,
                branch=branch,
                status="active"
            ).first()


        # ================================
        # TERRITORY
        # ================================

        territory = None

        if territory_id:

            territory = Territory_db.objects.filter(
                id=territory_id,
                branch=branch,
                status="active"
            ).first()


        # ================================
        # DEAL OWNER
        # ================================

        deal_owner = None

        if deal_owner_id:

            deal_owner = Users_db.objects.filter(
                id=deal_owner_id,
                branch=branch,
                status="active"
            ).first()

        elif request.session.get("user_type") == "user":

            U_id = request.session.get("U_id")

            deal_owner = Users_db.objects.filter(
                id=U_id,
                branch=branch,
                status="active"
            ).first()


        # ================================
        # CREATE DEAL
        # ================================

        deal = Deal_db.objects.create(

            branch=branch,

            organization=organization,

            lead=lead,

            industry=industry,

            territory=territory,

            deal_owner=deal_owner,

            website=website or None,

            no_of_employees=no_of_employees,

            annual_revenue=annual_revenue,

            salutation=salutation,

            first_name=first_name or None,

            last_name=last_name or None,

            primary_email=primary_email or None,

            primary_mobile_no=primary_mobile_no or None,

            gender=gender,

            deal_status=deal_status,

            probability=probability,

            status="active",
        )


        messages.success(
            request,
            "Deal created successfully."
        )

        return redirect("deals")

    else:
        return redirect("login")


def deal_detail(request, deal_id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        # ================================
        # DEAL
        # ================================

        deal = get_object_or_404(
            Deal_db.objects.select_related(
                "lead",
                "organization",
                "industry",
                "deal_owner",
                "territory"
            ),
            id=deal_id,
            branch=branch,
            status="active"
        )


        # ================================
        # CONTACTS
        # ================================

        contacts = Contact_db.objects.filter(
            branch=branch,
            status="active",
            company_name=deal.organization
        )


        # ================================
        # NOTES
        # ================================

        notes_list = Note_db.objects.filter(
            branch=branch,
            deal=deal,
            status="active"
        ).order_by("-created_at")


        # ================================
        # TASKS
        # ================================

        tasks_list = Task_db.objects.filter(
            branch=branch,
            deal=deal,
            status="active"
        ).select_related(
            "assigned_to"
        ).order_by("-created_at")


        # ================================
        # ATTACHMENTS
        # ================================

        attachments_list = Attachment_db.objects.filter(
            branch=branch,
            deal=deal,
            status="active"
        ).order_by("-created_at")


        # ================================
        # COMMENTS
        # ================================

        comments_list = Comment_db.objects.filter(
            branch=branch,
            deal=deal,
            status="active"
        ).order_by("-created_at")


        # ================================
        # EMAILS
        # ================================

        emails_list = Email_db.objects.filter(
            branch=branch,
            deal=deal,
            status="active"
        ).order_by("-created_at")


        # ================================
        # PRODUCTS
        # ================================

        deal_products = DealProduct_db.objects.filter(
            branch=branch,
            deal=deal,
            status="active"
        ).select_related(
            "product"
        )


        # ================================
        # CONTEXT
        # ================================

        return render(
            request,
            "deal_tech_detail.html",
            {
                "branch": branch,

                "deal": deal,

                "contacts": contacts,

                "notes": notes_list,

                "tasks": tasks_list,

                "attachments": attachments_list,

                "comments": comments_list,

                "emails": emails_list,

                "deal_products": deal_products,
            }
        )

    else:
        return redirect("login")


def delete_deal(request, id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        deal = get_object_or_404(
            Deal_db,
            id=id,
            branch=branch,
            status="active"
        )

        deal.status = "inactive"
        deal.save()

        messages.success(request, "Deal deleted successfully.")

        return redirect("deals")

    else:
        return redirect("login")


def organizations(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        organizations = Organization_db.objects.filter(
            branch=branch,
            status="active"
        ).select_related(
            "industry",
            "territory",
            "address"
        ).order_by("-created_at")

        industries = Industry_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("industry_name")

        territories = Territory_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("territory_name")

        addresses = Address_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("address_title")

        users = Users_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("full_name")

        return render(request, "organizations.html", {
            "organizations": organizations,
            "industries": industries,
            "territories": territories,
            "addresses": addresses,
            "users": users,

            "employee_choices":
                Organization_db._meta.get_field(
                    "no_of_employees"
                ).choices,

            "address_type_choices":
                Address_db._meta.get_field(
                    "address_type"
                ).choices,

            "branch": branch
        })

    else:
        return redirect("login")


def add_organization_full(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            organization_name = request.POST.get(
                "organization_name", ""
            ).strip()

            website = request.POST.get(
                "website", ""
            ).strip()

            annual_revenue = request.POST.get(
                "annual_revenue", "0"
            ) or "0"

            no_of_employees = request.POST.get(
                "no_of_employees"
            ) or None

            territory_id = request.POST.get(
                "territory"
            ) or None

            industry_id = request.POST.get(
                "industry"
            ) or None

            address_id = request.POST.get(
                "address"
            ) or None


            territory = None

            if territory_id:
                territory = Territory_db.objects.filter(
                    id=territory_id,
                    branch=branch,
                    status="active"
                ).first()


            industry = None

            if industry_id:
                industry = Industry_db.objects.filter(
                    id=industry_id,
                    branch=branch,
                    status="active"
                ).first()


            address = None

            if address_id:
                address = Address_db.objects.filter(
                    id=address_id,
                    branch=branch,
                    status="active"
                ).first()


            Organization_db.objects.create(
                branch=branch,
                organization_name=organization_name,
                website=website or None,
                annual_revenue=annual_revenue,
                no_of_employees=no_of_employees,
                territory=territory,
                industry=industry,
                address=address,
                status="active"
            )

            messages.success(
                request,
                "Organization created successfully."
            )

            return redirect("organizations")

        return redirect("organizations")

    else:
        return redirect("login")


def organization_detail(request, organization_id):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        organization = get_object_or_404(
            Organization_db.objects.select_related(
                "industry",
                "territory",
                "address"
            ),
            id=organization_id,
            branch=branch,
            status="active"
        )

        organization_deals = Deal_db.objects.filter(
            branch=branch,
            organization=organization,
            status="active"
        ).select_related(
            "deal_owner"
        ).order_by("-created_at")

        organization_contacts = Contact_db.objects.filter(
            branch=branch,
            company_name=organization,
            status="active"
        ).order_by("-created_at")

        return render(request, "organization_detail.html", {
            "branch": branch,
            "organization": organization,
            "organization_deals": organization_deals,
            "organization_contacts": organization_contacts
        })

    else:
        return redirect("login")


def delete_organization(request, id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            organization = Organization_db.objects.filter(
                id=id,
                branch=branch,
                status="active"
            ).first()

            if not organization:
                messages.error(
                    request,
                    "Organization not found."
                )
                return redirect("organizations")

            organization.status = "inactive"
            organization.save()

            messages.success(
                request,
                "Organization deleted successfully."
            )

            return redirect("organizations")

        return redirect(
            "organization_detail",
            organization_id=id
        )

    else:
        return redirect("login")


def calls(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        calls_list = (
            CallLog_db.objects
            .filter(
                branch=branch,
                status="active"
            )
            .select_related(
                "caller",
                "call_received_by",
                "lead",
                "deal",
                "deal__organization",
                "lead__organization"
            )
            .order_by("-created_at")
        )

        users_list = (
            Users_db.objects
            .filter(
                branch=branch,
                status="active"
            )
            .order_by("full_name")
        )

        return render(
            request,
            "calls.html",
            {
                "calls": calls_list,
                "users": users_list,
                "branch": branch
            }
        )

    else:
        return redirect("login")


def add_call(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method != "POST":
            return JsonResponse({
                "success": False,
                "message": "Invalid request method."
            })

        call_type = request.POST.get(
            "call_type", ""
        ).strip().lower()

        call_status = request.POST.get(
            "call_status", ""
        ).strip().lower()

        to_number = request.POST.get(
            "to_number", ""
        ).strip()

        from_number = request.POST.get(
            "from_number", ""
        ).strip()

        duration = request.POST.get(
            "duration", "0"
        ).strip()

        caller_id = request.POST.get(
            "caller", ""
        ).strip()

        received_by_id = request.POST.get(
            "call_received_by", ""
        ).strip()


        # VALIDATE CALL TYPE

        if call_type not in ["incoming", "outgoing"]:

            return JsonResponse({
                "success": False,
                "message": "Please select call type."
            })


        # VALIDATE NUMBERS

        if not to_number:

            return JsonResponse({
                "success": False,
                "message": "To Number is required."
            })

        if not from_number:

            return JsonResponse({
                "success": False,
                "message": "From Number is required."
            })


        # VALIDATE STATUS

        valid_statuses = [
            "initiated",
            "ringing",
            "in_progress",
            "completed",
            "failed",
            "busy",
            "no_answer",
            "queued",
            "canceled",
        ]

        if call_status not in valid_statuses:

            return JsonResponse({
                "success": False,
                "message": "Please select a valid call status."
            })


        # DURATION

        try:
            duration = int(duration or 0)

        except (ValueError, TypeError):
            duration = 0


        # CALLER / RECEIVED BY

        caller = None
        call_received_by = None


        # OUTGOING

        if call_type == "outgoing":

            if caller_id:

                caller = get_object_or_404(
                    Users_db,
                    id=caller_id,
                    branch=branch,
                    status="active"
                )


        # INCOMING

        elif call_type == "incoming":

            if received_by_id:

                call_received_by = get_object_or_404(
                    Users_db,
                    id=received_by_id,
                    branch=branch,
                    status="active"
                )


        # CREATE CALL

        call = CallLog_db.objects.create(

            branch=branch,

            caller=caller,
            call_received_by=call_received_by,

            telephony_medium="manual",

            call_type=call_type,

            to_number=to_number,
            from_number=from_number,

            call_status=call_status,

            duration=duration,

            status="active"
        )


        return redirect("calls")

    else:
        return redirect("login")


def call_detail(request, call_id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        call = get_object_or_404(
            CallLog_db.objects.select_related(
                "caller",
                "call_received_by",
                "lead",
                "deal",
                "deal__organization",
                "lead__organization"
            ),
            pk=call_id,
            branch=branch,
            status="active"
        )

        return render(
            request,
            "call_detail.html",
            {
                "call": call,
                "branch": branch
            }
        )

    else:
        return redirect("login")


def delete_call(request, id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        call = get_object_or_404(
            CallLog_db,
            id=id,
            branch=branch,
            status="active"
        )

        call.status = "inactive"
        call.save()

        messages.success(
            request,
            "Call deleted successfully."
        )

        return redirect("calls")

    else:
        return redirect("login")


def tasks(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        tasks_list = Task_db.objects.filter(
            branch=branch,
            status="active"
        ).select_related(
            "assigned_to",
            "lead",
            "deal"
        ).order_by("-updated_at")

        users_list = Users_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("full_name")

        return render(
            request,
            "tasks.html",
            {
                "tasks": tasks_list,
                "users": users_list,
                "branch": branch,
            }
        )

    else:
        return redirect("login")


def add_task(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            title = request.POST.get(
                "title", ""
            ).strip()

            description = request.POST.get(
                "description", ""
            ).strip()

            priority = request.POST.get(
                "priority", "low"
            )

            assigned_to_id = request.POST.get(
                "assigned_to"
            )

            due_date = request.POST.get(
                "due_date"
            ) or None

            task_status = request.POST.get(
                "task_status", "backlog"
            )


            if not title:

                messages.error(
                    request,
                    "Title is required."
                )

                return redirect("tasks")


            assigned_to = None

            if assigned_to_id:

                assigned_to = get_object_or_404(
                    Users_db,
                    id=assigned_to_id,
                    branch=branch,
                    status="active"
                )


            task = Task_db.objects.create(

                branch=branch,

                title=title,

                description=description,

                priority=priority,

                assigned_to=assigned_to,

                due_date=due_date,

                task_status=task_status,

                status="active"
            )


            return redirect("tasks")

        return redirect("tasks")

    else:
        return redirect("login")


def delete_task(request, id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        task = get_object_or_404(
            Task_db,
            id=id,
            branch=branch,
            status="active"
        )

        task.status = "inactive"
        task.save()

        messages.success(
            request,
            "Task deleted successfully."
        )

        return redirect("tasks")

    else:
        return redirect("login")


def notes(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        notes_list = Note_db.objects.filter(
            branch=branch,
            status="active"
        ).select_related(
            "lead",
            "deal"
        ).order_by("-created_at")

        return render(
            request,
            "notes.html",
            {
                "notes": notes_list,
                "branch": branch,
            }
        )

    else:
        return redirect("login")


def add_note(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            title = request.POST.get(
                "title", ""
            ).strip()

            content = request.POST.get(
                "content", ""
            ).strip()

            if not title:

                messages.error(
                    request,
                    "Title is required."
                )

                return redirect("notes")

            note = Note_db.objects.create(
                branch=branch,
                title=title,
                content=content,
                status="active"
            )

            return redirect(
                "note_detail",
                note_id=note.id
            )

        return redirect("notes")

    else:
        return redirect("login")


def note_detail(request, note_id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        note = get_object_or_404(
            Note_db.objects.select_related(
                "lead",
                "deal"
            ),
            id=note_id,
            branch=branch,
            status="active"
        )

        return render(
            request,
            "note_detail.html",
            {
                "branch": branch,
                "note": note,
            }
        )

    else:
        return redirect("login")


def delete_note(request, id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        note = get_object_or_404(
            Note_db,
            id=id,
            branch=branch,
            status="active"
        )

        note.status = "inactive"
        note.save()

        messages.success(
            request,
            "Note deleted successfully."
        )

        return redirect("notes")

    else:
        return redirect("login")


def contacts(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        contacts = Contact_db.objects.filter(
            branch=branch,
            status="active"
        ).select_related(
            "company_name",
            "address"
        ).order_by("-updated_at")

        organizations = Organization_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("organization_name")

        industries = Industry_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("industry_name")

        territories = Territory_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("territory_name")

        addresses = Address_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("address_title")

        employee_choices = Organization_db._meta.get_field(
            "no_of_employees"
        ).choices

        return render(request, "contacts.html", {

            "contacts": contacts,

            "organizations": organizations,

            "addresses": addresses,

            "industries": industries,

            "territories": territories,

            "employee_choices": employee_choices,

            "salutation_choices": SALUTATION_CHOICES,

            "gender_choices": GENDER_CHOICES,

            "contact_status_choices": CONTACT_STATUS_CHOICES,

            "address_type_choices": ADDRESS_TYPE_CHOICES,

            "branch": branch,
        })

    else:
        return redirect("login")


def add_contact(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method != "POST":
            return redirect("contacts")

        first_name = request.POST.get(
            "first_name",
            ""
        ).strip()

        if not first_name:

            messages.error(
                request,
                "First Name is required."
            )

            return redirect("contacts")

        salutation = request.POST.get(
            "salutation"
        ) or None

        last_name = request.POST.get(
            "last_name",
            ""
        ).strip() or None

        email = request.POST.get(
            "email",
            ""
        ).strip() or None

        mobile_no = request.POST.get(
            "mobile_no",
            ""
        ).strip() or None

        gender = request.POST.get(
            "gender"
        ) or None

        designation = request.POST.get(
            "designation",
            ""
        ).strip() or None

        contact_status = request.POST.get(
            "contact_status"
        ) or "open"

        organization_id = request.POST.get(
            "company_name"
        ) or None

        address_id = request.POST.get(
            "address"
        ) or None


        # ORGANIZATION

        company_name = None

        if organization_id:

            company_name = Organization_db.objects.filter(
                id=organization_id,
                branch=branch,
                status="active"
            ).first()


        # ADDRESS

        address = None

        if address_id:

            address = Address_db.objects.filter(
                id=address_id,
                branch=branch,
                status="active"
            ).first()


        # CREATE CONTACT

        Contact_db.objects.create(

            branch=branch,

            company_name=company_name,

            address=address,

            salutation=salutation,

            first_name=first_name,

            last_name=last_name,

            email=email,

            mobile_no=mobile_no,

            gender=gender,

            designation=designation,

            contact_status=contact_status,

            status="active",
        )


        messages.success(
            request,
            f"Contact '{first_name}' created successfully."
        )

        return redirect("contacts")

    else:
        return redirect("login")


def contact_detail(request, contact_id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        contact = get_object_or_404(
            Contact_db.objects.select_related(
                "company_name",
                "address",
                "branch"
            ),
            id=contact_id,
            branch=branch,
            status="active"
        )

        # =====================================
        # CONTACT ORGANIZATION DEALS
        # =====================================

        contact_deals = Deal_db.objects.filter(
            branch=branch,
            status="active",
            organization=contact.company_name
        ).select_related(
            "organization",
            "deal_owner"
        ).order_by(
            "-created_at"
        )

        context = {
            "branch": branch,
            "contact": contact,
            "contact_deals": contact_deals,
        }

        return render(
            request,
            "contact_detail.html",
            context
        )

    else:
        return redirect("login")


def add_contact_company(request):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        if request.method != "POST":

            return JsonResponse({
                "success": False,
                "message": "Invalid request."
            })


        # =========================
        # ORGANIZATION NAME
        # =========================

        organization_name = request.POST.get(
            "organization_name",
            ""
        ).strip()

        if not organization_name:

            return JsonResponse({
                "success": False,
                "message": "Organization Name is required."
            })


        # =========================
        # WEBSITE
        # =========================

        website = request.POST.get(
            "website",
            ""
        ).strip()


        # =========================
        # ANNUAL REVENUE
        # =========================

        raw_revenue = request.POST.get(
            "annual_revenue",
            "0"
        ).strip()

        annual_revenue = re.sub(
            r"[^\d.]",
            "",
            raw_revenue
        ) or "0"


        # =========================
        # NO. OF EMPLOYEES
        # =========================

        no_of_employees = request.POST.get(
            "no_of_employees"
        ) or None


        # =========================
        # TERRITORY
        # =========================

        territory_id = request.POST.get(
            "territory"
        ) or None

        territory = None

        if territory_id:

            territory = Territory_db.objects.filter(
                id=territory_id,
                branch=branch,
                status="active"
            ).first()


        # =========================
        # INDUSTRY
        # =========================

        industry_id = request.POST.get(
            "industry"
        ) or None

        industry = None

        if industry_id:

            industry = Industry_db.objects.filter(
                id=industry_id,
                branch=branch,
                status="active"
            ).first()


        # =========================
        # ADDRESS
        # =========================

        address_id = request.POST.get(
            "address"
        ) or None

        address = None

        if address_id:

            address = Address_db.objects.filter(
                id=address_id,
                branch=branch,
                status="active"
            ).first()


        # =========================
        # CREATE ORGANIZATION
        # =========================

        organization = Organization_db.objects.create(

            branch=branch,

            organization_name=organization_name,

            website=website or None,

            annual_revenue=annual_revenue,

            no_of_employees=no_of_employees,

            territory=territory,

            industry=industry,

            address=address,

            status="active",
        )


        # =========================
        # RETURN JSON
        # =========================

        return JsonResponse({

            "success": True,

            "id": organization.id,

            "name": organization.organization_name,

            "website": organization.website or "",

            "annual_revenue": str(
                organization.annual_revenue
            ),

            "no_of_employees":
                organization.no_of_employees or "",

            "territory":
                organization.territory.territory_name
                if organization.territory
                else "",

            "industry":
                organization.industry.industry_name
                if organization.industry
                else "",

            "address":
                organization.address.address_title
                if organization.address
                else "",

            "message":
                f"Organization '{organization_name}' created successfully."
        })

    else:
        return redirect("login")


def delete_contact(request, id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        contact = get_object_or_404(
            Contact_db,
            id=id,
            branch=branch,
            status="active"
        )

        contact.status = "inactive"
        contact.save()

        messages.success(
            request,
            "Contact deleted successfully."
        )

        return redirect("contacts")

    else:
        return redirect("login")


def settings(request):
    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']
        branch = Branch_db.objects.filter(id=B_id)

        return render(request, "settings.html", {'branch': branch})
    else:
        return redirect('login')


def users(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']
        branch = Branch_db.objects.get(id=B_id)

        users_list = Users_db.objects.filter(
            branch=branch,
            status="active"
        ).order_by("full_name")

        return render(request, "users.html",
            {
                "users": users_list,
                "branch": branch,
                "role_choices": ROLE_CHOICES
            }
        )

    else:
        return redirect("login")


def add_user(request):

    if 'B_id' in request.session:
        if request.session.has_key('B_id'):
            B_id = request.session['B_id']
        branch = Branch_db.objects.get(id=B_id)

        if request.method == "POST":

            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            username = request.POST.get("username")
            password = request.POST.get("password")
            role = request.POST.get("role", "sales")

            Users_db.objects.create(
                branch=branch,
                full_name=full_name,
                email=email,
                username=username,
                password=password,
                role=role,
                status="active"
            )

            messages.success(request, "User created successfully.")
            return redirect('users')
        return redirect('users')

    else:
        return redirect('login')




@login_required
def preferences(request):
    return render(request, "preferences.html")


@login_required
def general(request):
    return render(request, "general.html")


@login_required
def settings_dashboard(request):
    return render(request, "settings_dashboard.html")


@login_required
def defaults(request):
    return render(request, "defaults.html")


@login_required
def brand(request):
    return render(request, "brand.html")


@login_required
def invite_user(request):
    return render(request, "invite_user.html")


@login_required
def sales_hierarchy(request):

    users_list = Users_db.objects.filter(
        status="active"
    ).order_by("full_name")

    return render(
        request,
        "sales_hierarchy.html",
        {
            "users": users_list
        }
    )


# =========================================
# EMAIL
# =========================================

@login_required
def accounts(request):
    return render(request, "accounts.html")


@login_required
def templates(request):
    return render(request, "templates.html")


@login_required
def new_template(request):
    return render(request, "new_template.html")


# =========================================
# AUTOMATION
# =========================================

@login_required
def assignment_rules(request):
    return render(request, "assignment_rules.html")


@login_required
def sla_policies(request):
    return render(request, "sla_policies.html")


@login_required
def forms(request):
    return render(request, "forms.html")


# =========================================
# CUSTOMIZATION
# =========================================

@login_required
def home_actions(request):
    return render(request, "home_actions.html")


# =========================================
# INTEGRATIONS
# =========================================

@login_required
def telephony(request):
    return render(request, "telephony.html")


@login_required
def erpnext(request):
    return render(request, "erpnext.html")


@login_required
def lead_syncing(request):
    return render(request, "lead_syncing.html")

@login_required
def logout_view(request):

    logout(request)

    return redirect("login")



def add_lead_email(request, lead_id):
    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        lead = get_object_or_404(
            Lead_db,
            id=lead_id,
            branch=branch,
            status="active"
        )

        if request.method == "POST":

            to_email = request.POST.get("to_email")
            subject = request.POST.get("subject")
            content = request.POST.get("content")

            Email_db.objects.create(
                branch=branch,
                lead=lead,
                to_email=to_email,
                subject=subject,
                content=content,
                email_status="sent",
                status="active"
            )

            messages.success(request, "Email added successfully.")
            return redirect("lead_detail", lead_id=lead.id)

        return redirect("lead_detail", lead_id=lead.id)

    else:
        return redirect("login")


def add_lead_comment(request, lead_id):
    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        lead = get_object_or_404(
            Lead_db,
            id=lead_id,
            branch=branch,
            status="active"
        )

        if request.method == "POST":

            comment = request.POST.get("comment")

            Comment_db.objects.create(
                branch=branch,
                lead=lead,
                comment=comment,
                status="active"
            )

            messages.success(request, "Comment added successfully.")
            return redirect("lead_detail", lead_id=lead.id)

        return redirect("lead_detail", lead_id=lead.id)

    else:
        return redirect("login")


def add_lead_task(request, lead_id):
    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        lead = get_object_or_404(
            Lead_db,
            id=lead_id,
            branch=branch,
            status="active"
        )

        if request.method == "POST":

            title = request.POST.get("title")
            description = request.POST.get("description")
            priority = request.POST.get("priority")
            due_date = request.POST.get("due_date")
            assigned_to_id = request.POST.get("assigned_to")

            assigned_to = None

            if assigned_to_id:
                assigned_to = Users_db.objects.filter(
                    id=assigned_to_id,
                    branch=branch,
                    status="active"
                ).first()

            Task_db.objects.create(
                branch=branch,
                lead=lead,
                assigned_to=assigned_to,
                title=title,
                description=description,
                priority=priority,
                due_date=due_date,
                task_status="not_started",
                status="active"
            )

            messages.success(request, "Task added successfully.")
            return redirect("lead_detail", lead_id=lead.id)

        return redirect("lead_detail", lead_id=lead.id)

    else:
        return redirect("login")


def add_lead_note(request, lead_id):
    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        lead = get_object_or_404(
            Lead_db,
            id=lead_id,
            branch=branch,
            status="active"
        )

        if request.method == "POST":

            title = request.POST.get("title")
            content = request.POST.get("content")

            Note_db.objects.create(
                branch=branch,
                lead=lead,
                title=title,
                content=content,
                status="active"
            )

            messages.success(request, "Note added successfully.")
            return redirect("lead_detail", lead_id=lead.id)

        return redirect("lead_detail", lead_id=lead.id)

    else:
        return redirect("login")


def add_lead_attachment(request, lead_id):
    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        lead = get_object_or_404(
            Lead_db,
            id=lead_id,
            branch=branch,
            status="active"
        )

        if request.method == "POST":

            uploaded_file = request.FILES.get("file")

            if not uploaded_file:
                messages.error(request, "Please select a file.")
                return redirect("lead_detail", lead_id=lead.id)

            Attachment_db.objects.create(
                branch=branch,
                lead=lead,
                file=uploaded_file,
                file_name=uploaded_file.name,
                status="active"
            )

            messages.success(request, "Attachment uploaded successfully.")
            return redirect("lead_detail", lead_id=lead.id)

        return redirect("lead_detail", lead_id=lead.id)

    else:
        return redirect("login")


def add_lead_call(request, lead_id):
    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        lead = get_object_or_404(
            Lead_db,
            id=lead_id,
            branch=branch,
            status="active"
        )

        if request.method == "POST":

            call_type = request.POST.get("call_type")
            to_number = request.POST.get("to_number")
            from_number = request.POST.get("from_number")
            call_status = request.POST.get("call_status")
            duration = request.POST.get("duration")

            caller_id = request.POST.get("caller")
            received_by_id = request.POST.get("call_received_by")

            caller = None
            call_received_by = None

            if caller_id:
                caller = Users_db.objects.filter(
                    id=caller_id,
                    branch=branch,
                    status="active"
                ).first()

            if received_by_id:
                call_received_by = Users_db.objects.filter(
                    id=received_by_id,
                    branch=branch,
                    status="active"
                ).first()

            CallLog_db.objects.create(
                branch=branch,
                lead=lead,
                caller=caller,
                call_received_by=call_received_by,
                call_type=call_type,
                to_number=to_number,
                from_number=from_number,
                call_status=call_status,
                duration=duration,
                status="active"
            )

            messages.success(request, "Call logged successfully.")
            return redirect("lead_detail", lead_id=lead.id)

        return redirect("lead_detail", lead_id=lead.id)

    else:
        return redirect("login")


def convert_lead_to_deal(request, lead_id):

    if 'B_id' in request.session:

        if request.session.has_key('B_id'):
            B_id = request.session['B_id']

        branch = Branch_db.objects.get(id=B_id)

        # ================================
        # GET LEAD
        # ================================

        if request.session['user_type'] == 'branch':

            lead = get_object_or_404(
                Lead_db,
                id=lead_id,
                branch=branch,
                status="active"
            )

        else:

            U_id = request.session['U_id']

            lead = get_object_or_404(
                Lead_db,
                id=lead_id,
                branch=branch,
                lead_owner_id=U_id,
                status="active"
            )


        # ================================
        # CREATE DEAL
        # ================================

        deal = Deal_db.objects.create(

            branch=branch,

            organization=lead.organization,

            lead=lead,

            industry=lead.industry,

            territory=lead.territory,

            deal_owner=lead.lead_owner,

            website=lead.website,

            no_of_employees=lead.no_of_employees,

            annual_revenue=lead.annual_revenue,

            salutation=lead.salutation,

            first_name=lead.first_name,

            last_name=lead.last_name,

            primary_email=lead.email,

            primary_mobile_no=lead.mobile_no,

            gender=lead.gender,

            deal_status="qualification",

            probability=0,

            status="active"
        )


        # ================================
        # UPDATE LEAD
        # ================================

        lead.lead_status = "converted"
        lead.status = "inactive"
        lead.save()


        messages.success(
            request,
            "Lead converted to deal successfully."
        )


        return redirect(
            "deal_detail",
            deal_id=deal.id
        )

    else:
        return redirect("login")
