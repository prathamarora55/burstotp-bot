from flask import Flask, request, jsonify, send_from_directory
import requests, os

app = Flask(__name__, static_folder='static')

BURST_KEY  = 'AK_f0573508039744f7b5ccd522afbb369f'
SPEEDZ_KEY = 'AK_MhaEcEVHiKYyBEvyy-wW7yWwn8YVNeub'
BURST_BASE  = 'http://burstotpapi.qd.je:8080'
SPEEDZ_BASE = 'https://tubesave.in'

session = requests.Session()
session.trust_env = False  # ignore proxy env vars

def proxy(base, key, path, method, body=None, params=None):
    url = base + path
    headers = {
        'X-API-Key': key,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'User-Agent': 'BurstOTP-Client/1.0'
    }
    try:
        if method == 'GET':
            r = session.get(url, headers=headers, params=params, timeout=30)
        else:
            r = session.post(url, headers=headers, json=body, timeout=30)
        try:
            data = r.json()
        except Exception:
            data = {'raw': r.text, 'status': r.status_code}
        return jsonify(data), r.status_code
    except requests.exceptions.Timeout:
        return jsonify({'error': 'API timeout after 30s'}), 504
    except requests.exceptions.ConnectionError as e:
        return jsonify({'error': f'Connection failed: {str(e)}'}), 502
    except Exception as e:
        return jsonify({'error': f'Unexpected: {str(e)}'}), 500

@app.route('/burst/<path:path>', methods=['GET','POST'])
def burst(path):
    body = request.get_json(silent=True)
    params = request.args.to_dict()
    return proxy(BURST_BASE, BURST_KEY, '/'+path, request.method, body, params)

@app.route('/speedz/<path:path>', methods=['GET','POST'])
def speedz(path):
    body = request.get_json(silent=True)
    return proxy(SPEEDZ_BASE, SPEEDZ_KEY, '/'+path, request.method, body)

# Debug endpoint - test connectivity directly
@app.route('/debug')
def debug():
    results = {}
    try:
        r = session.get(BURST_BASE + '/api/v1/me',
                       headers={'X-API-Key': BURST_KEY}, timeout=30)
        results['burst'] = {'status': r.status_code, 'body': r.text[:200]}
    except Exception as e:
        results['burst'] = {'error': str(e)}
    try:
        r = session.get(SPEEDZ_BASE + '/api/v1/me',
                       headers={'X-API-Key': SPEEDZ_KEY}, timeout=30)
        results['speedz'] = {'status': r.status_code, 'body': r.text[:200]}
    except Exception as e:
        results['speedz'] = {'error': str(e)}
    return jsonify(results)

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
