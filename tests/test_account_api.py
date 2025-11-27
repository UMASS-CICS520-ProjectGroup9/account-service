import pytest
from datetime import timedelta
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.backends import TokenBackend

from base.models import Account


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def token_backend(settings):
    algorithm = settings.SIMPLE_JWT.get("ALGORITHM", "HS256")
    signing_key = settings.SIMPLE_JWT.get("SIGNING_KEY", settings.SECRET_KEY)
    return TokenBackend(algorithm=algorithm, signing_key=signing_key)


@pytest.fixture
def make_auth_headers(token_backend):
    def _make(role="STUDENT", user_id=1, email="user@example.com", username="user"):
        payload = {
            "user_id": user_id,
            "email": email,
            "username": username,
            "role": role,
        }
        token = token_backend.encode(payload)
        return {"HTTP_AUTHORIZATION": f"bearer {token}"}

    return _make


@pytest.fixture
def admin_headers(make_auth_headers):
    return make_auth_headers(role="ADMIN", user_id=999, email="admin@example.com", username="admin")


@pytest.fixture
def student_headers(make_auth_headers):
    return make_auth_headers(role="STUDENT", user_id=111, email="student@example.com", username="student")


# @pytest.mark.django_db
# def test_requires_authentication(api_client):
#     response = api_client.get("/api/account/")
#     assert response.status_code == 401


@pytest.mark.django_db
def test_admin_can_list_accounts(api_client, admin_headers):
    Account.objects.create(email="alice@example.com", fullname="Alice", role="ADMIN", creator_id=1)
    Account.objects.create(email="bob@example.com", fullname="Bob", role="STUDENT", creator_id=2)

    response = api_client.get("/api/account/", **admin_headers)
    assert response.status_code == 200
    data = response.json()
    emails = {acct["email"] for acct in data}
    assert emails == {"alice@example.com", "bob@example.com"}


@pytest.mark.django_db
def test_student_can_fetch_account_by_email(api_client, student_headers):
    account = Account.objects.create(email="target@example.com", fullname="Target User", role="STUDENT", creator_id=7)

    response = api_client.get(f"/api/account/get/{account.email}/", **student_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "target@example.com"


@pytest.mark.django_db
def test_student_create_sets_email_role_and_creator_from_token(api_client, student_headers):
    body = {"email": "ignored@example.com", "fullname": "Created User", "role": "ADMIN"}

    response = api_client.post("/api/account/create/", body, format="json", **student_headers)
    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "student@example.com"
    assert payload["role"] == "STUDENT"
    assert payload["creator_id"] == 111
    assert Account.objects.filter(email="student@example.com").exists()


@pytest.mark.django_db
def test_owner_can_update_account(api_client, make_auth_headers):
    account = Account.objects.create(
        email="owner@example.com", fullname="Owner Name", role="STUDENT", creator_id=55
    )
    headers = make_auth_headers(role="STUDENT", user_id=55, email="owner@example.com", username="owner")
    response = api_client.put(
        "/api/account/update/",
        {"email": account.email, "fullname": "Updated Name"},
        format="json",
        **headers,
    )

    assert response.status_code == 200
    account.refresh_from_db()
    assert account.fullname == "Updated Name"


@pytest.mark.django_db
def test_student_cannot_update_another_users_account(api_client, student_headers):
    account = Account.objects.create(
        email="other@example.com", fullname="Other Name", role="STUDENT", creator_id=222
    )

    response = api_client.put(
        "/api/account/update/",
        {"email": account.email, "fullname": "Attempted Change"},
        format="json",
        **student_headers,
    )

    assert response.status_code == 404
    account.refresh_from_db()
    assert account.fullname == "Other Name"


@pytest.mark.django_db
def test_admin_can_delete_any_account(api_client, admin_headers):
    account = Account.objects.create(
        email="delete-me@example.com", fullname="Delete Me", role="STUDENT", creator_id=333
    )

    response = api_client.delete(
        "/api/account/delete/",
        {"email": account.email},
        format="json",
        **admin_headers,
    )

    assert response.status_code == 200
    assert Account.objects.filter(email=account.email).count() == 0


@pytest.mark.django_db
def test_student_cannot_delete_another_users_account(api_client, student_headers):
    account = Account.objects.create(
        email="keep-me@example.com", fullname="Keep Me", role="STUDENT", creator_id=444
    )

    response = api_client.delete(
        "/api/account/delete/",
        {"email": account.email},
        format="json",
        **student_headers,
    )

    assert response.status_code == 404
    assert Account.objects.filter(email=account.email).exists()


@pytest.mark.django_db
def test_count_endpoints(api_client, admin_headers):
    Account.objects.create(email="one@example.com", fullname="One", role="STUDENT", creator_id=1)
    Account.objects.create(email="two@example.com", fullname="Two", role="ADMIN", creator_id=1)
    Account.objects.create(email="three@example.com", fullname="Three", role="ADMIN", creator_id=1)

    count_response = api_client.get("/api/account/count/", **admin_headers)
    assert count_response.status_code == 200
    assert count_response.json()["count"] == 3

    role_response = api_client.get("/api/account/count_by_role/ADMIN/", **admin_headers)
    assert role_response.status_code == 200
    assert role_response.json()["count"] == 2
    assert role_response.json()["role"] == "ADMIN"


@pytest.mark.django_db
def test_filter_by_role(api_client, admin_headers):
    Account.objects.create(email="admin@example.com", fullname="Admin", role="ADMIN", creator_id=1)
    Account.objects.create(email="student@example.com", fullname="Student", role="STUDENT", creator_id=1)

    response = api_client.get("/api/account/role/ADMIN/", **admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["role"] == "ADMIN"


@pytest.mark.django_db
def test_filter_by_created_after(api_client, admin_headers):
    two_days_ago = timezone.now() - timedelta(days=2)
    yesterday = timezone.now() - timedelta(days=1)
    old_account = Account.objects.create(email="old@example.com", fullname="Old", role="ADMIN", creator_id=1)
    recent_account = Account.objects.create(email="recent@example.com", fullname="Recent", role="ADMIN", creator_id=1)
    Account.objects.filter(pk=old_account.pk).update(created_at=two_days_ago)
    Account.objects.filter(pk=recent_account.pk).update(created_at=timezone.now())

    response = api_client.get(
        f"/api/account/created_after/{yesterday.isoformat()}/",
        **admin_headers,
    )
    assert response.status_code == 200
    emails = {acct["email"] for acct in response.json()}
    assert emails == {"recent@example.com"}


@pytest.mark.django_db
def test_filter_by_updated_before(api_client, admin_headers):
    cutoff = timezone.now() - timedelta(days=1)
    old_account = Account.objects.create(email="stale@example.com", fullname="Stale", role="ADMIN", creator_id=1)
    fresh_account = Account.objects.create(email="fresh@example.com", fullname="Fresh", role="ADMIN", creator_id=1)
    old_timestamp = timezone.now() - timedelta(days=5)
    Account.objects.filter(pk=old_account.pk).update(updated_at=old_timestamp)

    response = api_client.get(
        f"/api/account/updated_before/{cutoff.isoformat()}/",
        **admin_headers,
    )
    assert response.status_code == 200
    emails = {acct["email"] for acct in response.json()}
    assert emails == {"stale@example.com"}
