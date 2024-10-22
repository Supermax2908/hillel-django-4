from django.contrib import admin

from products.models import Product, Category, Tag

# Register your models here.
admin.site.register(Category)
admin.site.register(Tag)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    pass
    list_display = ['name', 'price', 'category']
    list_filter = ['category', 'tags', 'created_at']
    search_fields = ['name']
    # list_per_page = 10
    list_editable = ['price']
    list_display_links = ['name', 'category']
    list_select_related = ['category']
    list_prefetch_related = ['tags']
    list_max_show_all = 100

    # Custom actions
    actions = ['make_18_plus', 'disable_18_plus']

    def make_18_plus(self, request, queryset):
        queryset.update(is_18_plus=True)

    make_18_plus.short_description = 'Make 18+'
    make_18_plus.allowed_permissions = ('change',)

    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'description', 'is_18_plus')
        }),
        ('Relations', {
            'fields': ('category', 'tags')
        }),
        ('Images', {
            'fields': ('image',)
        }),
        ('Files', {
            'fields': ('manual',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    filter_horizontal = ['tags']

    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields.copy()

        if request.user.is_superuser:
            return fields
        return fields + ['price']
