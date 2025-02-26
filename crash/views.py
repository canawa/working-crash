from django.shortcuts import render
from .models import Balance

def get_or_create_balance(request):
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
    
    balance, created = Balance.objects.get_or_create(
        session_id=session_id,
        defaults={'amount': 1000.00}
    )
    return balance

def crash(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/index.html', {'balance': balance})

# Оставляем остальные view для других игр
def plinko(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/plinko.html', {'balance': balance})

def boss_fight(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/boss_fight.html', {'balance': balance})

def ballon(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/ballon.html', {'balance': balance})

def roullete(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/roulette.html', {'balance': balance})

def mines(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/mines.html', {'balance': balance})

def stats(request):
    balance = get_or_create_balance(request)
    return render(request, 'crash/stats.html', {'balance': balance})

# Удаляем get_game_state и make_bet, так как теперь используем WebSocket


