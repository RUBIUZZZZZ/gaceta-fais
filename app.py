from flask import Flask, render_template_string, request, redirect, url_for
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
inicializar_db()

# En internet la base de datos se guardará de forma segura en el servidor
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fais_comunidad_v2.db")

def conectar_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_db():
    with conectar_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS avisos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                titulo TEXT NOT NULL,
                contenido TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS respuestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                aviso_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                nombre TEXT NOT NULL,
                comentario TEXT NOT NULL,
                FOREIGN KEY (aviso_id) REFERENCES avisos(id)
            )
        """)
        conn.commit()

# --- PLANTILLA ÚNICA ---
PLANTILLA_GACETA = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FAIS - Comunidades Indígenas y Afromexicanas</title>
    <style>
        body { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f9f9f9; color: #333; margin: 0; padding: 0; }
        .header-banner { width: 100%; max-width: 900px; margin: 0 auto; display: block; }
        .header-banner img { width: 100%; height: auto; display: block; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .container { max-width: 850px; margin: 20px auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border-top: 5px solid #6A1B29; }
        h1 { color: #6A1B29; border-bottom: 2px solid #BC955C; padding-bottom: 10px; font-size: 24px; text-align: center; }
        h2 { color: #6A1B29; font-size: 20px; margin-top: 30px; }
        .box-publicar { background: #fdfdfd; border: 1px solid #e0e0e0; padding: 25px; margin-bottom: 40px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-top: 4px solid #BC955C; }
        .box-publicar label { font-weight: bold; display: block; margin-top: 12px; color: #6A1B29; }
        .box-publicar input, .box-publicar textarea { width: 100%; padding: 10px; margin-top: 5px; box-sizing: border-box; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; }
        .btn-publicar { background-color: #6A1B29; color: white; border: none; padding: 12px; width: 100%; font-weight: bold; border-radius: 4px; cursor: pointer; margin-top: 15px; font-size: 15px; }
        .btn-publicar:hover { background-color: #4A121A; }
        .aviso-card { background: #fdfdfd; border-left: 4px solid #6A1B29; padding: 20px; margin-bottom: 35px; border-radius: 0 8px 8px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05); position: relative; }
        .aviso-header { display: flex; justify-content: space-between; align-items: flex-start; }
        .aviso-fecha { color: #777; font-size: 13px; font-weight: bold; margin-bottom: 5px; }
        .aviso-titulo { color: #6A1B29; font-size: 20px; margin: 0 0 12px 0; font-weight: bold; }
        .aviso-contenido { font-size: 16px; line-height: 1.6; color: #444; margin-bottom: 20px; }
        .btn-borrar { background-color: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: bold; }
        .btn-borrar:hover { background-color: #bd2130; }
        .seccion-respuestas { background: #f5f5f5; padding: 15px; border-radius: 6px; margin-top: 15px; }
        .comentario-item { background: white; padding: 10px 15px; border-radius: 4px; margin-bottom: 10px; border-bottom: 1px solid #e0e0e0; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
        .comentario-autor { font-weight: bold; color: #BC955C; font-size: 14px; }
        .comentario-texto { margin: 5px 0 0 0; font-size: 14px; color: #333; }
        .form-respuesta { margin-top: 15px; display: flex; flex-direction: column; gap: 8px; }
        .input-resp { padding: 8px; border: 1px solid #ccc; border-radius: 4px; font-size: 14px; box-sizing: border-box; }
        .btn-resp { background-color: #BC955C; color: white; padding: 8px 15px; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; align-self: flex-end; }
        .btn-resp:hover { background-color: #9E7B43; }
    </style>
</head>
<body>
    <div class="header-banner">
        <img src="/portada.jpg" alt="Portada Oficial FAIS">
    </div>
    <div class="container">
        <h1>Gaceta Informativa Digital Comunitaria</h1>

        {% if es_admin %}
            <div class="box-publicar">
                <h3 style="margin: 0 0 10px 0; color: #6A1B29; border-bottom: 1px solid #BC955C; padding-bottom: 5px;">🏛️ Panel de Publicación Oficial</h3>
                <form method="POST" action="/publicar">
                    <label for="titulo">Título del Aviso / Convocatoria:</label>
                    <input type="text" name="titulo" placeholder="Ej. Convocatoria a Asamblea General Extraordinaria" required>
                    
                    <label for="contenido">Información detallada para el pueblo:</label>
                    <textarea name="contenido" style="height:120px;" placeholder="Escribe aquí los detalles..." required></textarea>
                    
                    <button class="btn-publicar" type="submit">Publicar Comunicado al Pueblo 🏛️</button>
                </form>
            </div>
        {% endif %}
        
        <h2>📢 Últimos Avisos y Comunicados Oficiales</h2>
        
        {% for aviso in datos_avisos %}
            <div class="aviso-card">
                <div class="aviso-header">
                    <div>
                        <div class="aviso-fecha">📅 Publicado el: {{ aviso['info']['fecha'] }}</div>
                        <div class="aviso-titulo">{{ aviso['info']['titulo'] }}</div>
                    </div>
                    {% if es_admin %}
                        <form method="POST" action="/eliminar/{{ aviso['info']['id'] }}" onsubmit="return confirm('¿Seguro que deseas borrar este aviso?');">
                            <button class="btn-borrar" type="submit">🗑️ Borrar Aviso</button>
                        </form>
                    {% endif %}
                </div>
                <div class="aviso-contenido">{{ aviso['info']['contenido'] }}</div>
                
                <div class="seccion-respuestas">
                    <h4 style="margin: 0 0 10px 0; color: #555;">💬 Respuestas y Dudas de la Comunidad:</h4>
                    {% if aviso['respuestas'] %}
                        {% for resp in aviso['respuestas'] %}
                            <div class="comentario-item">
                                <span class="comentario-autor">👤 {{ resp['nombre'] }}</span> 
                                <span style="font-size: 11px; color:#999;">({{ resp['fecha'] }})</span>
                                <p class="comentario-texto">{{ resp['comentario'] }}</p>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p style="font-size: 13px; color: #777; italic; margin: 5px 0;">No hay respuestas en este comunicado aún.</p>
                    {% endif %}
                    
                    <form class="form-respuesta" method="POST" action="/responder/{{ aviso['info']['id'] }}">
                        <input class="input-resp" type="text" name="nombre" placeholder="Tu nombre o comunidad" required>
                        <input class="input-resp" type="text" name="comentario" placeholder="Escribe tu duda o respuesta aquí..." required>
                        <button class="btn-resp" type="submit">Enviar Respuesta ↩️</button>
                    </form>
                </div>
            </div>
        {% endfor %}
    </div>
</body>
</html>
"""

