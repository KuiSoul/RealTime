import uuid
import tornado.ioloop
import tornado.web
import tornado.websocket

class CorsWebSocketHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

class CorsHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.set_header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept")

    def options(self):
        # Respond to CORS preflight requests
        self.set_status(204)
        self.finish()

class EchoWebSocket(CorsWebSocketHandler):
    waiters = set()
    user = None

    def open(self):
        EchoWebSocket.waiters.add(self)
        print("WebSocket opened")

    def on_close(self):
        try:
            EchoWebSocket.waiters.remove(self)
        except ValueError:
            pass
        print("WebSocket closed")

    def on_message(self, message):
        if message.startswith('user:'):
            print('User logged: '+message)
            self.user = message.split(':')[1]
            self.user_uuid = str(uuid.uuid4())
            return
        if message == 'refresh' and self.user is not None:
            print('refreshing...')
            for w in EchoWebSocket.waiters:
                if w != self and w.user == self.user:
                    w.write_message('refresh')
    def options(self):
        # Respond to CORS preflight requests
        self.set_status(204)
        self.finish()


application = tornado.web.Application([
    (r'/ws', EchoWebSocket),
    (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': '/path/to/static/files'}),
    (r'/cors', CorsHandler),
])

if __name__ == '__main__':
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()