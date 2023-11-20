import requests
import json, time, os

script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, 'example_file.txt')

upload_url = "http://127.0.0.1:5000/upload"

ips = ["192.168.1.1", "199.199.199.199", "192.168.1.3"]

for i in ips:
    additional_parameters = {
        'stime': time.time(),
        'proto_number': 3,
        'saddr': i,
        'daddr': '127.0.0.1:5000',
        'pkts': 15,
        'bytes': 900,
        'ltime': 1528099351.94587,
        'seq': 109223,
        'dur': 13.657889,
        'mean': 3.91046,
        'stddev': 1.367803,
        'sum': 11.73138,
        'min': 1.976111,
        'max': 4.884452,
        'spkts': 15,
        'dpkts': 0,
        'sbytes': 900,
        'dbytes': 0,
        'rate': 1.025049,
        'srate': 1.025049,
        'drate': 0,
        'TnBPSrcIP': 90000,
        'TnBPDstIP': 90000,
        'TnP_PSrcIP': 1500,
        'TnP_PDstIP': 1500,
        'TnP_PerProto': 1500,
        'TnP_Per_Dport': 1500,
        'AR_P_Proto_P_SrcIP': 1.09825,
        'AR_P_Proto_P_DstIP': 1.09825,
        'N_IN_Conn_P_DstIP': 100,
        'N_IN_Conn_P_SrcIP': 100,
        'AR_P_Proto_P_Sport': 1.09827,
        'AR_P_Proto_P_Dport': 1.09825,
        'Pkts_P_State_P_Protocol_P_DestIP': 1500,
        'Pkts_P_State_P_Protocol_P_SrcIP': 1500,
        'state': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    }

    files = {'file': open(file_path, 'rb')}

    payload = {'additional_params': json.dumps(additional_parameters)}

    #headers = {'Content-Type': 'multipart/form-data'}
    response = requests.post(upload_url, data=payload, files=files)
    print("Response:", response.text)
