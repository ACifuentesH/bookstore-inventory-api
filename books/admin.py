from django.contrib import admin
from .models import Book, PriceHistory


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'title', 
        'author', 
        'isbn', 
        'cost_usd', 
        'selling_price_local', 
        'stock_quantity', 
        'category',
        'supplier_country',
        'is_low_stock_display',
        'created_at'
    ]
    list_filter = ['category', 'supplier_country', 'created_at']
    search_fields = ['title', 'author', 'isbn']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['title']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'author', 'isbn', 'category', 'supplier_country')
        }),
        ('Precios', {
            'fields': ('cost_usd', 'selling_price_local')
        }),
        ('Inventario', {
            'fields': ('stock_quantity',)
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_low_stock_display(self, obj):
        """Mostrar si el stock está bajo"""
        return "⚠️ Bajo" if obj.is_low_stock() else "✅ OK"
    is_low_stock_display.short_description = "Estado Stock"
    
    def save_model(self, request, obj, form, change):
        """Recalcular precio sugerido al guardar"""
        super().save_model(request, obj, form, change)
        if not obj.selling_price_local:
            obj.update_suggested_price()


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['book', 'cost_usd', 'selling_price_local', 'exchange_rate_used', 'created_at']
    list_filter = ['created_at', 'book__category']
    search_fields = ['book__title', 'book__author']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
