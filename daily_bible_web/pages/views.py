from datetime import date

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render

from .models import DailyPage, ReadingLink


CATEGORY_IMAGE_MAP = {
    "全心爱主": "/static/images/picture1.jpg",
    "连结社群": "/static/images/picture2.jpg",
    "进入命定": "/static/images/picture3.jpg",
    "成为祝福": "/static/images/picture4.jpg",
}

DEFAULT_IMAGE = "/static/images/top_banner.jpg"


def _page_queryset():
    return DailyPage.objects.prefetch_related(
        Prefetch(
            'reading_links',
            queryset=ReadingLink.objects.order_by('display_order', 'id')
        )
    )


def _apply_category_image(page):
    if page is None:
        return None

    if not page.image_path:
        page.image_path = CATEGORY_IMAGE_MAP.get(page.category, DEFAULT_IMAGE)

    return page


def daily_page(request, page_date=None):
    qs = _page_queryset()

    if page_date:
        page = get_object_or_404(qs, page_date=page_date)
    else:
        today = date.today()
        page = qs.filter(page_date=today).first() or qs.order_by('page_date').last()
        if page is None:
            return render(
                request,
                'pages/daily_page.html',
                {'page': None, 'prev_page': None, 'next_page': None},
            )

    page = _apply_category_image(page)

    prev_page = DailyPage.objects.filter(page_date__lt=page.page_date).order_by('-page_date').first()
    next_page = DailyPage.objects.filter(page_date__gt=page.page_date).order_by('page_date').first()

    prev_page = _apply_category_image(prev_page)
    next_page = _apply_category_image(next_page)

    return render(
        request,
        'pages/daily_page.html',
        {
            'page': page,
            'prev_page': prev_page,
            'next_page': next_page,
        },
    )