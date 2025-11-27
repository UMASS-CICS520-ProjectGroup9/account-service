from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.backends import TokenBackend

from base.models import Account


class AccountApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.token_backend = TokenBackend(algorithm="HS256", signing_key="Umass-CSCI520-FinalProject-Group9")

    def auth_headers(self, role="STUDENT", user_id=1, email="user@example.com", username="user"):
        payload = {"user_id": user_id, "email": email, "username": username, "role": role}
        token = self.token_backend.encode(payload)
        return {"HTTP_AUTHORIZATION": f"bearer {token}"}

    # def test_requires_authentication(self):
    #     response = self.client.get("/api/account/")
    #     self.assertEqual(response.status_code, 401)

    def test_admin_can_list_accounts(self):
        Account.objects.create(email="alice@example.com", fullname="Alice", role="ADMIN", creator_id=1)
        Account.objects.create(email="bob@example.com", fullname="Bob", role="STUDENT", creator_id=2)

        response = self.client.get("/api/account/", **self.auth_headers(role="ADMIN", email="admin@example.com", user_id=99))
        self.assertEqual(response.status_code, 200)
        emails = {acct["email"] for acct in response.json()}
        self.assertSetEqual(emails, {"alice@example.com", "bob@example.com"})

    def test_student_create_sets_email_role_and_creator_from_token(self):
        body = {"email": "ignored@example.com", "fullname": "Created User", "role": "ADMIN"}

        response = self.client.post(
            "/api/account/create/", body, format="json", **self.auth_headers(role="STUDENT", email="student@example.com", user_id=111)
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertEqual(payload["email"], "student@example.com")
        self.assertEqual(payload["role"], "STUDENT")
        self.assertEqual(payload["creator_id"], 111)
        self.assertTrue(Account.objects.filter(email="student@example.com").exists())

    def test_owner_can_update_account(self):
        account = Account.objects.create(email="owner@example.com", fullname="Owner Name", role="STUDENT", creator_id=55)
        headers = self.auth_headers(role="STUDENT", user_id=55, email="owner@example.com", username="owner")

        response = self.client.put(
            "/api/account/update/",
            {"email": account.email, "fullname": "Updated Name"},
            format="json",
            **headers,
        )

        self.assertEqual(response.status_code, 200)
        account.refresh_from_db()
        self.assertEqual(account.fullname, "Updated Name")

    def test_student_cannot_update_another_users_account(self):
        account = Account.objects.create(email="other@example.com", fullname="Other Name", role="STUDENT", creator_id=222)

        response = self.client.put(
            "/api/account/update/",
            {"email": account.email, "fullname": "Attempted Change"},
            format="json",
            **self.auth_headers(role="STUDENT", user_id=111, email="student@example.com"),
        )

        self.assertEqual(response.status_code, 404)
        account.refresh_from_db()
        self.assertEqual(account.fullname, "Other Name")

    def test_admin_can_delete_any_account(self):
        account = Account.objects.create(email="delete-me@example.com", fullname="Delete Me", role="STUDENT", creator_id=333)

        response = self.client.delete(
            "/api/account/delete/",
            {"email": account.email},
            format="json",
            **self.auth_headers(role="ADMIN", email="admin@example.com", user_id=1),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Account.objects.filter(email=account.email).exists())

    def test_counts_and_filters(self):
        Account.objects.create(email="one@example.com", fullname="One", role="STUDENT", creator_id=1)
        Account.objects.create(email="two@example.com", fullname="Two", role="ADMIN", creator_id=1)
        Account.objects.create(email="three@example.com", fullname="Three", role="ADMIN", creator_id=1)

        count_response = self.client.get("/api/account/count/", **self.auth_headers(role="ADMIN", email="admin@example.com"))
        self.assertEqual(count_response.status_code, 200)
        self.assertEqual(count_response.json()["count"], 3)

        role_response = self.client.get("/api/account/role/ADMIN/", **self.auth_headers(role="ADMIN", email="admin@example.com"))
        self.assertEqual(role_response.status_code, 200)
        self.assertEqual(len(role_response.json()), 2)

    def test_date_filters(self):
        two_days_ago = timezone.now() - timedelta(days=2)
        yesterday = timezone.now() - timedelta(days=1)
        old_account = Account.objects.create(email="old@example.com", fullname="Old", role="ADMIN", creator_id=1)
        recent_account = Account.objects.create(email="recent@example.com", fullname="Recent", role="ADMIN", creator_id=1)
        Account.objects.filter(pk=old_account.pk).update(created_at=two_days_ago, updated_at=two_days_ago)
        Account.objects.filter(pk=recent_account.pk).update(created_at=timezone.now(), updated_at=timezone.now())

        created_after = self.client.get(
            f"/api/account/created_after/{yesterday.isoformat()}/",
            **self.auth_headers(role="ADMIN", email="admin@example.com"),
        )
        self.assertEqual(created_after.status_code, 200)
        self.assertEqual({acct["email"] for acct in created_after.json()}, {"recent@example.com"})

        updated_before = self.client.get(
            f"/api/account/updated_before/{yesterday.isoformat()}/",
            **self.auth_headers(role="ADMIN", email="admin@example.com"),
        )
        self.assertEqual(updated_before.status_code, 200)
        self.assertEqual({acct["email"] for acct in updated_before.json()}, {"old@example.com"})

    def test_activate_and_deactivate(self):
        account = Account.objects.create(email="toggle@example.com", fullname="Toggle", role="ADMIN", creator_id=1, is_active=False)

        activate = self.client.put(
            "/api/account/activate/",
            {"email": account.email},
            format="json",
            **self.auth_headers(role="ADMIN", email="admin@example.com"),
        )
        self.assertEqual(activate.status_code, 200)
        account.refresh_from_db()
        self.assertTrue(account.is_active)

        deactivate = self.client.put(
            "/api/account/deactivate/",
            {"email": account.email},
            format="json",
            **self.auth_headers(role="ADMIN", email="admin@example.com"),
        )
        self.assertEqual(deactivate.status_code, 200)
        account.refresh_from_db()
        self.assertFalse(account.is_active)

    def test_active_and_inactive_lists(self):
        Account.objects.create(email="active@example.com", fullname="Active", role="ADMIN", creator_id=1, is_active=True)
        Account.objects.create(email="inactive@example.com", fullname="Inactive", role="ADMIN", creator_id=1, is_active=False)

        active_resp = self.client.get("/api/account/active/", **self.auth_headers(role="ADMIN", email="admin@example.com"))
        inactive_resp = self.client.get("/api/account/inactive/", **self.auth_headers(role="ADMIN", email="admin@example.com"))

        self.assertEqual(active_resp.status_code, 200)
        self.assertEqual(inactive_resp.status_code, 200)
        self.assertEqual({acct["email"] for acct in active_resp.json()}, {"active@example.com"})
        self.assertEqual({acct["email"] for acct in inactive_resp.json()}, {"inactive@example.com"})

    def test_get_account_not_found(self):
        resp = self.client.get("/api/account/get/missing@example.com/", **self.auth_headers(role="STUDENT", email="student@example.com"))
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["error"], "Account not found")

    # def test_health_and_welcome_public(self): pass
        # health = self.client.get("/api/health/")
        # welcome = self.client.get("/api/welcome/")
        # overview = self.client.get("/api/")

        # # self.assertEqual(health.status_code, 200)
        # self.assertEqual(welcome.status_code, 200)
        # self.assertEqual(overview.status_code, 200)
        # self.assertEqual(health.json()["status"], "Account Service is healthy")
        # self.assertIn("Welcome to the Account Service API", welcome.json()["message"])
