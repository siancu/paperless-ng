from django.contrib import admin
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe
from whoosh.writing import AsyncWriter

from . import index
from .models import Correspondent, Document, DocumentType, Log, Tag, \
    SavedView, SavedViewFilterRule


class CorrespondentAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "match",
        "matching_algorithm"
    )
    list_filter = ("matching_algorithm",)
    list_editable = ("match", "matching_algorithm")


class TagAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "colour",
        "match",
        "matching_algorithm"
    )
    list_filter = ("colour", "matching_algorithm")
    list_editable = ("colour", "match", "matching_algorithm")


class DocumentTypeAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "match",
        "matching_algorithm"
    )
    list_filter = ("matching_algorithm",)
    list_editable = ("match", "matching_algorithm")


class DocumentAdmin(admin.ModelAdmin):

    search_fields = ("correspondent__name", "title", "content", "tags__name")
    readonly_fields = (
        "added",
        "modified",
        "mime_type",
        "storage_type",
        "filename",
        "checksum",
        "archive_filename",
        "archive_checksum"
    )

    list_display_links = ("title",)

    list_display = (
        "created",
        "added",
        "archive_serial_number",
        "title",
        "mime_type",
        "filename",
        "archive_filename"
    )

    list_filter = (
        ("mime_type"),
        ("archive_serial_number", admin.EmptyFieldListFilter),
        ("archive_filename", admin.EmptyFieldListFilter),
    )

    filter_horizontal = ("tags",)

    ordering = ["-created"]

    date_hierarchy = "created"

    def has_add_permission(self, request):
        return False

    def created_(self, obj):
        return obj.created.date().strftime("%Y-%m-%d")
    created_.short_description = "Created"

    def delete_queryset(self, request, queryset):
        ix = index.open_index()
        with AsyncWriter(ix) as writer:
            for o in queryset:
                index.remove_document(writer, o)
        super(DocumentAdmin, self).delete_queryset(request, queryset)

    def delete_model(self, request, obj):
        index.remove_document_from_index(obj)
        super(DocumentAdmin, self).delete_model(request, obj)

    def save_model(self, request, obj, form, change):
        index.add_or_update_document(obj)
        super(DocumentAdmin, self).save_model(request, obj, form, change)


class RuleInline(admin.TabularInline):
    model = SavedViewFilterRule


class SavedViewAdmin(admin.ModelAdmin):

    list_display = ("name", "user")

    inlines = [
        RuleInline
    ]


admin.site.register(Correspondent, CorrespondentAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(DocumentType, DocumentTypeAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(SavedView, SavedViewAdmin)
