import csv
import requests
from flask import Flask, render_template

app = Flask(__name__)

# 🔗 TU ENLACE CSV DE GOOGLE SHEETS
URL_MI_GOOGLE_SHEET = "https://docs.google.com/spreadsheets/d/e/2PACX-1vQhDMd-J78JjOXzgPVyFgvEmx6b8MiEO_dFFA5l9B-J9Qde1wWyF69kZRK8MTEFgihVCtsJAr6T4Vqf/pub?output=csv"

def obtener_datos_desde_sheets():
    try:
        respuesta = requests.get(URL_MI_GOOGLE_SHEET)
        respuesta.encoding = 'utf-8'
        
        lineas = respuesta.text.splitlines()
        lector_csv = csv.DictReader(lineas)
        
        platillos = []
        url_portada = None 
        url_logo = None 
        
        for fila in lector_csv:
            fila_limpia = {k.strip().lower().replace('í', 'i').replace('ó', 'o'): v for k, v in fila.items() if k}
            
            # Detectamos las filas de configuración (portada y logo)
            if fila_limpia.get("categoria", "").lower() == "config":
                nombre_config = fila_limpia.get("nombre", "").lower()
                if nombre_config == "portada":
                    url_portada = fila_limpia.get("url imagen", "").strip()
                elif nombre_config == "logo":
                    url_logo = fila_limpia.get("url imagen", "").strip()
                continue 
            
            precio_texto = fila_limpia.get("precio", "0").replace("Q", "").replace("$", "").strip()
            try:
                precio_final = float(precio_texto)
            except ValueError:
                precio_final = 0.0

            platillos.append({
                "categoria": fila_limpia.get("categoria", "Otros").strip(),
                "nombre": fila_limpia.get("nombre", "Platillo sin nombre").strip(),
                "descripcion": fila_limpia.get("descripcion", "").strip(),
                "precio": precio_final,
                "url_imagen": fila_limpia.get("url imagen", "").strip()
            })
        return platillos, url_portada, url_logo
    except Exception as e:
        print(f"⚠️ Error crítico al procesar Google Sheets: {e}")
        return [], None, None

@app.route('/<restaurante_slug>/mesa/<int:numero_mesa>')
def mostrar_menu(restaurante_slug, numero_mesa):
    platillos, foto_portada, foto_logo = obtener_datos_desde_sheets()
    
    # 🌟 CORREGIDO: Nombre de variable unificado y consistente para Python
    categorias_agrupadas = {}
    for p in platillos:
        cat = p["categoria"]
        if cat not in categorias_agrupadas:
            categorias_agrupadas[cat] = []
        categorias_agrupadas[cat].append(p)
    
    nombre_limpio = restaurante_slug.replace("-", " ").title()
        
    return render_template(
        'menu.html', 
        menu_estructurado=categorias_agrupadas, 
        mesa=numero_mesa, 
        nombre_restaurante=nombre_limpio,
        portada_background=foto_portada,
        logo_restaurante=foto_logo 
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')