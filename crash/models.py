from django.db import models

# Create your models here.
class GameStats(models.Model):
    game_id = models.AutoField(primary_key=True)  # Автоинкремент без ручного управления
    coef = models.FloatField('Коэффициент')
    player_id = models.TextField('ID игрока',default='-') 
    time=models.DateTimeField('Время', auto_now_add=True, )
   
    
    
    class Meta:
        verbose_name = 'Статистика Игр'
        verbose_name_plural = 'Статистика Игр'