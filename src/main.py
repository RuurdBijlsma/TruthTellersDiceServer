import socketio
from aiohttp import web
from game import Game

# create a Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*', logger=False)
app = web.Application()
sio.attach(app)
# app = socketio.WSGIApp(sio)
game = Game(sio)


# Events are sent from the web client to this server
@sio.event
async def do_stuff(sid, number):
    result = game.do_stuff(number)
    # This emits an event from the server to the client
    await sio.emit('done_stuff', result)


@sio.event
def connect(sid, environ):
    print('connect sid:', sid)


@sio.event
def disconnect(sid):
    print('disconnect sid:', sid)


if __name__ == '__main__':
    web.run_app(app, port=5000)
