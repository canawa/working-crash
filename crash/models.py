from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

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

class Balance(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"Balance: {self.amount}₽ (User: {self.user.username})"
        return f"Balance: {self.amount}₽ (Session: {self.session_id})"