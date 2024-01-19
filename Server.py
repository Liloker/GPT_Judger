from upload import *


LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 5431


@app.route('/api')
def hello_world():
    output('[-]:hello_world接口被调用了')
    return 'Hello World!'


if __name__ == '__main__':

    app.run(host=LISTEN_HOST, port=LISTEN_PORT, debug=True)










