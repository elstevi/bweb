import json
import os
from bapiclient import client
from flask import Flask, jsonify, redirect, render_template, request, url_for
from libbhyve.custom_t import DISK_TYPES, NIC_TYPES, BACKING_TYPES

# Where are our jinja templates?
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.route('/')
def vm_manager():
    if request.args.get('message') != None:
        message = request.args.get('message')
    else:
        message = None
    vnc_host = request.headers.get('X-Forwarded-Server')
    vms = client.get_all_vms()
    vms_detail = []
    for vm in vms:
        vms_detail.append(client.get_vm_details(vm))
    return render_template('vm_manager.html', vms=vms_detail, vnc_host=vnc_host, message=message)

@app.route('/vm/<vm_name>/<action>')
def vm_action(vm_name, action):
    output = client.vm_action(vm_name, action)
    return jsonify(output), 200

def request_to_json(request):
    newvm = {}
    newvm['network'] = []
    newvm['disk'] = []
    lookup_net = {}
    lookup_disk = {}
    i = 0
    for key in request.form.keys():
        if key[:3] == "net":

            src_index = int(key[4])
            new_key = key[6:]
            if lookup_net.get(src_index) is None:
                # we do not have this in a lookup table yet
                newvm['network'].append({new_key: request.form[key]})
                lookup_net[src_index] = len(newvm['network']) - 1
            else:
                newvm['network'][lookup_net.get(src_index)][new_key] = request.form[key]
        elif key[:3] == "dsk":

            src_index = int(key[4])
            new_key = key[6:]
            if lookup_disk.get(src_index) is None:
                # we do not have this in a lookup table yet
                newvm['disk'].append({new_key: request.form[key]})
                lookup_disk[src_index] = len(newvm['disk']) - 1
            else:
                newvm['disk'][lookup_disk.get(src_index)][new_key] = request.form[key]
        else:
            newvm[key] = request.form[key]
        i+=1
    return newvm

def error_page(summary, status_code, error):
    return render_template('error', summary=summary, status_code=status_code, error=error)

@app.route('/vm/edit/<vm_name>', methods=['GET', 'POST'])
def edit(vm_name):
    if request.method == 'GET':
        vm = client.get_vm_details(vm_name)
        return render_template('create_vm.html', DISK_TYPES=DISK_TYPES, NIC_TYPES=NIC_TYPES, BACKING_TYPES=BACKING_TYPES, hosts=client.get_hosts(), vm=vm)
    elif request.method == 'POST':
        newvm = request_to_json(request)
        host = client.get_vm_details(vm_name)['host']
        vm = client.edit_host(host, newvm)
        return redirect(url_for('vm_manager', message='VM updated'))

@app.route('/vm/create', methods=['GET', 'POST'])
def create():
    if request.method == 'GET':
        return render_template('create_vm.html', DISK_TYPES=DISK_TYPES, NIC_TYPES=NIC_TYPES, BACKING_TYPES=BACKING_TYPES, hosts=client.get_hosts())
    elif request.method == 'POST':
        newvm = request_to_json(request)
        r = client.new_host(request.form['host'], newvm)
        return redirect(url_for('vm_manager', message='VM created'))

if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=True, port=8000)
