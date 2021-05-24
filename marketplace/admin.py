from django.contrib import admin

from marketplace.models import Product, Collection, Order, Review, ProductOrder

admin.site.register(Product)
admin.site.register(Collection)
admin.site.register(Review)


class ProductOrderInline(admin.TabularInline):
    model = ProductOrder

# todo разобраться на каком этапе считать сумму заказа
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['created_at']
    readonly_fields = ('amount',)
    inlines = [ProductOrderInline]
