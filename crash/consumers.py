import json
from channels.generic.websocket import AsyncWebsocketConsumer
import time
import secrets
from asgiref.sync import sync_to_async
from .models import GameStats, GameResult
import asyncio
import logging
from decimal import Decimal

# Настраиваем логгер
logger = logging.getLogger('crash.game')

class CrashConsumer(AsyncWebsocketConsumer):
    game_state = {
        'status': 'waiting',
        'current_multiplier': 1.00,
        'crash_point': None,
        'start_time': None,
        'game_id': 0,
        'countdown': 10,
        'next_game_time': time.time() + 10,
        'bets': []  # Добавим список для хранения ставок
    }

    @classmethod
    async def get_next_game_id(cls):
        # Получаем последний game_id и увеличиваем его на 1
        last_game = await sync_to_async(GameStats.objects.all().order_by('-game_id').first)()
        if last_game:
            return last_game.game_id + 1
        return 1

    async def get_safe_state(self):
        """Получить безопасную версию состояния для клиента"""
        state = self.game_state.copy()
        if state['status'] != 'crashed':
            state.pop('crash_point', None)
        return state

    async def connect(self):
        await self.channel_layer.group_add("crash_game", self.channel_name)
        await self.accept()
        
        if not hasattr(CrashConsumer, 'game_loop_running'):
            self.game_state['game_id'] = await self.get_next_game_id() - 1
            CrashConsumer.game_loop_running = True
            asyncio.create_task(self.start_game_loop())
        
        # Отправляем безопасную версию состояния
        safe_state = await self.get_safe_state()
        await self.send(text_data=json.dumps(safe_state))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("crash_game", self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            if data['type'] == 'bet':
                # Сохраняем ставку
                bet = {
                    'amount': float(data['amount']),
                    'auto_cashout': float(data.get('auto_cashout', 0)),
                    'cashout_multiplier': None  # Будет установлено при выводе
                }
                self.game_state['bets'].append(bet)
            elif data['type'] == 'cashout':
                # При выводе средств сохраняем множитель
                for bet in self.game_state['bets']:
                    if bet.get('cashout_multiplier') is None:  # Если еще не было вывода
                        bet['cashout_multiplier'] = self.game_state['current_multiplier']
                        break
        except Exception as e:
            logger.error(f"Error processing message: {e}")

    async def game_update(self, event):
        state = event['state'].copy()
        
        # Удаляем crash_point из данных, если игра не закончилась
        if state['status'] != 'crashed':
            state.pop('crash_point', None)
        
        await self.send(text_data=json.dumps(state))

    async def calculate_crash_point(self):
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

    async def start_game_loop(self):
        while True:
            try:
                current_time = time.time()
                
                if self.game_state['status'] == 'waiting':
                    remaining = int(self.game_state['next_game_time'] - current_time)
                    self.game_state['countdown'] = max(0, remaining)
                    
                    if current_time >= self.game_state['next_game_time']:
                        self.game_state['crash_point'] = await self.calculate_crash_point()
                        self.game_state['current_multiplier'] = 1.00
                        self.game_state['start_time'] = current_time
                        self.game_state['status'] = 'running'
                        
                        # Получаем следующий уникальный game_id
                        next_game_id = await self.get_next_game_id()
                        self.game_state['game_id'] = next_game_id
                        
                        # Создаем запись в БД с уникальным game_id
                        await sync_to_async(GameStats.objects.create)(
                            coef=self.game_state['crash_point'],
                            game_id=next_game_id
                        )
                        # Очищаем ставки для нового раунда
                        self.game_state['bets'] = []
                
                elif self.game_state['status'] == 'running':
                    elapsed = current_time - self.game_state['start_time']
                    current_multiplier = 1.0 + (0.05 * elapsed) * (1.0 + elapsed * 0.08)
                    self.game_state['current_multiplier'] = float(f"{current_multiplier:.2f}")
                    
                    if self.game_state['current_multiplier'] >= self.game_state['crash_point']:
                        # Вызываем end_game перед изменением статуса
                        await self.end_game()
                        self.game_state['next_game_time'] = current_time + 5
                
                elif self.game_state['status'] == 'crashed':
                    remaining = int(self.game_state['next_game_time'] - current_time)
                    self.game_state['countdown'] = max(0, remaining)
                    
                    if current_time >= self.game_state['next_game_time']:
                        self.game_state['status'] = 'waiting'
                        self.game_state['next_game_time'] = current_time + 10

                # Отправляем обновления всем клиентам через game_update
                await self.channel_layer.group_send(
                    "crash_game",
                    {
                        "type": "game_update",
                        "state": self.game_state
                    }
                )
                
                # Регулируем частоту обновлений
                if self.game_state['status'] == 'running':
                    await asyncio.sleep(0.02)  # Частые обновления во время игры
                else:
                    await asyncio.sleep(0.1)  # Более редкие обновления в других состояниях
                
            except Exception as e:
                logger.error(f"Error in game loop: {e}")
                await asyncio.sleep(1) 

    async def end_game(self):
        try:
            total_bets = sum(bet['amount'] for bet in self.game_state['bets'])
            total_payouts = sum(
                bet['amount'] * bet['cashout_multiplier'] 
                for bet in self.game_state['bets'] 
                if bet.get('cashout_multiplier')
            )
            
            casino_profit = total_bets - total_payouts

            # Сохраняем результат игры
            await sync_to_async(GameResult.objects.create)(
                round_number=self.game_state['game_id'],
                multiplier=Decimal(str(self.game_state['crash_point'])),
                casino_profit=Decimal(str(casino_profit))
            )

            self.game_state['status'] = 'crashed'
            await self.channel_layer.group_send(
                "crash_game",
                {
                    "type": "game_update",
                    "state": self.game_state
                }
            )
        except Exception as e:
            logger.error(f"Error in end_game: {e}") 