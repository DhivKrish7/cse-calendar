from django.db import models
from django.core.exceptions import ValidationError

class StockEvent(models.Model):

    EVENT_TYPES = [
        ('DIVIDEND', 'Dividend'),
        ('SPLIT', 'Split'),
        ('RIGHTS ISSUE', 'Rights Issue'),
        ('AGM', 'AGM'),
        ('BONUS ISSUE', 'Bonus Issue'),
        ('EARNINGS', 'Earnings'),
    ]

    stock_symbol = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES)
    announcement_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['announcement_date']
        indexes = [
            models.Index(fields=['announcement_date']),
            models.Index(fields=['stock_symbol', 'announcement_date']),
            models.Index(fields=['event_type', 'announcement_date']),
        ]

    def clean(self):
        if not self.stock_symbol:
            raise ValidationError("Stock Symbol is required!")
        
    def __str__(self):
        return f"{self.stock_symbol} - {self.event_type}"
    
class DividendEvent(models.Model):
    Dividend_Types = [
        ('CASH', 'Cash Dividend'),
        ('SCRIP', 'Scrip Dividend'),
    ]
    event = models.OneToOneField(
        StockEvent,
        on_delete=models.CASCADE,
        related_name="dividend_details"
    )

    dividend_type = models.CharField(max_length=10, choices=Dividend_Types)
    xd_date = models.DateField()
    dividend_per_share = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    scrip_ratio = models.CharField(max_length=6, blank=True, null=True)
    payment_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if self.event.event_type != "DIVIDEND":
            raise ValidationError("This record must linked to a Dividend Event!")
        if self.xd_date < self.event.announcement_date:
            raise ValidationError("XD Date cant be before Announcemet Date!")
        if self.payment_date < self.xd_date:
            raise ValidationError("Payment Date cant be before XD Date!")
        if self.dividend_type == "CASH":
            if not self.dividend_per_share:
                raise ValidationError("Cash Dividend must requires Dividend Per Share!")
        if self.dividend_type == "SCRIP":
            if not self.scrip_ratio:
                raise ValidationError("Scrip Dividend requires Scrip Ratio!")
            
    def __str__(self):
        return f"Dividend Details - {self.event.stock_symbol}"
    
class RightsIssueEvent(models.Model):
    event = models.OneToOneField(
        StockEvent,
        on_delete=models.CASCADE,
        related_name="rights_details"
    )

    xr_date = models.DateField()
    rights_ratio = models.CharField(max_length=20)
    subscription_price = models.DecimalField(max_digits=10, decimal_places=2)
    trade_start_date = models.DateField()
    trade_close_date = models.DateField()
    last_payment_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if self.event.event_type != "RIGHTS ISSUE":
            raise ValidationError("This record must linked to a Rights Issue Event!")
        if self.xr_date < self.event.announcement_date:
            raise ValidationError("XR Date cant be before Announcemet Date!")
        if self.trade_close_date < self.trade_start_date:
            raise ValidationError("Trade Close Date cant be before Trade Start Date!")
        if self.last_payment_date < self.xr_date:
            raise ValidationError("Payment Date cant be before XR Date!")
    def __str__(self):
        return f"Rights Issue Details - {self.event.stock_symbol}"
    
class BonusIssueEvent(models.Model):
    event = models.OneToOneField(
        StockEvent,
        on_delete=models.CASCADE,
        related_name= "bonus_details"
    )

    bonus_ratio = models.CharField(max_length=10)
    xd_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if self.event.event_type != "BONUS ISSUE":
            raise ValidationError("This record must linked to a Bonus Issue Event!")
        if self.xd_date < self.event.announcement_date:
            raise ValidationError("XD Date cant be before Announcemet Date!")
        if not self.bonus_ratio:
            raise ValidationError("Bonus Ratio cant be empty!")
    
    def __str__(self):
        return f"Bonus Issue Details - {self.event.stock_symbol}"
    
class SplitEvent(models.Model):
    event = models.OneToOneField(
        StockEvent,
        on_delete=models.CASCADE,
        related_name= "split_details"
    )

    split_ratio = models.CharField(max_length=10)
    xd_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if self.event.event_type != "SPLIT":
            raise ValidationError("This record must linked to a Split Event!")
        if self.xd_date < self.event.announcement_date:
            raise ValidationError("XD Date cant be before Announcemet Date!")
        if not self.split_ratio:
            raise ValidationError("Split Ratio cant be empty!")

    def __str__(self):
        return f"Stock Split - {self.event.stock_symbol}"
    
class EarningsEvent(models.Model):
    event = models.OneToOneField(
        StockEvent,
        on_delete=models.CASCADE,
        related_name="earnings_details"
    )

    report_period = models.CharField(max_length=10)
    report_date = models.DateField()
    description = models.TextField(blank=True, null=True)

    def clean(self):
        if self.event.event_type != "EARNINGS":
            raise ValidationError("This record must linked to a Earnings Event!")
        if self.report_date < self.event.announcement_date:
            raise ValidationError("Report Date cant be before Announcemet Date!")
        if not self.report_period:
            raise ValidationError("Report Period cant be empty!")

    def __str__(self):
        return f"Earnings Details - {self.event.stock_symbol}"