from django.shortcuts import render, redirect
from .models import Balance
from django.contrib.auth import login, authenticate
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie

def get_or_create_balance(request):
    if not request.session.session_key:
        request.session.create()
    session_id = request.session.session_key

    if request.user.is_authenticated:
        # Для авторизованного пользователя
        try:
            # Пытаемся найти баланс по пользователю
            balance = Balance.objects.get(user=request.user)
            if balance.session_id != session_id:
                # Проверяем, не использует ли кто-то другой этот session_id
                existing_balance = Balance.objects.filter(session_id=session_id).first()
                if existing_balance and existing_balance.id != balance.id:
                    # Если session_id занят, генерируем новый
                    request.session.cycle_key()
                    session_id = request.session.session_key
                
                balance.session_id = session_id
                balance.save()
            return balance
        except Balance.DoesNotExist:
            # Проверяем существующий баланс по session_id
            existing_balance = Balance.objects.filter(session_id=session_id).first()
            if existing_balance:
                # Если нашли баланс по session_id, привязываем его к пользователю
                existing_balance.user = request.user
                existing_balance.save()
                return existing_balance
            else:
                # Создаем новый баланс
                return Balance.objects.create(
                    user=request.user,
                    session_id=session_id,
                    amount=1000.00
                )
    else:
        # Для анонимного пользователя
        try:
            return Balance.objects.get(session_id=session_id)
        except Balance.DoesNotExist:
            return Balance.objects.create(
                session_id=session_id,
                amount=1000.00
            )

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

@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return JsonResponse({'error': 'Пароли не совпадают'}, status=400)

        try:
            user = User.objects.create_user(username=username, email=email, password=password1)
            login(request, user)
            
            # Привязываем существующий баланс к пользователю или создаем новый
            session_balance = Balance.objects.filter(session_id=request.session.session_key).first()
            if session_balance:
                session_balance.user = user
                session_balance.save()
            else:
                balance = Balance.objects.create(user=user, session_id=request.session.session_key)
            
            balance = get_or_create_balance(request)
            return JsonResponse({
                'username': user.username,
                'balance': str(balance.amount)
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

@ensure_csrf_cookie
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(request, user)
            balance = get_or_create_balance(request)
            
            return JsonResponse({
                'username': user.username,
                'balance': str(balance.amount)
            })
        else:
            return JsonResponse({'error': 'Неверное имя пользователя или пароль'}, status=400)
            
    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)

def profile(request):
    if request.user.is_authenticated:
        balance = get_or_create_balance(request)
        return render(request, 'crash/profile.html', {'balance': balance})
    return redirect('login')  # Перенаправление на страницу входа, если не авторизован


