from django.contrib import admin
from .models import StockEvent, DividendEvent, RightsIssueEvent, BonusIssueEvent, SplitEvent, EarningsEvent

class DividendInline(admin.StackedInline):
    model = DividendEvent
    extra = 0

class RightsInline(admin.StackedInline):
    model = RightsIssueEvent
    extra = 0

class BonusInline(admin.StackedInline):
    model = BonusIssueEvent
    extra = 0

class SplitInline(admin.StackedInline):
    model = SplitEvent
    extra = 0

class EarningsInline(admin.StackedInline):
    model = EarningsEvent
    extra = 0

# admin.site.register(StockEvent)
@admin.register(StockEvent)
class StockEventAdmin(admin.ModelAdmin):
    list_display = ('stock_symbol', 'event_type', 'announcement_date')
    list_filter = ('event_type',)
    search_fields = ('stock_symbol',)

    inlines = [
        DividendInline,
        RightsInline,
        SplitInline,
        BonusInline,
        EarningsInline
    ]

    def save_model(self, request, obj, form, change):
        obj.full_clean()
        super().save_model(request, obj, form, change)

    class Media:
        js = ('events/admin.js',)
