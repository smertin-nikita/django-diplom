from django.contrib import admin

from marketplace.models import Product, Collection, Order, Review, ProductOrder

admin.site.register(Collection)
admin.site.register(Review)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    search_fields = ['title', 'description']


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder

# todo разобраться на каком этапе считать сумму заказа
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['created_at']
    # readonly_fields = ('amount',)
    inlines = [ProductOrderInline]
