class MockEmailService:
    def send_invite_email(
        self,
        recipient_email: str,
        project_name: str,
        inviter_name: str,
        join_link: str,
    ):
        print(f"Mock email: {inviter_name} invited you to {project_name}")
        print(f"Sent to: {recipient_email}")
        print(f"Join link: {join_link}")
        return True
