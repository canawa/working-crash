from django.shortcuts import render, HttpResponse
import secrets
import time
import json
from .models import GameStats
import asyncio
from asgiref.sync import sync_to_async
from django.http import JsonResponse
import threading
from datetime import datetime
from functools import partial
from django.views.decorators.csrf import csrf_protect

# Глобальные переменные для отслеживания состояния игры
current_game = {
    'status': 'waiting',  # waiting, running, crashed
    'current_multiplier': 1.00,
    'crash_point': None,
    'start_time': None,
    'game_id': 0,
    'countdown': 10,  # Для начальной паузы на ставки
    'next_game_time': time.time() + 10
}

# Глобальная переменная для хранения event loop
game_loop = None

def start_game_loop():
    global game_loop
    if game_loop is None or not game_loop.is_running():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        game_loop = loop
        
        # Запускаем игровой цикл
        loop.create_task(update_game_state())
        
        try:
            loop.run_forever()
        except Exception as e:
            print(f"Game loop error: {e}")

# Запускаем игровой цикл в отдельном потоке
game_thread = threading.Thread(target=start_game_loop, daemon=True)
game_thread.start()

async def calculate_crash_point():
    raw = secrets.randbelow(10**9) / 10**9
    if raw == 0:
        raw = 0.001
    multiplier = 1 / raw * 0.95
    multiplier = round(multiplier, 2)
    
    if multiplier < 1:
        raw = secrets.randbelow(10**9) / 10**9
        multiplier = 1 / raw * 0.95
        multiplier = round(multiplier, 2)
        
        if multiplier < 1:
            multiplier = 1.00
    
    return multiplier

async def update_game_state():
    print("Game loop started")
    while True:
        try:
            current_time = time.time()
            
            if current_game['status'] == 'waiting':
                remaining = int(current_game['next_game_time'] - current_time)
                current_game['countdown'] = max(0, remaining)
                print(f"Waiting: {current_game['countdown']} seconds")
                
                if current_time >= current_game['next_game_time']:
                    print("Starting new game")
                    current_game['crash_point'] = await calculate_crash_point()
                    current_game['current_multiplier'] = 1.00
                    current_game['start_time'] = current_time
                    current_game['status'] = 'running'
                    current_game['game_id'] += 1
                    
                    await sync_to_async(GameStats.objects.create)(
                        coef=current_game['crash_point'],
                        game_id=current_game['game_id']
                    )
            
            elif current_game['status'] == 'running':
                elapsed = current_time - current_game['start_time']
                # Более плавная формула роста с точностью до сотых
                current_multiplier = 1.0 + (0.05 * elapsed) * (1.0 + elapsed * 0.08)
                # Округляем до 2 знаков после запятой для плавности
                current_game['current_multiplier'] = float(f"{current_multiplier:.2f}")
                
                print(f"Running: {current_game['current_multiplier']}x")
                
                if current_game['current_multiplier'] >= current_game['crash_point']:
                    print(f"Crashed at {current_game['crash_point']}x")
                    current_game['status'] = 'crashed'
                    current_game['next_game_time'] = current_time + 5  # 5 секунд после краша
            
            elif current_game['status'] == 'crashed':
                remaining = int(current_game['next_game_time'] - current_time)
                current_game['countdown'] = max(0, remaining)
                print(f"Crashed: {current_game['countdown']} seconds until next game")
                
                if current_time >= current_game['next_game_time']:
                    print("Resetting to waiting state")
                    current_game['status'] = 'waiting'
                    current_game['next_game_time'] = current_time + 10  # 10 секунд на ставки
            
            # Уменьшаем интервал обновления для более плавной анимации
            await asyncio.sleep(0.02)
            
        except Exception as e:
            print(f"Error in game loop: {e}")
            await asyncio.sleep(1)

def get_game_state(request):
    return JsonResponse(current_game)

def crash(request):
    return render(request, 'crash/index.html')

def move_to_main(request):
      return render(request, 'crash/index.html' )

def boss_fight(request):
     return render(request,'crash/boss_fight.html')
def mines(request):
     return render(request,'crash/mines.html')
def roullete(request):
     return render(request,'crash/roullete.html')
def ballon(request):
     return render(request,'crash/ballon.html')

def plinko(request):
     return render(request,'crash/plinko.html')

def stats(request):
    order = request.GET.get('order','game_id')
    data = GameStats.objects.order_by(order)
    context = {
         'direction' : 'asc' if not order.startswith('-') else 'desc'
    }
    return render(request, 'crash/all_game_stats.html', {'data':data })

@csrf_protect
def make_bet(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = float(data.get('amount', 0))
            auto_cashout = float(data.get('auto_cashout', 0))
            
            # Здесь добавьте вашу логику обработки ставки
            # Например, проверка баланса, сохранение ставки и т.д.
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


