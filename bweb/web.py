import os
from bapiclient import client
from flask import Flask, jsonify, render_template, request

# Where are our jinja templates?
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.route('/')
def vm_list():
    vnc_host = request.headers.get('X-Forwarded-Server')
    vms = client.get_all_vms()
    vms_detail = []
    for vm in vms:
        vms_detail.append(client.get_vm_details(vm))
    return render_template('vm_manager.html', vms=vms_detail, vnc_host=vnc_host)

@app.route('/vm/<vm_name>/<action>')
def vm_action(vm_name, action):
    output = client.vm_action(vm_name, action)
    print output
    try:
        output['error']
        return jsonify(output), 500
    except KeyError:
        return jsonify(output), 200


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=8000)
