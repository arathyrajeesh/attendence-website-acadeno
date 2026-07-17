import datetime
import calendar


def month_end_alert(request):
    today = datetime.date.today()
    last_day = calendar.monthrange(today.year, today.month)[1]
    days_left = last_day - today.day
    return {
        'month_end_alert': days_left <= 4,
        'month_end_days': days_left,
        'current_month_name': today.strftime('%B %Y'),
        'current_year': today.year,
        'current_month': today.month,
    }
