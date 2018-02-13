from flask import Flask, request, jsonify
import pystache, os

app = Flask(__name__)


@app.errorhandler(404)
def not_found():
    message = {
        'status': 404,
        'message': 'Not Found: ' + request.url,
    }
    resp = jsonify(message)
    resp.status_code = 404

    return resp


@app.route('/')
def index():
    return ''


@app.route('/conf', methods=['POST'])
def config():
    """
    get config info from user input, populate yml template
    """

    cfg = request.form.get('cfg')

    template = \
        open(
            '{}/cfg_template.tmpl'
                .format(os.path.dirname(os.path.realpath(__file__)))
        )

    data = {
        'PID': cfg['pid'],
        'NAME': cfg['name'],
        'DELIM': cfg['delimiter'],
        'CODE_PATH': cfg['code_path'],
        'INPUT_PATH': cfg['input_path'],
        'OUTPUT_PATH': cfg['output_path'],
        'NODE_NAME': cfg['node_name'],
        'HOST_ONE': cfg['host_one'],
        'PORT_ONE': cfg['port_one'],
        'HOST_TWO': cfg['host_two'],
        'PORT_TWO': cfg['port_two'],
        'HOST_THREE': cfg['host_three'],
        'PORT_THREE': cfg['port_three']
    }

    return pystache.render(template, data)


@app.route('/protocol', methods=['POST'])
def protocol():
    """
    get protocol specification from user
    """

    protocol = request.form.get('protocol')

    return protocol
