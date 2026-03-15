from django.contrib import admin

from .models import DailyPage, ReadingLink


class ReadingLinkInline(admin.TabularInline):
    model = ReadingLink
    extra = 3
    fields = ('ref_text', 'url', 'display_order')
    ordering = ('display_order', 'id')


@admin.register(DailyPage)
class DailyPageAdmin(admin.ModelAdmin):
    list_display = ('page_date', 'title')
    search_fields = ('title', 'body', 'prayer')
    ordering = ('page_date',)
    inlines = [ReadingLinkInline]


@admin.register(ReadingLink)
class ReadingLinkAdmin(admin.ModelAdmin):
    list_display = ('ref_text', 'page', 'display_order')
    search_fields = ('ref_text', 'url', 'page__title')
    list_filter = ('page__page_date',)
    ordering = ('page', 'display_order', 'id')
