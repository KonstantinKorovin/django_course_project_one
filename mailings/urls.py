from django.urls import path

from mailings.apps import MailingConfig
from mailings.views import (
    CreateMailing,
    DeleteMailing,
    DetailMailing,
    LaunchMailingView,
    ListMailings,
    MailingDisableView,
    UpdateMailing,
)

app_name = MailingConfig.name

urlpatterns = [
    path("list/", ListMailings.as_view(), name="list-mailings"),
    path("create/", CreateMailing.as_view(), name="create-mailing"),
    path(
        "<int:pk>/update/",
        UpdateMailing.as_view(),
        name="update-mailing",
    ),
    path(
        "<int:pk>/detail/",
        DetailMailing.as_view(),
        name="detail-mailing",
    ),
    path(
        "<int:pk>/delete/",
        DeleteMailing.as_view(),
        name="delete-mailing",
    ),
    path("<int:pk>/launch/", LaunchMailingView.as_view(), name="launch-mailing"),
    path(
        "disable/mailing/<int:pk>/",
        MailingDisableView.as_view(),
        name="disable-mailing",
    ),
]
