from django.urls import path
from . import views

# urlpatterns = [
#     path("", views.calendar_view, name="calendar"),
#     path("events-json/", views.events_json, name="events_json"),
#     path("symbols-json/", views.symbols_json, name="symbols_json"),
# ]

urlpatterns = [
    path("api/v1/events/", views.events_json, name="api_events"),
    path("api/v1/symbols/", views.symbols_json, name="api_symbols"),
    path("", views.calendar_view, name="calendar_view"),
]