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
async def start_game(sid, players, dice, sides):
    try:
        games[sid] = FunctionalGame(players, dice, sides, sid)
        # This emits an event from the server to the client
        mat = games[sid].connection_mat
        new_mat = games[sid].new_connection_mat
        await sio.emit('worlds', games[sid].world_list)
        await sio.emit('dice', games[sid].dice_combos)
        await sio.emit('connection_matrices', [mat.tolist(), new_mat.tolist()])
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
