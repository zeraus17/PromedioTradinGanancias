from flask import Flask, render_template, request, redirect, url_for
import pytesseract
from PIL import Image
import os

app = Flask(__name__)

# Configura la ruta de Tesseract si es necesario
pytesseract.pytesseract.tesseract_cmd = r'D:/Documents/tesseract.exe'  # Cambia esto a tu ruta de Tesseract

# Calcular las ganancias totales
def CalcularGanancias(Nombre_Moneda, Precio_Compra, Precio_Venta):
    ganancias_totales = 0
    ganancias_por_moneda = {}
    for n, compra, venta in zip(Nombre_Moneda, Precio_Compra, Precio_Venta):
        ganancia = float(venta) - float(compra)
        ganancias_totales += ganancia
        ganancias_por_moneda[n] = ganancia
    return ganancias_totales, ganancias_por_moneda

# Página principal que toma la imagen
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Guardar la imagen subida
        imagen = request.files['imagen']
        imagen_path = os.path.join('uploads', imagen.filename)
        imagen.save(imagen_path)

        # Extraer texto de la imagen
        texto_extraido = pytesseract.image_to_string(Image.open(imagen_path))

        # Procesar el texto extraído para obtener datos (suponiendo que el texto tiene un formato específico)
        datos = procesar_texto(texto_extraido)  # Debes definir esta función para extraer la información necesaria

        Nombre_Moneda = datos['Nombre_Moneda']
        Precio_Compra = datos['Precio_Compra']
        Precio_Venta = datos['Precio_Venta']

        # Calcular ganancias diarias por moneda
        ganancias_totales, ganancias_por_moneda = CalcularGanancias(Nombre_Moneda, Precio_Compra, Precio_Venta)

        # Calcular el monto recomendado para invertir
        objetivo = float(request.form['objetivo'])
        monto_inicial = float(request.form['monto_inicial'])

        if ganancias_totales > 0:
            monto_recomendado = objetivo / ganancias_totales * monto_inicial
        else:
            monto_recomendado = 0

        # Verificar si las ganancias permiten alcanzar el objetivo
        semanas_necesarias = objetivo // ganancias_totales if ganancias_totales > 0 else float('inf')

        return render_template('resultado.html', 
                               objetivo=objetivo, 
                               monto_inicial=monto_inicial,
                               ganancias_totales=ganancias_totales, 
                               semanas_necesarias=semanas_necesarias,
                               ganancias_por_moneda=ganancias_por_moneda,
                               monto_recomendado=monto_recomendado)  # Pasar monto recomendado
    return render_template('index.html')

# Función para procesar el texto extraído de la imagen
def procesar_texto(texto):
    # Aquí debes implementar la lógica para extraer Nombre_Moneda, Precio_Compra y Precio_Venta
    # Por ejemplo, puedes utilizar expresiones regulares o dividir el texto en líneas
    # Asegúrate de devolver un diccionario con las listas necesarias
    # Ejemplo (esto debe adaptarse a tu caso):
    return {
        'Nombre_Moneda': ['MRF', 'DTQ'],  # Estos valores deben ser extraídos de 'texto'
        'Precio_Compra': ['224.84', '201.81'],  # Extraídos también
        'Precio_Venta': ['230.82', '206.80']  # Extraídos también
    }

# Preguntar si desea invertir ahora
@app.route('/invertir', methods=['POST'])
def invertir():
    invertir_ahora = request.form['invertir']
    if invertir_ahora.lower() == 'si':
        return redirect(url_for('select_exchange'))
    return render_template('gracias.html')

# Selección de exchange
@app.route('/exchange', methods=['GET', 'POST'])
def select_exchange():
    exchanges = {
        'Binance': 'https://www.binance.com/en/login',
        'Coinbase': 'https://www.coinbase.com/signin',
        'Kraken': 'https://www.kraken.com/sign-in',
        'Bitfinex': 'https://www.bitfinex.com/sign-in',
        'Huobi': 'https://www.huobi.com/en-us/login/'
    }

    if request.method == 'POST':
        selected_exchange = request.form['exchange']
        if selected_exchange in exchanges:
            return redirect(exchanges[selected_exchange])

    return render_template('exchange.html', exchanges=exchanges)

# Templates para la página
@app.route('/gracias')
def gracias():
    return render_template('gracias.html')

if __name__ == '__main__':
    app.run(debug=True)
