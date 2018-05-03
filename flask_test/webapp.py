from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Lock
import redis
import json
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
async_mode = None
socketio = SocketIO(app, async_mode=async_mode)
thread = None


redis_config={
'redis_host':"139.198.4.56",
'redis_port':6379,
'redis_password':'LtmJ16w9lZ',
'timeout':100,
}


@app.route('/')
def index():
    return render_template('index.html')

def background_thread():
    """持续发送当前的爬取数据"""
    redis_client = redis.Redis(host=redis_config['redis_host'], port=redis_config['redis_port'],
                                    password=redis_config['redis_password'])
    crawler_sub=redis_client.pubsub()
    crawler_sub.subscribe('weibo_gp')
    print('开始监听！')
    for item in crawler_sub.listen():
        if item['type'] != 'message':
            continue
        meta = str(item['data'], encoding='utf-8')
        meta=json.loads(meta)
        print('监听到：%s' % meta)
        socketio.emit('crawl data',{'data': str(meta)})
        print('emit')

@socketio.on('my broadcast event')
def test_message(message):
    emit('my response', {'data': message['data']}, broadcast=True)

@socketio.on('connect')
def test_connect():
    print('begin connect')
    global thread
    thread = socketio.start_background_task(target=background_thread)
    print('right')


@socketio.on('my event')
def handle_my_custom_event(json):
    print('my responseing' + str(json))

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app,debug=True)