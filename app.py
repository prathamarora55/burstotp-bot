from flask import Flask, request, jsonify, send_from_directory
import requests, os

app = Flask(__name__, static_folder='static')

BURST_KEY   = 'AK_f0573508039744f7b5ccd522afbb369f'
SPEEDZ_KEY  = 'AK_MhaEcEVHiKYyBEvyy-wW7yWwn8YVNeub'
BURST_BASE  = 'http://burstotpapi.qd.je:8080'
SPEEDZ_BASE = 'https://tubesave.in'
WORKER_URL  = 'https://raspy-glade-355a.pratham-arora55.workers.dev'

def proxy_via_worker(base, key, path, method, body=None, params=None):
    target = base + path
    if params:
        qs = '&'.join(f'{k}={v}' for k,v in params.items())
        target += ('&' if '?' in target else '?') + qs
    try:
        opts = {
            'method': method,
            'headers': {'X-API-Key': key, 'Content-Type': 'application/json'},
            'timeout': 30
        }
        if body and method == 'POST':
            opts['json'] = body
        r = requests.request(
            method,
            WORKER_URL,
            params={'target': target},
            headers={'X-API-Key': key, 'Content-Type': 'application/json'},
            json=body if method == 'POST' else None,
            timeout=30
        )
        try:
            return jsonify(r.json()), r.status_code
        except:
            return jsonify({'raw': r.text}), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 502

@app.route('/burst/<path:path>', methods=['GET','POST'])
def burst(path):
    body = request.get_json(silent=True)
    params = request.args.to_dict()
    return proxy_via_worker(BURST_BASE, BURST_KEY, '/'+path, request.method, body, params)

@app.route('/speedz/<path:path>', methods=['GET','POST'])
def speedz(path):
    body = request.get_json(silent=True)
    return proxy_via_worker(SPEEDZ_BASE, SPEEDZ_KEY, '/'+path, request.method, body)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
