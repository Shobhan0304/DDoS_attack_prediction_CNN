from flask import Flask, render_template, request
import torch
from model import Multiclass  # Assuming your model class is defined in a separate file

app = Flask(__name__)

# Load the pre-trained model, specifying map_location='cpu'
model = Multiclass()
model = torch.load('ddos_cnn_model.pth', map_location=torch.device('cpu'))
model.eval()

def predict(username, password):
    # Perform some processing or prediction based on username and password
    # For simplicity, let's just concatenate them and use as features
    features = [float(ord(char)) for char in username + password]
    with torch.no_grad():
        input_tensor = torch.FloatTensor(features).unsqueeze(0).unsqueeze(2)
        output = model(input_tensor)
        _, prediction = torch.max(output, 1)
    return prediction.item()

@app.route('/', methods=['GET', 'POST'])
def index():
    prediction = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Perform prediction using the username and password
        prediction = predict(username, password)

    return render_template('index.html', prediction=prediction)


if __name__ == '__main__':
    app.run(debug=True)
