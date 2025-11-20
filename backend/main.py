# Camada que geerencia o database
from flask import Flask, jsonify
from flask_cors import CORS
from backend.rotas.produto_comprador import produtos_comprador_blueprint
from Trabalho_final_Backend.rotas.vendedor import vendedor_blueprint

app = Flask(__name__)
CORS(app, origins="*")


@app.route("/", methods=["GET"])
def get_autor():
    return jsonify("It's Alive"), 200


app.register_blueprint(produtos_comprador_blueprint)
app.register_blueprint(vendedor_blueprint)
app.run("0.0.0.0", port=8001, debug=False)
