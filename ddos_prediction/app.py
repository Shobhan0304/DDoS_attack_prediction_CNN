from flask import Flask, render_template, request, jsonify, send_from_directory
import torch, time, csv, json, os
from model import Multiclass

app = Flask(__name__)

model = torch.load('ddos_cnn_model.pth', map_location=torch.device('cpu'))
model.eval()


def conv_ip_addr(ip_addr):
    ip_addr = ip_addr.replace(':','.')
    temp = ip_addr.split('.')
    op = ''.join(temp)
    if op.isnumeric():
        op = int(op)
    else:
        op = int(op, 16)
    return op

def predict(features):
    with torch.no_grad():
        
        output = model(features)
        _, prediction = torch.max(output, 1)
    
    if prediction.item() == 1:
        output = False
    else:
        output = True
    return output

def scaler(param):
    col_to_scale = ['stime','saddr','daddr', 'pkts', 'bytes', 'ltime', 'dur', 
                'mean', 'stddev', 'sum', 'min', 'max', 'spkts', 'dpkts',
                'sbytes', 'dbytes', 'rate', 'srate', 'drate', 'TnBPSrcIP', 'TnBPDstIP',
                'TnP_PSrcIP', 'TnP_PDstIP', 'TnP_PerProto', 'TnP_Per_Dport',
                'Pkts_P_State_P_Protocol_P_DestIP', 'Pkts_P_State_P_Protocol_P_SrcIP']
    
    mu = [1527873757.053765, 1.1952392039582042e+19, 4666589058.031348, 10.912460622088727, 2039.7210233919004, 1527873770.4945116, 13.440746581030988, 2.943216399274818, 1.072583588831781, 8.878277994752604, 1.4455163774161497, 3.7582167835628426, 10.298676782514264, 0.6137838395744643, 1577.569909442023, 462.15111394987747, 1340.8847058186311, 14.089417154862517, 2.4121117767403315, 54788.991877604625, 63166.10807422942, 782.5447943373591, 927.1824128450522, 990.8376941970496, 904.5027418693775, 920.5686798639387, 775.6257849405106]
    std = [572205.9973862184, 3.6122627915962274e+21, 22687146924.78048, 270.2339174843412, 262984.05756207026, 572205.8152231389, 43.44854860876978, 1.2553351929548489, 0.6500499642489185, 12.518377518098632, 1.2331206655121796, 1.529703797131268, 180.1731664372533, 116.29813071840113, 168492.57358629766, 115835.8709405756, 18513.105320198145, 1697.2273942815184, 141.21188001964003, 1036090.5356344222, 971579.5500858399, 1138.9347563665456, 1141.8676968460732, 3277.83414150737, 1350.2372110997678, 655.730587475891, 615.0606996433498]

    for i in range(len(col_to_scale)):
        param[col_to_scale[i]] = (float(param[col_to_scale[i]]) - mu[i])/std[i]
    
    return param 

def flatten_list(nested_list):
    flattened_list = []
    for item in nested_list:
        if isinstance(item, list):
            flattened_list.extend(flatten_list(item))
        else:
            flattened_list.append(item)
    return flattened_list

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/admin', methods = ['GET'])
def view_tables():
    with open('blacklist_table.csv','r') as file:
        reader = csv.reader(file)
        bl_table = []
        for i in reader:
            bl_table.append(i)
    with open('data_table.csv', 'r') as file:
        reader = csv.reader(file)
        data_table = []
        for i in reader:
            data_table.append(i)
    
    return render_template('admin.html', blacklist_table = bl_table, data_table = data_table)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods = ['POST'])
def upload_file():
    try:
        upload_file = request.files['file']

        
        #print("Received file:", request.files['file'])
        if 'additional_params' in request.form:
            additional_params = json.loads(request.form['additional_params'])
           #additional_params = request.json.get('additional_params', {})
        else:
            additional_params = {
                'stime':time.time(),
                'proto_number':3,
                'saddr':'192.168.100.150',
                'daddr':'127.0.0.1:5000',
                'pkts':2,
                'bytes':172,
                'ltime':1526350331,
                'seq':4283,
                'dur':2.501092,
                'mean':0,
                'stddev':0,
                'sum':0,
                'min':0,
                'max':0,
                'spkts':2,
                'dpkts':0,
                'sbytes':172,
                'dbytes':0,
                'rate':0.399825,
                'srate':0.399825,
                'drate':0,
                'TnBPSrcIP':2328,
                'TnBPDstIP':3182,
                'TnP_PSrcIP':30,
                'TnP_PDstIP':37,
                'TnP_PerProto':78955,
                'TnP_Per_Dport':129,
                'AR_P_Proto_P_SrcIP':1.58971,
                'AR_P_Proto_P_DstIP':0.870395,
                'N_IN_Conn_P_DstIP':20,
                'N_IN_Conn_P_SrcIP':11,
                'AR_P_Proto_P_Sport':0.799651,
                'AR_P_Proto_P_Dport':0.322581,
                'Pkts_P_State_P_Protocol_P_DestIP':37,
                'Pkts_P_State_P_Protocol_P_SrcIP':10,
                'state':[0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
        }

        prediction = False
        with open('blacklist_table.csv', 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if additional_params['saddr'] == row[0]:
                    prediction = True
                    return render_template('result.html', message = 'Error: DDoS Attack Detected')
        ip = additional_params['saddr']

        additional_params['saddr'] = conv_ip_addr(additional_params['saddr'])
        additional_params['daddr'] = conv_ip_addr(additional_params['daddr'])
        additional_params = scaler(additional_params)
        
        features = flatten_list(list(additional_params.values()))
        input_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(1)
        prediction = predict(input_tensor)

        if prediction == True:
            message = 'Error: DDoS Attack Detected'
            with open('blacklist_table.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([ip])
        else:
            message = 'File Uploaded Successfully'
            with open('data_table.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([upload_file.filename, ip])
        
        return render_template('result.html', message = message)
    except Exception as e:
        return render_template('result.html', message = f"Error: {str(e)}")


if __name__ == '__main__':
    app.run(host = '192.168.100.6', port = 5000, debug=True)
            
