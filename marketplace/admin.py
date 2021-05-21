from django.contrib import admin

from marketplace.models import Product, Collection, Order, Review

admin.site.register(Product)
admin.site.register(Collection)
admin.site.register(Review)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    ordering = ['created_at']