@app.route("/")
def inicio():
    with conectar_db() as conn:
        avisos = conn.execute("SELECT * FROM avisos ORDER BY id DESC").fetchall()
        datos_avisos = []
        for aviso in avisos:
            respuestas = conn.execute("SELECT * FROM respuestas WHERE aviso_id = ? ORDER BY id ASC", (aviso["id"],)).fetchall()
            datos_avisos.append({"info": aviso, "respuestas": respuestas})
    return render_template_string(PLANTILLA_GACETA, datos_avisos=datos_avisos, es_admin=False)

@app.route("/admin_fais_secreto")
def admin():
    with conectar_db() as conn:
        avisos = conn.execute("SELECT * FROM avisos ORDER BY id DESC").fetchall()
        datos_avisos = []
        for aviso in avisos:
            respuestas = conn.execute("SELECT * FROM respuestas WHERE aviso_id = ? ORDER BY id ASC", (aviso["id"],)).fetchall()
            datos_avisos.append({"info": aviso, "respuestas": respuestas})
    return render_template_string(PLANTILLA_GACETA, datos_avisos=datos_avisos, es_admin=True)

@app.route("/portada.jpg")
def servir_portada():
    return redirect(url_for('static', filename='portada.jpg'))

@app.route("/publicar", methods=["POST"])
def publicar():
    titulo = request.form["titulo"]
    contenido = request.form["contenido"]
    fecha_hoy = datetime.now().strftime("%d/%m/%Y")
    with conectar_db() as conn:
        conn.execute("INSERT INTO avisos (fecha, titulo, contenido) VALUES (?, ?, ?)", (fecha_hoy, titulo, contenido))
        conn.commit()
    return redirect(url_for('admin'))

@app.route("/responder/<int:aviso_id>", methods=["POST"])
def responder(aviso_id):
    nombre = request.form["nombre"]
    comentario = request.form["comentario"]
    fecha_hoy = datetime.now().strftime("%d/%m/%Y %H:%M")
    with conectar_db() as conn:
        conn.execute("INSERT INTO respuestas (aviso_id, fecha, nombre, comentario) VALUES (?, ?, ?, ?)", (aviso_id, fecha_hoy, nombre, comentario))
        conn.commit()
    return redirect(request.referrer or url_for('inicio'))

@app.route("/eliminar/<int:aviso_id>", methods=["POST"])
def eliminar(aviso_id):
    with conectar_db() as conn:
        conn.execute("DELETE FROM respuestas WHERE aviso_id = ?", (aviso_id,))
        conn.execute("DELETE FROM avisos WHERE id = ?", (aviso_id,))
        conn.commit()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    inicializar_db()
    # Cambiado para que corra de forma automática en los servidores de Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
