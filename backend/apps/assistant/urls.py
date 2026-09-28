from django.urls import path

from apps.assistant import views

app_name = "assistant"

urlpatterns = [
    path("chat/", views.chat, name="chat"),
]
