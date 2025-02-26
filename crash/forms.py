from .models import GameStats
from django.forms import ModelForm      

class GameStatsForm(ModelForm):
    class Meta:
        model = GameStats
        