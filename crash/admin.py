from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Balance, GameStats, GameResult

class BalanceInline(admin.StackedInline):
    model = Balance
    can_delete = False

class CustomUserAdmin(UserAdmin):
    inlines = (BalanceInline,)
    list_display = ('username', 'email', 'get_balance', 'date_joined', 'last_login', 'is_staff')
    
    def get_balance(self, obj):
        try:
            return f"{obj.balance.amount}₽"
        except Balance.DoesNotExist:
            return "Нет баланса"
    get_balance.short_description = 'Баланс'

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(GameStats)

@admin.register(GameResult)
class GameResultAdmin(admin.ModelAdmin):
    list_display = ('round_number', 'timestamp', 'multiplier', 'casino_profit')
    list_filter = ('timestamp',)
    search_fields = ('round_number',)
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False  # Запрещаем ручное добавление результатов

    def has_change_permission(self, request, obj=None):
        return False  # Запрещаем изменение результатов