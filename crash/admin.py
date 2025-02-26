from django.contrib import admin
from .models import GameStats, GameResult
# Register your models here.
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