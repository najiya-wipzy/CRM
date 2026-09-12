from django.urls import path
from . import views


urlpatterns = [

    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    path("dashboard/", views.dashboard, name="dashboard"),
    path("users/", views.users, name="users"),
    path("add-user/", views.add_user, name="add_user"),
    path("invite-user/", views.invite_user, name="invite_user"),

    path('leads/', views.leads, name='leads'),
    path('add-lead/', views.add_lead, name='add_lead'),
    path('leads/<int:lead_id>/', views.lead_detail, name='lead_detail'),
    path('leads/<int:lead_id>/delete/', views.delete_lead, name='delete_lead'),

    path("add-lead-organization/", views.add_lead_organization, name="add_lead_organization"),



    path(
        "organizations/",
        views.organizations,
        name="organizations"
    ),

    path(
        "organizations/add/",
        views.add_organization_full,
        name="add_organization"
    ),
    path(
        "organizations/add-full/",
        views.add_organization_full,
        name="add_organization_full"
    ),

    path(
    "organizations/<int:organization_id>/",
    views.organization_detail,
    name="organization_detail"
    ),

    path(
    'organization/delete/<int:id>/',
    views.delete_organization,
    name='delete_organization'
    ),

    path("add-address/", views.add_address, name="add_address"),

    path(
        "leads/industry/add/",
        views.add_industry,
        name="add_industry"
    ),

    path(
        "leads/territory/add/",
        views.add_territory,
        name="add_territory"
    ),


path(
    "lead/<int:lead_id>/",
    views.lead_detail,
    name="lead_detail"
),

path(
    "lead/<int:lead_id>/comment/add/",
    views.add_lead_comment,
    name="add_lead_comment"
),

path(
    "lead/<int:lead_id>/email/add/",
    views.add_lead_email,
    name="add_lead_email"
),

path(
    "lead/<int:lead_id>/call/add/",
    views.add_lead_call,
    name="add_lead_call"
),

path(
    "lead/<int:lead_id>/task/add/",
    views.add_lead_task,
    name="add_lead_task"
),

path(
    "lead/<int:lead_id>/note/add/",
    views.add_lead_note,
    name="add_lead_note"
),

path(
    "lead/<int:lead_id>/attachment/add/",
    views.add_lead_attachment,
    name="add_lead_attachment"
),

path(
    "lead/<int:lead_id>/convert/",
    views.convert_lead_to_deal,
    name="convert_lead_to_deal"
),


    # Deals
    path(
        "deals/",
        views.deals,
        name="deals"
    ),

    path(
        "deals/add/",
        views.add_deal,
        name="add_deal"
    ),

    path(
        "deals/<int:deal_id>/",
        views.deal_detail,
        name="deal_detail"
    ),
    path("deal/<int:id>/delete/", views.delete_deal, name="delete_deal"),

    # Contacts
    path("contacts/", views.contacts, name="contacts"),
    path(
    "contacts/<int:contact_id>/",
    views.contact_detail,
    name="contact_detail"
    ),

    path(
    "contacts/add/",
    views.add_contact,
    name="add_contact"
    ),

    path(
    "contacts/company/add/",
    views.add_contact_company,
    name="add_contact_company"
    ),

    path("contact/<int:id>/delete/", views.delete_contact, name="delete_contact"),

    # path(
    # "addresses/add/",
    # views.add_address,
    # name="add_address"
    # ),

    # Organizations


    # Tasks

    path("tasks/", views.tasks, name="tasks"),
    path("tasks/add/", views.add_task, name="add_task"),
    path(
    "task/<int:id>/delete/",
    views.delete_task,
    name="delete_task"
    ),


    # Notes
    path(
        "notes/",
        views.notes,
        name="notes"
    ),
    path(
    "notes/<int:note_id>/",
    views.note_detail,
    name="note_detail"
    ),

    path("notes/add/", views.add_note, name="add_note"),

    path(
    "note/<int:id>/delete/",
    views.delete_note,
    name="delete_note"
    ),

    path("calls/", views.calls, name="calls"),

    path("calls/add/", views.add_call, name="add_call"),
    path("calls/<int:call_id>/", views.call_detail, name="call_detail"),
    path(
    "call/<int:id>/delete/",
    views.delete_call,
    name="delete_call"
    ),


    # Settings
    path(
        "settings/",
        views.settings,
        name="settings"
    ),

    path(
        "settings/preferences/",
        views.preferences,
        name="preferences"
    ),

    path(
        "settings/general/",
        views.general,
        name="general"
    ),

    path(
        "settings/dashboard/",
        views.settings_dashboard,
        name="settings_dashboard"
    ),

    path(
        "settings/defaults/",
        views.defaults,
        name="defaults"
    ),

    path(
        "settings/brand/",
        views.brand,
        name="brand"
    ),


    # Users
    path(
        "users/",
        views.users,
        name="users"
    ),

    path(
        "invite-user/",
        views.invite_user,
        name="invite_user"
    ),

    path(
        "sales-hierarchy/",
        views.sales_hierarchy,
        name="sales_hierarchy"
    ),


    # Email
    path(
        "accounts/",
        views.accounts,
        name="accounts"
    ),

    path(
        "templates/",
        views.templates,
        name="templates"
    ),

    path(
        "new-template/",
        views.new_template,
        name="new_template"
    ),


    # Automation
    path(
        "assignment-rules/",
        views.assignment_rules,
        name="assignment_rules"
    ),

    path(
        "sla-policies/",
        views.sla_policies,
        name="sla_policies"
    ),

    path(
        "forms/",
        views.forms,
        name="forms"
    ),


    # Customization
    path(
        "home-actions/",
        views.home_actions,
        name="home_actions"
    ),


    # Integrations
    path(
        "telephony/",
        views.telephony,
        name="telephony"
    ),

    path(
        "erpnext/",
        views.erpnext,
        name="erpnext"
    ),

    path(
        "lead-syncing/",
        views.lead_syncing,
        name="lead_syncing"
    ),

]