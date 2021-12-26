"""
GIW 2021-22
Práctica 7
Grupo 9
Autores: Sergio Arroyo Galán, Víctor Fresco Perales, Hugo García González, Miguel Ángel Portocarrero Sánchez y Diego Andrés Ramón Sanchis

Sergio Arroyo Galán, Víctor Fresco Perales, Hugo García González, Miguel Ángel Portocarrero Sánchez 
y Diego Andrés Ramón Sanchis declaramos que esta solución es fruto exclusivamente
de nuestro trabajo personal. No hemos sido ayudados por ninguna otra persona ni hemos
obtenido la solución de fuentes externas, y tampoco hemos compartido nuestra solución
con nadie. Declaramos además que no hemos realizado de manera deshonesta ninguna otra
actividad que pueda mejorar nuestros resultados ni perjudicar los resultados de los demás.
"""
import json
from typing import List
from flask import Flask, request, session, render_template
app = Flask(__name__)

claves = ["nombre", "numero_alumnos", "horario"]
clavesHorario =["dia", "hora_inicio", "hora_final"]
asignaturas = []

def buscarAsignaturaPorId(id):
    i = 0
    while i < len(asignaturas):
        if asignaturas[i].get("id") == id:
            return asignaturas[i]
        i = i + 1
    return -1

@app.route('/asignaturas', methods=['GET', 'DELETE', 'POST'])
def get_asignaturas () :    
    # Consultar las asignaturas ====================================================
    if request.method == 'GET':
        supported_args = ['alumnos_gte', 'page', 'per_page']
        result = {"asignaturas": []}
        # Comprobar que los parámetros de la petición son válidos
        for arg in request.args.keys():
            if arg not in supported_args:
                return ('', 400)

        # Comprobar que si está presente "page" o "per_page", están ambos argumentos y no sólo uno de ellos
        if (request.args.get('page') or request.args.get('per_page')) and not (request.args.get('page') and request.args.get('per_page')):
            return ('', 400)

        # Obtener asignaturas
        if request.args.get('alumnos_gte'):
            if not request.args.get('alumnos_gte').isdigit():
                return '', 400

            gte = int(request.args.get('alumnos_gte'))
            for a in asignaturas:
                if a.get('numero_alumnos') >= gte:
                    result.get('asignaturas').append('/asignaturas/'+str(a.get('id')))

        else:
            for a in asignaturas:
                result.get('asignaturas').append('/asignaturas/'+str(a.get('id')))

        # Paginar resultados
        if request.args.get('page') and request.args.get('per_page'):
            if not request.args.get('page').isdigit() or not request.args.get('per_page').isdigit():
                return ('', 400)

            per_page = int(request.args.get('per_page'))
            page = int(request.args.get('page'))-1

            # Comprobar que los valores de page son correctos
            if page < 0 or page >= len(result['asignaturas'])/per_page:
                return ({"asignaturas":[]}, 206)

            # Mete en paginated_result una lista de listas de asignaturas de tamaño per_page
            paginated_result = [result['asignaturas'][i:i+per_page] for i in range(0, len(result['asignaturas']), per_page)]
            result_page = {"asignaturas":[]}
            result_page['asignaturas'] = paginated_result[page]

            # Comprobar si se devuelve todo el contenido disponible o no
            if len(result_page['asignaturas']) == len(asignaturas):
                code = 200
            else:
                code = 206

            return (result_page, code)
        else:
            if len(result['asignaturas']) == len(asignaturas):
                code = 200
            else:
                code = 206

            return (result, code)
    
    # Añadir asignaturas nuevas =====================================================
    elif request.method == 'POST':
        data = request.get_json()
        
        # comprobamos que los campos introducidos son correctos, si no retornamos bad request
        if (data == None) or (data.get("nombre") == None) or (data.get("numero_alumnos") == None) or (data.get("horario") == None) or (len(data) != 3) or (type(data.get("nombre")) != str) or (type(data.get("horario")) != list) or (type(data.get("numero_alumnos")) != int) or (data.get("numero_alumnos") < 0):
            return ('',400)
        
        for i in data.get("horario"):
           
            if (i.get("dia") == None) or (i.get("hora_inicio") == None) or (i.get("hora_final") == None) or (len(i) != 3) or (type(i.get("dia")) != str) or  (type(i.get("hora_inicio")) != int) or (type(i.get("hora_final")) != int):
                return ('',400)

        # En caso de que los campos sean correctos registramos la nueva asignaturas
        if len(asignaturas) == 0:
            id = 0
        else:
            id = asignaturas[-1].get("id") + 1

        asignaturas.append({"id": id, "nombre": data["nombre"], "numero_alumnos": data["numero_alumnos"], "horario": data["horario"]})
        
        return {"id": id}, 201  # en caso de que los campos introducidos son correctos devolvemos el id de la asignatura creada

    # Borrar todas las asignaturas registradas ============================================
    elif request.method == 'DELETE':  
        asignaturas.clear()
        return ('',204)
    else:
        return ('', 405)

