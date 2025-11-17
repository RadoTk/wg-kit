import calendar
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from wagtail.admin.viewsets.base import ViewSet

def index(request):
    current_year = timezone.now().year
    calendar_html = calendar.HTMLCalendar().formatyear(current_year)

    return render(request, 'agenda/calendar_admin.html', {
        'current_year': current_year,
        'calendar_html': calendar_html,
    })

def month(request):
    current_year = timezone.now().year
    current_month = timezone.now().month
    calendar_html = calendar.HTMLCalendar().formatmonth(current_year, current_month)

    return render(request, 'agenda/calendar_admin.html', {
        'current_year': current_year,
        'calendar_html': calendar_html,
    })


class AgendaViewSet(ViewSet):
    add_to_admin_menu = True
    menu_label = "Agenda"
    icon = "date"
    # The `name` will be used for both the URL prefix and the URL namespace.
    # They can be customized individually via `url_prefix` and `url_namespace`.
    name = "agenda"     

    def get_urlpatterns(self):
        return [
            # This can be accessed at `/admin/agenda/`
            # and reverse-resolved with the name `agenda:index`.
            # This first URL will be used for the menu item, but it can be
            # customized by overriding the `menu_url` property.
            path('', index, name='index'),

            # This can be accessed at `/admin/agenda/month/`    
            # and reverse-resolved with the name `agenda:month`.
            path('month/', month, name='month'),
        ]