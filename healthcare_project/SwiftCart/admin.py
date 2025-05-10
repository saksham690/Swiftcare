from django.contrib import admin
from .models import Medicine, Order, OrderItem

@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'stock_quantity', 'is_in_stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock_quantity')

    def is_in_stock(self, obj):
        return obj.stock_quantity > 0
    is_in_stock.boolean = True

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('medicine', 'quantity')
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'is_paid', 'status')
    list_filter = ('status', 'is_paid')
    search_fields = ('user__username', 'id')
    list_editable = ('status',)
    readonly_fields = ('created_at',)
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'medicine', 'quantity')
    search_fields = ('medicine__name', 'order__id')