@app.route('/asignaturas/<int:id>', methods=['GET', 'DELETE', 'PUT', 'PATCH'])
def get_asignatura(id) :    
    # Consultar asignatura =========================================
    if request.method == 'GET':
        ok = False
        for a in asignaturas:
            if (a.get('id') == id):
                return(json.dumps(a,indent=2), 200)
                ok = True
        if not ok:
            return('', 404)
        
    # Borrar asignatura ==============================================
    elif request.method == 'DELETE':  
        ok = False
        for a in asignaturas:
            if (a.get('id') == id):
                asignaturas.remove(a)
                return('', 204)
                ok = True
        if not ok:
            return('', 404)  
    # Actualizacion completa ===========================================
    elif request.method == 'PUT':
        asig = buscarAsignaturaPorId(id)
        if asig == -1:
            return "", 404
        else:
            detalles_asignatura = request.get_json()
            if detalles_asignatura == None:
                return "", 400
                
            # Comprobar que estan todos los campos en la peticion
            for c in claves:
                if c not in detalles_asignatura.keys():
                    return "", 400
            # Comprobar que no hay ningún campo distinto de los permitidos
            for key in detalles_asignatura:
                if key not in claves:
                    return "", 400
            # Comprobar que los tipos son correctos
            if not isinstance(detalles_asignatura["nombre"], str):
                return "", 400
            if not isinstance(detalles_asignatura["numero_alumnos"], int):
                return "", 400
            if not isinstance(detalles_asignatura["horario"], list):
                return "", 400

            # Comprobar los campos del horario de la misma forma
            for value in detalles_asignatura["horario"]:
                for key in value.keys():
                    if key not in clavesHorario:
                        return "", 400
                for c in clavesHorario:
                    if c not in value.keys():
                        return "", 400
                if not isinstance(value["dia"], str):
                    return "", 400
                if not isinstance(value["hora_inicio"], int):
                    return "", 400
                if not isinstance(value["hora_final"], int):
                    return "", 400

            asig["id"] = id
            asig["nombre"] = detalles_asignatura["nombre"]
            asig["numero_alumnos"] = detalles_asignatura["numero_alumnos"]
            asig["horario"] = detalles_asignatura["horario"]

            return "", 200    
    #Actualizacion parcial
    elif request.method == 'PATCH':
        asig = buscarAsignaturaPorId(id)
        print("Asignatura antes de modificar:", asig)
        if asig == -1:
            return "", 404
        else:
            detalles_asignatura = request.get_json()
            for key in detalles_asignatura:
                if key not in claves:
                    return "", 400
            for k,v in detalles_asignatura.items():
                asignaturas[asig["id"]][k] = v
            print("Asignatura modificada: ", asignaturas[0])
            return "", 200
    
@app.route('/asignaturas/<int:numero>/horario', methods=['GET'])
def get_asignaturas_schedule(numero):
    result = {'horario':[]}
    if request.method == "GET":
        ok = False
        for a in asignaturas:
            if (a.get('id') == numero):
                result['horario'] = a.get('horario')
                return(result, 200)
                ok = True
        if not ok:
            return('', 404)

class FlaskConfig:
    """Configuración de Flask"""
    # Activa depurador y recarga automáticamente
    ENV = 'development'
    DEBUG = True
    TEST = True
    # Imprescindible para usar sesiones
    SECRET_KEY = "giw2021&!_()"
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


if __name__ == '__main__':
    app.config.from_object(FlaskConfig())
    app.run()

