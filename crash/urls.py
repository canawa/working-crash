from django.urls import path
from . import views

urlpatterns = [
    path('', views.crash, name='crash'),
    path('plinko/', views.plinko, name='plinko'),
    path('boss_fight', views.boss_fight, name='boss_fight'),
    path('ballon', views.ballon, name='ballon'),
    path('roulette', views.roullete, name='roulette'),
    path('mines', views.mines, name='mines'),
    path('stats/', views.stats, name='all_stats'),
    path('stats/crash', views.stats, name='stats_crash'),
    path('stats/mines', views.stats, name='stats_mines'),
    path('stats/bossfight', views.stats, name='stats_boss_fight'),
    path('stats/plinko', views.stats, name='stats_plinko'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('profile/', views.profile, name='profile'),
]