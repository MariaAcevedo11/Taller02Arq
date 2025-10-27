from flask import Flask
from routes.pokeneas_routes import pokenea_bp

app = Flask(__name__)

# Registrar las rutas
app.register_blueprint(pokenea_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
