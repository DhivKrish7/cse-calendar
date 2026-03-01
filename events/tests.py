from django.test import TestCase
from django.urls import reverse

from .models import BonusIssueEvent, SplitEvent, StockEvent


class EventsJsonViewTests(TestCase):
    def test_bonus_and_split_secondary_dates_are_serialized(self):
        bonus_base = StockEvent.objects.create(
            stock_symbol="ABC",
            event_type="BONUS ISSUE",
            announcement_date="2026-01-01",
        )
        BonusIssueEvent.objects.create(
            event=bonus_base,
            bonus_ratio="1:1",
            xd_date="2026-01-15",
        )

        split_base = StockEvent.objects.create(
            stock_symbol="XYZ",
            event_type="SPLIT",
            announcement_date="2026-02-01",
        )
        SplitEvent.objects.create(
            event=split_base,
            split_ratio="2:1",
            xd_date="2026-02-10",
        )

        response = self.client.get(reverse("api_events"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["status"], "success")

        titles = {item["title"] for item in payload["data"]}
        self.assertIn("ABC - BONUS ISSUE (Announcement)", titles)
        self.assertIn("ABC - BONUS ISSUE (XB)", titles)
        self.assertIn("XYZ - SPLIT (Announcement)", titles)
        self.assertIn("XYZ - SPLIT (XS)", titles)
