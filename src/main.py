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
        while len(games[sid].players) > 1:
            games[sid].playround()

        matrices = list(map(
            lambda x: list(map(lambda y: y.tolist(), x)),
            games[sid].connection_mathistory
        ))
        common_knowledge = list(map(
            lambda x: list(map(lambda y: y.tolist(), x)),
            games[sid].logic_commonknowledgehistory
        ))
        data = {
            "worlds": games[sid].world_list,
            "matrices": matrices,
            "dice": games[sid].dicehistory,
            "common_knowledge": common_knowledge,
            "players": games[sid].playershistory,
            "beliefs": games[sid].logic_beliefshistory,
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
