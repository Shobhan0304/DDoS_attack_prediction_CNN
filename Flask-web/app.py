from flask import Flask, render_template, request
import torch, time
from model import Multiclass  # Assuming your model class is defined in a separate file

app = Flask(__name__)

# Load the pre-trained model, specifying map_location='cpu'
#model = Multiclass()
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

def predict(input_tensor):
    #input_tensor = torch.FloatTensor(param).unsqueeze(0).unsqueeze(2)
    with torch.no_grad():
        
        output = model(input_tensor)
        _, prediction = torch.max(output, 1)
    return prediction.item()

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None
    categories = ['CON', 'ECO', 'FIN', 'INT', 'MAS', 'NRS', 'REQ', 'RST', 'TST', 'URP']
    param = {}

    if request.method == 'POST':
        param['stime'] = time.time()
        param['proto_number'] = int(request.form['proto_number'])

        saddr = request.form['saddr']
        param['saddr'] = conv_ip_addr(saddr)

        daddr = request.form['daddr']
        param['daddr'] = conv_ip_addr(daddr)

        param['pkts'] = float(request.form['pkts'])
        param['bytes'] = float(request.form['bytes'])
        param['ltime'] = float(request.form['ltime'])
        param['seq'] = float(request.form['seq'])
        param['dur'] = float(request.form['dur'])
        param['mean'] = float(request.form['mean'])
        param['stddev'] = float(request.form['stddev'])
        param['sum'] = float(request.form['sum'])
        param['min'] = float(request.form['min'])
        param['max'] = float(request.form['max'])
        param['spkts'] = float(request.form['spkts'])
        param['dpkts'] = float(request.form['dpkts'])
        param['sbytes'] = float(request.form['sbytes'])
        param['dbytes'] = float(request.form['dbytes'])
        param['rate'] = float(request.form['rate'])
        param['srate'] = float(request.form['srate'])
        param['drate'] = float(request.form['drate'])
        param['TnBPSrcIP'] = float(request.form['TnBPSrcIP'])
        param['TnBPDstIP'] = float(request.form['TnBPDstIP'])
        param['TnP_PSrcIP'] = float(request.form['TnP_PSrcIP'])
        param['TnP_PDstIP'] = float(request.form['TnP_PDstIP'])
        param['TnP_PerProto'] = float(request.form['TnP_PerProto'])
        param['TnP_Per_Dport'] = float(request.form['TnP_Per_Dport'])
        param['AR_P_Proto_P_SrcIP'] = float(request.form['AR_P_Proto_P_SrcIP'])
        param['AR_P_Proto_P_DstIP'] = float(request.form['AR_P_Proto_P_DstIP'])
        param['N_IN_Conn_P_DstIP'] = float(request.form['N_IN_Conn_P_DstIP'])
        param['N_IN_Conn_P_SrcIP'] = float(request.form['N_IN_Conn_P_SrcIP'])
        param['AR_P_Proto_P_Sport'] = float(request.form['AR_P_Proto_P_Sport'])
        param['AR_P_Proto_P_Dport'] = float(request.form['AR_P_Proto_P_Dport'])
        param['Pkts_P_State_P_Protocol_P_DestIP'] = float(request.form['Pkts_P_State_P_Protocol_P_DestIP'])
        param['Pkts_P_State_P_Protocol_P_SrcIP'] = float(request.form['Pkts_P_State_P_Protocol_P_SrcIP'])
        state = request.form['state']

        category_mapping = {category: 1 if category == state else 0 for category in categories}
        param['state'] = list(category_mapping.values())
        
        param = scaler(param)
        features = flatten_list(list(param.values()))
        input_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(1)
        # Perform prediction using the username and password
        prediction = predict(input_tensor)
       # prediction = features

    return render_template('index.html', prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)
