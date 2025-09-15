from django.urls import path

from communications.apps import CommunicationsConfig
from communications.views import (
    CreateMessage,
    DeleteMessage,
    DetailMessage,
    ListMailings,
    ListMessages,
    UpdateMessage,
)

app_name = CommunicationsConfig.name

urlpatterns = [
    path("", ListMailings.as_view(), name="home"),
    path("messages/list/", ListMessages.as_view(), name="list-messages"),
    path("message/create/", CreateMessage.as_view(), name="create-message"),
    path("message/<int:pk>/update/", UpdateMessage.as_view(), name="update-message"),
    path("message/<int:pk>/detail/", DetailMessage.as_view(), name="detail-message"),
    path("message/<int:pk>/delete/", DeleteMessage.as_view(), name="delete-message"),
]
