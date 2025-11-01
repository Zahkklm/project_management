class MockEmailService:
    def send_invite_email(self, to_email: str, join_link: str):
        print(f"Mock email sent to {to_email} with link: {join_link}")
        return True
