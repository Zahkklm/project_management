"""
AWS SES Email Service for sending project invitation emails.
"""

# flake8: noqa: E501

import logging
from typing import Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class SESEmailService:
    """Service for sending emails via AWS SES."""

    def __init__(
        self,
        sender_email: str,
        aws_region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        """
        Initialize SES email service.

        Args:
            sender_email: Verified sender email address in SES
            aws_region: AWS region for SES
            aws_access_key_id: AWS access key (optional if using IAM role)
            aws_secret_access_key: AWS secret key (optional if using IAM role)
        """
        self.sender_email = sender_email
        self.aws_region = aws_region

        # Initialize SES client
        client_kwargs = {"region_name": aws_region}
        if aws_access_key_id and aws_secret_access_key:
            client_kwargs["aws_access_key_id"] = aws_access_key_id
            client_kwargs["aws_secret_access_key"] = aws_secret_access_key

        self.ses_client = boto3.client("ses", **client_kwargs)

    def send_invite_email(
        self, to_email: str, join_link: str, project_name: str = "Project"
    ) -> bool:
        """
        Send project invitation email via AWS SES.

        Args:
            to_email: Recipient email address
            join_link: URL link to join the project
            project_name: Name of the project being shared

        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"You've been invited to join {project_name}"

        # HTML email body
        html_body = self._generate_html_email(
            to_email, join_link, project_name
        )

        # Plain text email body (fallback)
        text_body = f"""
You've been invited to join {project_name}!

Click the link below to accept the invitation:
{join_link}

This invitation link will expire in 7 days.

If you didn't expect this invitation, you can safely ignore this email.
        """.strip()

        try:
            response = self.ses_client.send_email(
                Source=self.sender_email,
                Destination={"ToAddresses": [to_email]},
                Message={
                    "Subject": {"Data": subject, "Charset": "UTF-8"},
                    "Body": {
                        "Text": {"Data": text_body, "Charset": "UTF-8"},
                        "Html": {"Data": html_body, "Charset": "UTF-8"},
                    },
                },
            )
            logger.info(
                f"Email sent successfully to {to_email}. "
                f"Message ID: {response['MessageId']}"
            )
            return True

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            logger.error(
                f"Failed to send email to {to_email}. "
                f"Error: {error_code} - {error_message}"
            )
            return False

        except Exception as e:
            logger.error(
                f"Unexpected error sending email to {to_email}: {e}"
            )
            return False

    def _generate_html_email(
        self, to_email: str, join_link: str, project_name: str
    ) -> str:
        """
        Generate HTML email template for project invitation.

        Args:
            to_email: Recipient email
            join_link: Join URL
            project_name: Project name

        Returns:
            HTML string for email body
        """
        return f"""  <!-- noqa -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Project Invitation</title>
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">  <!-- noqa -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4; padding: 20px;">  <!-- noqa -->
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">  <!-- noqa -->
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #4F46E5; color: #ffffff; padding: 30px; text-align: center; border-radius: 8px 8px 0 0;">  <!-- noqa -->
                            <h1 style="margin: 0; font-size: 28px;">Project Invitation</h1>
                        </td>
                    </tr>

                    <!-- Body -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">  <!-- noqa -->
                                Hello,
                            </p>
                            <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 20px 0;">  <!-- noqa -->
                                You've been invited to collaborate on <strong>{project_name}</strong>.  <!-- noqa -->
                            </p>
                            <p style="font-size: 16px; color: #333333; line-height: 1.6; margin: 0 0 30px 0;">  <!-- noqa -->
                                Click the button below to accept the invitation and get started:  <!-- noqa -->
                            </p>

                            <!-- CTA Button -->
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td align="center">
                                        <a href="{join_link}" style="display: inline-block; background-color: #4F46E5; color: #ffffff; text-decoration: none; padding: 15px 40px; border-radius: 5px; font-size: 16px; font-weight: bold;">  <!-- noqa -->
                                            Accept Invitation
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="font-size: 14px; color: #666666; line-height: 1.6; margin: 30px 0 0 0;">  <!-- noqa -->
                                Or copy and paste this link into your browser:
                            </p>
                            <p style="font-size: 14px; color: #4F46E5; line-height: 1.6; margin: 10px 0 0 0; word-break: break-all;">  <!-- noqa -->
                                {join_link}
                            </p>
                        </td>
                    </tr>

                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f9fafb; padding: 20px 30px; border-radius: 0 0 8px 8px;">  <!-- noqa -->
                            <p style="font-size: 12px; color: #666666; line-height: 1.6; margin: 0;">  <!-- noqa -->
                                This invitation will expire in 7 days. If you didn't expect this invitation, you can safely ignore this email.  <!-- noqa -->
                            </p>
                            <p style="font-size: 12px; color: #666666; line-height: 1.6; margin: 10px 0 0 0;">  <!-- noqa -->
                                &copy; 2025 Project Management Platform. All rights reserved.
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
        """.strip()

    def verify_email_address(self, email: str) -> bool:
        """
        Verify an email address in AWS SES (for development/testing).

        Args:
            email: Email address to verify

        Returns:
            True if verification initiated successfully
        """
        try:
            self.ses_client.verify_email_identity(EmailAddress=email)
            logger.info(
                f"Verification email sent to {email}. "
                "Check inbox to complete verification."
            )
            return True
        except ClientError as e:
            logger.error(f"Failed to verify email {email}: {e}")
            return False
