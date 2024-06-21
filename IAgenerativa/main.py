from flask import Flask, request, jsonify
import os
import google.generativeai as genai

app = Flask(__name__)


GOOGLE_API_KEY = "AIzaSyBHrA3-wzZygn4s1ewl2Sj73WXb-Re0vag"  # add your GOOGLE API key here
os.environ["GOOGLE_API_KEY"] = GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.8,
    "top_p": 1,
    "top_k": 1,
    "max_output_tokens": 2048,
}

model = genai.GenerativeModel('gemini-pro',generation_config=generation_config)

@app.route('/generate_alert', methods=['POST'])
def generate_alert():
    alerta = request.get_json()

    titulo_prompt = f"Genera un título para una alerta de tipo {alerta['tipo'] }"
    titulo_response = model.generate_content(titulo_prompt)

    texto_informativo_prompt = f"Generame un parrafo informativo sin titiulo para una alerta de {alerta['tipo']}  en {alerta['direccion_limpia']}"
    texto_informativo_response = model.generate_content(texto_informativo_prompt)

    return jsonify({"titulo_alerta": titulo_response.text, "descripcion": texto_informativo_response.text,"fecha_hora": alerta['fecha_y_hora'],"lugar": alerta['direccion_limpia']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2015, debug=False)