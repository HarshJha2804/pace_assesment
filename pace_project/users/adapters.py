from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from config.settings.base import env
from pace_project.paceapp.enums import RoleEnum

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from pace_project.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def format_email_subject(self, subject):
        return subject

    def render_confirmation_mail(self, template_prefix, email, context, headers=None):
        to = [email] if isinstance(email, str) else email

        is_signup = template_prefix == 'account/email/signup'
        is_confirmation = template_prefix == 'account/email/email_confirmation'

        # Retrieve user from context
        user = context.get('user')
        user_role = getattr(user, 'role', '') if user else ''

        if user_role.name == RoleEnum.PARTNER.value and (is_signup or is_confirmation):

            subject = render_to_string("{0}_subject.txt".format(template_prefix), context)
            # remove superfluous line breaks
            subject = " ".join(subject.splitlines()).strip()
            subject = self.format_email_subject(subject)

            from_email = self.get_from_email()

            # Use AnymailMessage with SendGrid dynamic template
            template_id = env("CONFIRMATION_MAIL_TEMPLATE_ID")
            msg = EmailMessage(
                subject,
                from_email=from_email,
                to=to,
                headers=headers
            )
            msg.subject = subject
            msg.template_id = template_id
            msg.merge_global_data = {
                "user": str(context["user"]),
                "activate_url": context["activate_url"],
                "site_name": context["current_site"].name,
                "site_domain": context["current_site"].domain,
            }
            return msg
        else:
            return self.render_mail(template_prefix, email, context, headers)

    def send_mail(self, template_prefix, email, context):
        current_site = get_current_site(self.request)
        ctx = {
            "email": email,
            "current_site": current_site,
        }
        ctx.update(context)
        msg = self.render_confirmation_mail(template_prefix, email, ctx)
        msg.send()


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
