from datetime import datetime

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

from .models import StockEvent

def calendar_view(request):
    events = StockEvent.objects.all()
    return render(request, 'events/calendar.html', {'events': events})

def events_json(request):

    start = request.GET.get("start")
    end = request.GET.get("end")
    symbol = request.GET.get('symbol')
    event_type = request.GET.get('type')

    cache_key = f"events_{start}_{end}_{symbol}_{event_type}"

    cached_response = cache.get(cache_key)
    if cached_response:
        return JsonResponse(cached_response)

    qs = StockEvent.objects.all().select_related(
        'dividend_details',
        'rights_details',
        'bonus_details',
        'split_details',
        'earnings_details'
    )

    if start and end:
        try:
            start_date = datetime.fromisoformat(start).date()
            end_date = datetime.fromisoformat(end).date()
            qs = qs.filter(announcement_date__range=[start_date, end_date])
        except ValueError:
            pass

    if symbol and symbol != "ALL":
        qs = qs.filter(stock_symbol__iexact=symbol)

    if event_type and event_type != "ALL":
        qs = qs.filter(event_type=event_type)

    events = []

    for e in qs:
        base_title = f"{e.stock_symbol} - {e.event_type}"

        events.append({
            "title": f"{base_title} (Announcement)",
            "start": e.announcement_date.strftime("%Y-%m-%d"),
            "extendedProps": {
                "symbol": e.stock_symbol,
                "type": e.event_type,
                "date_type": "announcement",
            }
        })

        if hasattr(e, "dividend_details") and e.dividend_details:
            d = e.dividend_details
            if d.xd_date:
                events.append({
                    "title": f"{base_title} (XD)",
                    "start": d.xd_date.strftime("%Y-%m-%d"),
                    "extendedProps": {
                        "symbol": e.stock_symbol,
                        "type": e.event_type,
                        "date_type": "xd"
                    }
                })

        if hasattr(e, "rights_details") and e.rights_details:
            r = e.rights_details
            if r.xr_date:
                events.append({
                    "title": f"{base_title} (XR)",
                    "start": r.xr_date.strftime("%Y-%m-%d"),
                    "extendedProps": {
                        "symbol": e.stock_symbol,
                        "type": e.event_type,
                        "date_type": "xr"
                    }
                })

        if hasattr(e, "bonus_details") and e.bonus_details:
            b = e.bonus_details
            if b.xd_date:
                events.append({
                    "title": f"{base_title} (XB)",
                    "start": b.xd_date.strftime("%Y-%m-%d"),
                    "extendedProps": {
                        "symbol": e.stock_symbol,
                        "type": e.event_type,
                        "date_type": "xb"
                    }
                })

        if hasattr(e, "split_details") and e.split_details:
            s = e.split_details
            if s.xd_date:
                events.append({
                    "title": f"{base_title} (XS)",
                    "start": s.xd_date.strftime("%Y-%m-%d"),
                    "extendedProps": {
                        "symbol": e.stock_symbol,
                        "type": e.event_type,
                        "date_type": "xs"
                    }
                })

        if hasattr(e, "earnings_details") and e.earnings_details:
            er = e.earnings_details
            if er.report_date:
                events.append({
                    "title": f"{base_title} (Earnings)",
                    "start": er.report_date.strftime("%Y-%m-%d"),
                    "extendedProps": {
                        "symbol": e.stock_symbol,
                        "type": e.event_type,
                        "date_type": "earnings"
                    }
                })

    response = {
        "status": "success",
        "count": len(events),
        "data": events
    }

    cache.set(cache_key, response, timeout=300)

    return JsonResponse(response)

def symbols_json(request):
    query = request.GET.get("q", "")

    qs = StockEvent.objects.all()

    if query:
        qs = qs.filter(stock_symbol__icontains=query)

    symbols = qs.values_list("stock_symbol", flat=True).distinct()

    return JsonResponse(list(symbols), safe=False)
