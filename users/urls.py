from django.urls import path

from users.apps import UsersConfig
from users.views import (
    CreateRecipient,
    DeleteRecipient,
    DetailRecipient,
    DetailUser,
    ListRecipients,
    ListUsers,
    LoginUserView,
    LogoutUserView,
    PasswordResetView,
    RegisterUserView,
    UpdateRecipient,
    UserToggleActiveView,
    email_verification,
)

app_name = UsersConfig.name

urlpatterns = [
    path("recipients/list/", ListRecipients.as_view(), name="list-recipients"),
    path("recipients/create/", CreateRecipient.as_view(), name="create-recipient"),
    path(
        "recipients/<int:pk>/update/",
        UpdateRecipient.as_view(),
        name="update-recipient",
    ),
    path(
        "recipients/<int:pk>/detail/",
        DetailRecipient.as_view(),
        name="detail-recipient",
    ),
    path(
        "recipients/<int:pk>/delete/",
        DeleteRecipient.as_view(),
        name="delete-recipient",
    ),
    path("login/", LoginUserView.as_view(), name="user-login"),
    path(
        "logout/",
        LogoutUserView.as_view(next_page="users:user-logout"),
        name="user-logout",
    ),
    path("register/", RegisterUserView.as_view(), name="user-register"),
    path("email_confirm/<str:token>/", email_verification, name="email_confirm"),
    path("password-reset/", PasswordResetView.as_view(), name="password-reset"),
    path("list/users/", ListUsers.as_view(), name="list-users"),
    path("user/<int:pk>/", DetailUser.as_view(), name="detail-user"),
    path(
        "user/<int:pk>/toggle-active/",
        UserToggleActiveView.as_view(),
        name="user-toggle-active",
    ),
]
