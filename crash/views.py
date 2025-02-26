from django.shortcuts import render

def crash(request):
    return render(request, 'crash/index.html')

# Оставляем остальные view для других игр
def plinko(request):
    return render(request, 'crash/plinko.html')

def boss_fight(request):
    return render(request, 'crash/boss_fight.html')

def ballon(request):
    return render(request, 'crash/ballon.html')

def roullete(request):
    return render(request, 'crash/roulette.html')

def mines(request):
    return render(request, 'crash/mines.html')

def stats(request):
    return render(request, 'crash/stats.html')

# Удаляем get_game_state и make_bet, так как теперь используем WebSocket


