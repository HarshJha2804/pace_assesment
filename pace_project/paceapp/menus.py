MENUS = {
    'NAV_MENU_LEFT': [
        {
            "name": "Masters",
            "icon_class": 'ti-layout-dashboard',
            "url": "#",
            "validators": ['menu_generator.validators.is_superuser'],
            "submenu": [
                {
                    "name": "Role",
                    "url": "users:role_list"
                },
                {
                    "name": "User",
                    "url": "users:user_list"
                },
                {
                    "name": "Team Requirement",
                    "url": "core:staffing_requirement_list"
                },
                {
                    "name": "Year",
                    "url": "paceapp:year_list"
                },
                {
                    "name": "Intake",
                    "url": "paceapp:intake_list"
                },
                {
                    "name": "Country",
                    "url": "paceapp:country_list"
                },
                {
                    "name": "Regions",
                    "url": "paceapp:region_list"
                },
                {
                    "name": "State",
                    "url": "paceapp:state_list"
                },
                {
                    "name": "University Intake",
                    "url": "paceapp:university_intake_list"
                },
                {
                    "name": "University Targets",
                    "url": "core:university_target_list"
                },
                {
                    "name": "Board",
                    "url": "paceapp:board_list"
                },
                {
                    "name": "Campus",
                    "url": "paceapp:campus_list"
                },
                {
                    "name": "Stream",
                    "url": "paceapp:stream_list"
                },
                {
                    "name": "Sub-Stream",
                    "url": "paceapp:sub_stream_list"
                },
                {
                    "name": "Level",
                    "url": "paceapp:level_list"
                },

                {
                    "name": "Country Specific Level",
                    "url": "core:country_specific_level_list"

                },

                {
                    "name": "Document Templates",
                    "url": "core:document_template_list"
                },

                {
                    "name": "Country Specific Document",
                    "url": "core:country_specific_document_list"
                },

                {
                    "name": "Partner Document Support",
                    "url": "core:partner_support_document_list"
                },
                {
                    "name": "Commission Structure",
                    "url": "core:commission_structure_list"
                },
                {
                    "name": "Conditions",
                    "url": "core:condition_list"

                },
            ],
        },
        {
            "name": "Status & Fields",
            "icon_class": "ti ti-database-search",
            "url": "#",
            "validators": ['menu_generator.validators.is_superuser'],
            "submenu": [
                {
                    "name": "Status Types",
                    "url": "core:status_type_list"
                },

                {
                    "name": "Country Specific Status",
                    "url": "core:country_specific_status_list"
                },
                {
                    "name": "University Specific Interview Status",
                    "url": "core:university_interview_status_list"
                },
                {
                    "name": "Dynamic Field",
                    "url": "core:dynamic_field_list"
                },

                {
                    "name": "Country Specific Dynamic Field",
                    "url": "core:country_specific_field_list"
                },

                {
                    "name": "Interview Status Types",
                    "url": "core:interview_status_type_list"
                },
            ]
        },
        {
            "name": "Teams",
            "icon_class": "ti ti-users",
            "url": "#",
            "validators": ['menu_generator.validators.is_superuser'],
            "submenu": [
                {
                    "name": "Team Members",
                    "url": "users:employee_list"
                },
                {
                    "name": "Regional Marketing Heads",
                    "url": "users:rm_list",
                },
                {
                    "name": "Application Managers",
                    "url": "users:application_manager_list",
                },
                {
                    "name": "Regional Marketing Head Targets",
                    "url": "core:rm_target_list"
                },
            ]
        },
        {
            "name": "Projects",
            "icon_class": 'ti ti-building',
            "url": "paceapp:university_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        {
            "name": "Courses",
            "icon_class": 'ti ti-picture-in-picture',
            "url": "paceapp:course_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        {
            "name": "Partners",
            "icon_class": 'ti ti-heart-handshake',
            "url": "#",
            "validators": ['menu_generator.validators.is_superuser'],
            "submenu": [
                {
                    "name": "Partners List",
                    "icon_class": '#',
                    "url": "paceapp:partner_list",
                    "validators": [
                        "paceapp.validators.is_superuser_or_has_permission"
                    ],
                },
                {
                    "name": "Onboarding Requests",
                    "icon_class": '#',
                    "url": "paceapp:onboarded_partner",
                    "validators": ['menu_generator.validators.is_superuser'],
                },
                {
                    "name": "Partners Commission",
                    "icon_class": '#',
                    "url": "partner:partner_commission_list",
                    "validators": [
                        "paceapp.validators.is_superuser_or_has_permission"
                    ],
                },
            ]
        },

        # Assessment Officer

        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:assessment_dashboard",
            "validators": ["paceapp.validators.has_assessment_permission"],
        },
        {
            "name": "Manage Assessment",
            "icon_class": 'ti ti-school',
            "url": "paceapp:asf_student_list",
            "validators": ["paceapp.validators.has_assessment_permission"],
        },
        # Vice President

        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:dashboard_vice_president",
            "validators": ["paceapp.validators.has_vice_president"],
        },
        {
            "name": "Partners",
            "icon_class": 'ti ti-heart-handshake',
            "url": "paceapp:partner_list",
            "validators": ["paceapp.validators.has_vice_president"],
        },
        {
            "name": "Students",
            "icon_class": 'ti ti-school',
            "url": "paceapp:student_list",
            "validators": ["paceapp.validators.has_vice_president"],
        },
        {
            "name": "Applications",
            "icon_class": 'ti ti-files',
            "url": "core:application_list",
            "validators": ["paceapp.validators.has_vice_president"],
        },

        # Application Manager

        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:dashboard_application_manager",
            "validators": ["paceapp.validators.has_application_manager_permission_dashboard"],
        },
        {
            "name": "Students",
            "icon_class": 'ti ti-school',
            "url": "paceapp:am_student_list",
            "validators": ["paceapp.validators.has_application_permission_is_head"],
        },
        {
            "name": "Applications",
            "icon_class": 'ti ti-files',
            "url": "paceapp:application_manager_application_list",
            "validators": ["paceapp.validators.is_application_manager"],
        },
        {
            "name": "Students",
            "icon_class": 'ti ti-school',
            "url": "paceapp:student_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        {
            "name": "Applications",
            "icon_class": 'ti ti-files',
            "url": "core:application_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        {
            "name": "Important Updates",
            "icon_class": 'ti ti-bell-z',
            "url": "core:news_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },

        {
            "name": "Meeting",
            "icon_class": 'ti ti-calendar-stats',
            "url": "meetcom:meeting_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        {
            "name": "Webinar",
            "icon_class": 'ti ti-bell-z',
            "url": "meetcom:webinar_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        {
            "name": "Daily Progress Reports",
            "icon_class": 'ti ti-chart-infographic',
            "url": "paceapp:daily_report_list",
            "validators": ['menu_generator.validators.is_superuser'],
        },
        # Regional Officer Dashboard
        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:dashboard_regional_marketing_head",
            "validators": ["paceapp.validators.has_regional_permission"],
        },
        {
            "name": "Targets",
            "icon_class": 'ti ti-target-arrow',
            "url": "paceapp:target_list",
            "validators": ["paceapp.validators.has_regional_permission"],
        },
        {
            "name": "Premium Partners",
            "icon_class": 'ti ti-heart-handshake',
            "url": "paceapp:premium_partner_list",
            "validators": ["paceapp.validators.has_regional_permission"],
        },
        {
            "name": "Followup Offer To Deposits",
            "icon_class": 'ti ti-pointer-dollar',
            "url": "paceapp:regional_application_list",
            "validators": ["paceapp.validators.has_regional_permission"],
        },
        {
            "name": "New Partner On Boarding",
            "icon_class": 'ti ti-brand-asana',
            "url": "paceapp:onboarded_partner",
            "validators": ["paceapp.validators.has_regional_permission"],
        },
        {
            "name": "Meetings",
            "icon_class": 'ti ti-calendar-stats',
            "url": "meetcom:rm_meeting_list",
            "validators": ["paceapp.validators.has_regional_permission"],
        },
        {
            "name": "Daily Progress Reports",
            "icon_class": 'ti ti-chart-infographic',
            "url": "paceapp:daily_report_list",
            "validators": ["paceapp.validators.has_regional_permission"],
        },

        # Interview officer

        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "#",
            "validators": ["paceapp.validators.has_interview_permission"],
        },
        {
            "name": "Manage Applications",
            "icon_class": 'ti ti-files',
            "url": "core:interview_application_list",
            "validators": ["paceapp.validators.has_interview_permission"],
        },

        # Compliance Officer

        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:dashboard_compliance_officer",
            "validators": ["paceapp.validators.has_compliance_officer_permission"],
        },

        {
            "name": "Students",
            "icon_class": 'ti ti-files',
            "url": "paceapp:student_list",
            "validators": ["paceapp.validators.has_compliance_officer_permission"],
        },
        {
            "name": "Applications",
            "icon_class": 'ti ti-files',
            "url": "paceapp:compliance_application_list",
            "validators": ["paceapp.validators.has_compliance_officer_permission"],
        },

        # partner onboarding officer

        {
            "name": "Partner",
            "icon_class": '',
            "url": "paceapp:partner_list",
            "validators": ["paceapp.validators.has_onboarding_officer"],
        },
        {
            "name": "Onboarding Request",
            "icon_class": '',
            "url": "paceapp:onboarded_partner",
            "validators": ["paceapp.validators.has_onboarding_officer"],
        },

        # partner dashboard

        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "partner:dashboard_partner",
            "validators": ["paceapp.validators.has_partner"],
        },
        {
            "name": "Upload Signed Agreement",
            "icon_class": 'ti ti-contract',
            "url": "partner:upload_docs",
            "validators": ["paceapp.validators.has_partner_upload_agreements"],
        },
        {
            "name": "Important Updates",
            "icon_class": 'ti ti-bell-z',
            "url": "core:news_list",
            "validators": ["paceapp.validators.has_partner"],
        },

        {
            "name": "Students",
            "icon_class": 'ti ti-school',
            "url": "partner:list_student",
            "validators": ["paceapp.validators.has_partner"],
        },
        {
            "name": "Applications",
            "icon_class": 'ti ti-files',
            "url": "partner:application_list",
            "validators": ["paceapp.validators.has_partner"],
        },
        {
            "name": "Universities",
            "icon_class": 'ti ti-building',
            "url": "partner:university_list",
            "validators": ["paceapp.validators.has_partner"],
        },

        # {
        #     "name": "Requested Assessment",
        #     "icon_class": '',
        #     "url": "partner:partner_requested_assessment",
        #     "validators": ["paceapp.validators.has_partner"],
        # },
        # partner account manager:
        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:data_management_officer",
            "validators": ['paceapp.validators.has_partner_account_permission'],
        },
        {
            "name": "Students",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "partner:account_manager_students_list",
            "validators": ['paceapp.validators.has_partner_account_permission'],
        },
        {
            "name": "Partners",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "partner:account_manager_partners_list",
            "validators": ['paceapp.validators.has_partner_account_permission'],
        },
        {
            "name": "Applications",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "partner:account_manager_applications_list",
            "validators": ['paceapp.validators.has_partner_account_permission'],
        },
        {
            "name": "Contact us",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "core:contact_us_list",
            "validators": ['paceapp.validators.has_partner_account_permission'],
        },

        # Data management officer
        {
            "name": "Dashboard",
            "icon_class": 'ti ti-layout-dashboard',
            "url": "paceapp:data_management_officer",
            "validators": ['paceapp.validators.has_data_management_officer'],
        },
        {

            "name": "Masters",
            "icon_class": '',
            "url": "#",
            "validators": ['paceapp.validators.has_data_management_officer'],
            "submenu": [
                {
                    "name": "Year",
                    "url": "paceapp:year_list"
                },
                {
                    "name": "Intake",
                    "url": "paceapp:intake_list"
                },
                {
                    "name": "Country",
                    "url": "paceapp:country_list"
                },
                {
                    "name": "Regions",
                    "url": "paceapp:region_list"
                },
                {
                    "name": "State",
                    "url": "paceapp:state_list"
                },
                {
                    "name": "Status Types",
                    "url": "core:status_type_list"
                },
                {
                    "name": "Country Specific Status",
                    "url": "core:country_specific_status_list"
                },
                {
                    "name": "University Intake",
                    "url": "paceapp:university_intake_list"
                },
                {
                    "name": "University Targets",
                    "url": "core:university_target_list"
                },
                {
                    "name": "Board",
                    "url": "paceapp:board_list"
                },
                {
                    "name": "Campus",
                    "url": "paceapp:campus_list"
                },
                {
                    "name": "Stream",
                    "url": "paceapp:stream_list"
                },
                {
                    "name": "Sub-Stream",
                    "url": "paceapp:sub_stream_list"
                },
                {
                    "name": "Level",
                    "url": "paceapp:level_list"
                },

                {
                    "name": "Country Specific Level",
                    "url": "core:country_specific_level_list"

                },

                {
                    "name": "Document Templates",
                    "url": "core:document_template_list"
                },

                {
                    "name": "Country Specific Document",
                    "url": "core:country_specific_document_list"
                },

                {
                    "name": "Partner Document Support",
                    "url": "core:partner_support_document_list"
                },
            ],
        },
        {
            "name": "Projects",
            "icon_class": 'ti ti-building',
            "url": "paceapp:university_list",
            "validators": ['paceapp.validators.has_data_management_officer'],
        },
        {
            "name": "Courses",
            "icon_class": 'ti ti-picture-in-picture',
            "url": "paceapp:course_list",
            "validators": ['paceapp.validators.has_data_management_officer'],
        },
        {
            "name": "Partners",
            "icon_class": 'ti ti-heart-handshake',
            "url": "paceapp:partner_list",
            "validators": [
                "paceapp.validators.has_data_management_officer"
            ],
        },

    ],
    'NAV_MENU_RIGHT': [
        {
            "name": "Download Agreement",
            "icon_class": '',
            "url": "partner:docs",
            "validators": ["paceapp.validators.has_partner_download_agreements"],
        },

        {
            "name": "Commission Structure",
            "icon_class": '',
            "url": "partner:partner_commission_list",
            "validators": ["paceapp.validators.has_partner"],
        },
        {
            "name": "Change Password",
            "url": "account_change_password",
            "validators": ['menu_generator.validators.is_authenticated']
        },
        {
            "name": "Two Factor Authentication",
            "url": "mfa_index",
            "validators": ['paceapp.validators.has_mfa_auth']
        },
    ]
}
