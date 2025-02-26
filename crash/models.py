from django.db import models
from django.utils import timezone

# Create your models here.
class GameStats(models.Model):
    game_id = models.AutoField(primary_key=True)  # Автоинкремент без ручного управления
    coef = models.FloatField('Коэффициент')
    player_id = models.TextField('ID игрока',default='-') 
    time=models.DateTimeField('Время', auto_now_add=True, )
   
    
    
    class Meta:
        verbose_name = 'Статистика Игр'
        verbose_name_plural = 'Статистика Игр'

class GameResult(models.Model):
    round_number = models.IntegerField(unique=True)
    timestamp = models.DateTimeField(default=timezone.now)
    multiplier = models.DecimalField(max_digits=10, decimal_places=2)
    casino_profit = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ['-timestamp']
        
    def __str__(self):
        return f"Round {self.round_number} - x{self.multiplier} - Profit: {self.casino_profit}₽"