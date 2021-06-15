from django.contrib import admin

from marketplace.models import Product, Collection, Order, Review, OrderProduct, CollectionProduct

admin.site.register(Review)


class CollectionProductInline(admin.TabularInline):
    model = CollectionProduct


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    inlines = [CollectionProductInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']


class OrderProductInline(admin.TabularInline):
    model = OrderProduct


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['created_at']
    # readonly_fields = ('amount',)
    inlines = [OrderProductInline]
