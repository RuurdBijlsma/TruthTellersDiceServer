import numpy as np
import socketio
from aiohttp import web
from FunctionalGame import FunctionalGame

# create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*', logger=True)
app = web.Application()
sio.attach(app)
# app = socketio.WSGIApp(sio)

games = {}


# Events are sent from the web client to this server
@sio.event
async def start_game(sid, players, dice, sides, strategy):
    try:
        print(f"Starting game with {players} players, {dice} dice, {sides} sides, strategy = {strategy}")
        # TODO make use of strategy in functional game
        # TODO get bids history made per player
        games[sid] = FunctionalGame(players, dice, sides)
        game = games[sid]
        game.strategies[0] = strategy
        game.strategy_per_player[0] = strategy
        while len(game.players) > 1:
            game.playround()

        matrices = list(map(
            lambda x: list(map(lambda y: y.tolist(), x)),
            game.connection_mathistory
        ))
        common_knowledge = list(map(
            lambda x: list(map(lambda y: y.tolist(), x)),
            game.logic_commonknowledgehistory
        ))
        data = {
            "worlds": game.world_listhistory,
            "matrices": matrices,
            "dice": game.dicehistory,
            "common_knowledge": common_knowledge,
            "players": game.playershistory,
            "beliefs": game.logic_beliefshistory,
            "bids": game.bidshistory,
            "losers": game.losingplayers,
            "strategies": game.strategy_per_player,
        }

        await sio.emit('game_data', data, sid)
    except Exception as e:
        print(e)  # Events are sent from the web client to this server


@sio.event
async def simulate_games(sid, players, dice, sides, strategy, iterations=100):
    try:
        print(f"Simulating games with {players} players, {dice} dice, {sides} sides, strategy = {strategy}")
        winners = np.zeros(players)
        for i in range(iterations):
            game = FunctionalGame(players, dice, sides)
            game.strategies[0] = strategy
            while len(game.players) > 1:
                game.playround()
            winning_player = game.playershistory[len(game.playershistory) - 1]
            winners[winning_player[0]] += 1

        await sio.emit('simulation_data', winners.tolist(), sid)
    except Exception as e:
        print(e)


@sio.event
def connect(sid, environ):
    print('connect sid:', sid)


@sio.event
def disconnect(sid):
    games.pop(sid)
    print('disconnect sid:', sid)


if __name__ == '__main__':
    web.run_app(app, port=5000)
