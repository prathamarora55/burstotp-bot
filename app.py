from flask import Flask, request, jsonify, send_from_directory
import requests, os

app = Flask(__name__, static_folder='static')

BURST_KEY  = 'AK_f0573508039744f7b5ccd522afbb369f'
SPEEDZ_KEY = 'AK_MhaEcEVHiKYyBEvyy-wW7yWwn8YVNeub'
BURST_BASE  = 'http://burstotpapi.qd.je:8080'
SPEEDZ_BASE = 'https://tubesave.in'

def proxy(base, key, path, method, body=None, params=None):
    url = base + path
    headers = {'X-API-Key': key, 'Content-Type': 'application/json'}
    try:
        if method == 'GET':
            r = requests.get(url, headers=headers, params=params, timeout=30)
        else:
            r = requests.post(url, headers=headers, json=body, timeout=30)
        try:
            return jsonify(r.json()), r.status_code
        except Exception:
            return jsonify({'error': r.text}), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'API timeout — try again'}), 504
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': 'Cannot reach API: ' + str(e)}), 502
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/burst/<path:path>', methods=['GET','POST'])
def burst(path):
    body = request.get_json(silent=True)
    params = request.args.to_dict()
    return proxy(BURST_BASE, BURST_KEY, '/'+path, request.method, body, params)

@app.route('/speedz/<path:path>', methods=['GET','POST'])
def speedz(path):
    body = request.get_json(silent=True)
    return proxy(SPEEDZ_BASE, SPEEDZ_KEY, '/'+path, request.method, body)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
