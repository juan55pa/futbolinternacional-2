#--------------------------------------------------------------------
# Instalar con pip install Flask
from flask import Flask, request, jsonify, render_template
#from flask import request

# Instalar con pip install flask-cors
from flask_cors import CORS

# Instalar con pip install mysql-connector-python
import mysql.connector

# Si es necesario, pip install Werkzeug
from werkzeug.utils import secure_filename


import os
import time
#--------------------------------------------------------------------



app = Flask(__name__)
CORS(app)  # Esto habilitará CORS para todas las rutas

#--------------------------------------------------------------------
class Futbol():
    #----------------------------------------------------------------
    # Constructor de la clase
    def __init__(self, host, user, password, database):
        # Primero, establecemos una conexión sin especificar la base de datos
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        self.cursor = self.conn.cursor()

        # Intentamos seleccionar la base de datos
        try:
            self.cursor.execute(f"USE {database}")
        except mysql.connector.Error as err:
            # Si la base de datos no existe, la creamos
            if err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
                self.cursor.execute(f"CREATE DATABASE {database}")
                self.conn.database = database
            else:
                raise err

        # Una vez que la base de datos está establecida, creamos la tabla si no existe
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS futbolintenacional (
            Id_Jugador INT(4) AUTO_INCREMENT PRIMARY KEY,
            Jugador VARCHAR(26) NOT NULL,  
            Equipo  VARCHAR(27) NOT NULL,                                                  
            Posicion  varchar(20) NOT NULL,          
            Liga VARCHAR(27) NOT NULL,                            
            valor INT(10) NOT NULL) ''')
        self.conn.commit()

        # Cerrar el cursor inicial y abrir uno nuevo con el parámetro dictionary=True
        self.cursor.close()
        self.cursor = self.conn.cursor(dictionary=True)
        
    #----------------------------------------------------------------
    # Método para agregar un jugador a la base de datos
    def agregar_Jugador(self, Id_Jugador, Jugador, Equipo, Posicion, Liga, valor):
        sql = "INSERT INTO futbolintenacional (Id_Jugador, Jugador, Equipo, Posicion, Liga, valor) VALUES (%s, %s, %s, %s, %s, %s)"
        valores = (Id_Jugador, Jugador, Equipo, Posicion, Liga, valor)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return True


    #----------------------------------------------------------------
    def consultar_Jugador(self, Id_Jugador):
        # Consultamos un producto a partir de su código
        self.cursor.execute(f"SELECT * FROM futbolintenacional WHERE Id_Jugador = {Id_Jugador}")
        return self.cursor.fetchone()

    #----------------------------------------------------------------
    def modificar_jugador(self, Id_Jugador, nueva_Jugador, nueva_Equipo, nueva_Posicion, nueva_Liga, nueva_valor):
        sql = "UPDATE futbolintenacional SET Jugador = %s, Equipo = %s, Posicion = %s, Liga = %s, valor = %s WHERE Id_Jugador = %s"
        valores = (nueva_Jugador, nueva_Equipo, nueva_Posicion, nueva_Liga, nueva_valor, Id_Jugador)
        self.cursor.execute(sql, valores)
        self.conn.commit()
        return self.cursor.rowcount > 0

    #----------------------------------------------------------------
    def listar_Jugador(self):
        self.cursor.execute("SELECT * FROM futbolintenacional")
        futbolintenacional = self.cursor.fetchall()
        return futbolintenacional

        
    #----------------------------------------------------------------
    def eliminar_Jugador(self, Id_jugador):
        # Eliminamos un producto de la tabla a partir de su código
        self.cursor.execute(f"DELETE FROM futbolintenacional WHERE Id_jugador = {Id_jugador}")
        self.conn.commit()
        return self.cursor.rowcount > 0
    #----------------------------------------------------------------
    def mostrar_Jugador(self, Id_Jugador):
        # Mostramos los datos de un jugador a partir de su código
        Jugador = self.consultar_Jugador(Id_Jugador)
        if Jugador:
            print("-" * 40)
            print(f"Id_Jugador.....: {Jugador['Id_Jugador']}")
            print(f"Jugador: {Jugador['Jugador']}")
            print(f"Equipo...: {Jugador['Equipo']}")
            print(f"Posicion.....: {Jugador['Posicion']}")
            print(f"Liga.....: {Jugador['Ligal']}")
            print(f"valorr..: {Jugador['valor']}")
            print("-" * 40)
        else:
            print("Jugador no encontrado.")
            

#--------------------------------------------------------------------
# Cuerpo del programa
#--------------------------------------------------------------------
# Crear una instancia de la clase Catalogo

futbol = Futbol(host='localhost', user='root', password='', database='miapp')
#catalogo = Catalogo(host='arielfsp.mysql.pythonanywhere-services.com', user='arielfsp', password='1234qw12', database='arielfsp$miapp')







#--------------------------------------------------------------------
@app.route("/futbolintenacional", methods=["GET"])
def listar_jugadores():
    jugadores = futbol.listar_Jugador()  # Corregir el nombre del método
    return jsonify(jugadores)
#--------------------------------------------------------------------
@app.route("/futbolintenacional/<int:Id_Jugador>", methods=["GET"])
def mostrar_jugador(Id_Jugador):
    jugador = futbol.consultar_Jugador(Id_Jugador)  # Corregir el nombre del método
    if jugador:
        return jsonify(jugador), 201
    else:
        return "Jugador no encontrado", 404    


#--------------------------------------------------------------------
@app.route("/futbolintenacional", methods=["POST"])
def agregar_Jugador():
    #Recojo los datos del form
    Id_Jugador = request.form['Id_Jugador']
    Jugador = request.form['Jugador']
    Equipo = request.form['Equipo']
    Posicion = request.form['Posicion']
    Liga = request.form['Liga']  
    valor = request.form['valor']    

    if futbol.agregar_Jugador(Id_Jugador, Jugador, Equipo, Posicion, Liga, valor):
       
        return jsonify({"mensaje": "jugador agregado"}), 201
    else:
        return jsonify({"mensaje": "jugador ya existe"}), 400

#--------------------------------------------------------------------
@app.route("/futbolintenacional/<int:Id_Jugador>", methods=["PUT"])
def modificar_jugador(Id_Jugador):
    #Recojo los datos del form
    nueva_Jugador = request.form.get("Jugador")
    nueva_Equipo= request.form.get("Equipo")
    nueva_Posicion = request.form.get("Posicion")
    nueva_Liga = request.form.get("Liga")
    nueva_valor = request.form.get("valor")
    
    if futbol.modificar_jugador(Id_Jugador, nueva_Jugador, nueva_Equipo, nueva_Posicion, nueva_Liga, nueva_valor):
        return jsonify({"mensaje": "jugador modificado"}), 200
    else:
        return jsonify({"mensaje": "jugador no encontrado"}), 403
#--------------------------------------------------------------------
@app.route("/futbolintenacional/<int:Id_Jugador>", methods=["DELETE"])
def eliminar_jugador(Id_Jugador):
    if futbol.eliminar_Jugador(Id_Jugador):
        return jsonify({"mensaje": "Jugador eliminado"}), 200
    else:
        return jsonify({"mensaje": "Error al eliminar el Jugador"}), 500
#--------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)