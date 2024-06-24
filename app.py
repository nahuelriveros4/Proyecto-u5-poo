from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import random


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Sucursal,  Repartidor, Paquete, Transporte

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/acceso')
def acceso():
    sucursales = Sucursal.query.all()
    return render_template('acceso.html', sucursales=sucursales)

@app.route('/seleccionar_sucursal', methods=['GET','POST'])
def seleccionar_sucursal():
    if request.method == 'POST':
        sucursal_id = request.form.get('sucursales')
        return redirect(url_for('acceso_gestion', sucursal_id=sucursal_id))

@app.route('/acceso_gestion/<int:sucursal_id>')
def acceso_gestion(sucursal_id):
    sucursal = Sucursal.query.get(sucursal_id)
    return render_template('acceso_gestion.html', sucursal= sucursal)

#REGISTRO PAQUETES 
@app.route('/registrar_paquete/<int:sucursal_id>', methods=['GET','POST'])
def registrar_paquete(sucursal_id):
    sucursal= Sucursal.query.get(sucursal_id)
    if request.method == 'POST':
        peso = request.form['peso']
        nomdestinatario = request.form['nomdestinatario']
        dirdestinatario = request.form['dirdestinatario']
        observaciones = request.form.get('observaciones')

        if not peso or not nomdestinatario or not dirdestinatario:
            return render_template('error.html', error="Por favor ingrese los datos requeridos" , sucursal=sucursal )
        else:
            # Generar un número de envío único
            numeroenvio = random.randint(100000, 999999)
            while Paquete.query.filter_by(numeroenvio=numeroenvio).first():
                numeroenvio = random.randint(100000, 999999)
            
            nuevo_paquete = Paquete(
                numeroenvio=numeroenvio,
                peso=float(peso),
                nomdestinatario=nomdestinatario,
                dirdestinatario=dirdestinatario,
                entregado=False,
                idsucursal=sucursal_id,
                observaciones = observaciones
            )
            
            db.session.add(nuevo_paquete)
            db.session.commit()
            flash(f'Paquete registrado exitosamente, N° de envio: {numeroenvio}', 'success')
            return redirect(url_for('registrar_paquete', sucursal_id=sucursal_id))
    else:
        return render_template('registrar_paquete.html', sucursal=sucursal)

#REGISTRO SALIDA DE TRANSPORTE
@app.route('/registrar_salida/<int:sucursal_id>')
def registrar_salida_transporte(sucursal_id):
    sucursalOrigen = Sucursal.query.get(sucursal_id)
    sucursales = Sucursal.query.filter(Sucursal.id != sucursal_id).all()  # Filtrar la sucursal de origen
    return render_template('registrar_salida.html', sucursales=sucursales, sucursalOrigen=sucursalOrigen)

@app.route('/seleccionar_sucursal2/<int:sucursalOrigen_id>', methods=['GET','POST'])
def seleccionar_sucursal2(sucursalOrigen_id):
    if request.method == 'POST':
        sucursal_idDESTINO = request.form.get('sucursales')
        return redirect(url_for('seleccionar_paquetes', sucursal_idDestino=sucursal_idDESTINO, sucursal_idOrigen = sucursalOrigen_id))

@app.route('/seleccionar_paquetes/<int:sucursal_idDestino>/<int:sucursal_idOrigen>')
def seleccionar_paquetes(sucursal_idDestino,sucursal_idOrigen):
    sucursaldestino = Sucursal.query.get(sucursal_idDestino)
    sucursalOrigen = Sucursal.query.get(sucursal_idOrigen)
    # Obtener los paquetes que no han sido entregados y que no tienen repartidor asignado
    paquetes = Paquete.query.filter_by(entregado=False, idrepartidor=None, idsucursal = sucursal_idOrigen, idtransporte=None).all()
    return render_template('seleccionar_paquetes.html', sucursalDestino= sucursaldestino, sucursalOrigen=sucursalOrigen, paquetes=paquetes)

@app.route('/seleccion_paquetes/<int:sucursal_idDestino>/<int:sucursal_idOrigen>', methods=['GET', 'POST'])
def seleccion_paquetes(sucursal_idDestino,sucursal_idOrigen):
    sucursaldestino = Sucursal.query.get(sucursal_idDestino)
    sucursalOrigen = Sucursal.query.get(sucursal_idOrigen)
    if request.method == 'POST':
        paquetes_ids = request.form.getlist('paquetes')
        numero_transporte = request.form['numero_transporte']
        if not numero_transporte or not paquetes_ids :
            return render_template('error2.html', error="Por favor ingrese los datos requeridos" , sucursalDestino= sucursaldestino, sucursalOrigen=sucursalOrigen )
        else:
                # Crear el nuevo transporte
            fecha_hora_salida = datetime.now()
            fecha_hora_salida = fecha_hora_salida.replace(second=0, microsecond=0)
            nuevo_transporte = Transporte(
            numerotransporte=numero_transporte,
            fechahorasalida=fecha_hora_salida,
            idsucursal=sucursal_idDestino)
            db.session.add(nuevo_transporte)
            db.session.commit()

            # Asignar el ID del transporte a los paquetes seleccionados
            for paquete_id in paquetes_ids:
                paquete = Paquete.query.get(paquete_id)
                paquete.idtransporte = nuevo_transporte.id
                db.session.add(paquete)
        
                db.session.commit()

                flash('Transporte registrado y paquetes asignados correctamente.', 'success')
                return redirect(url_for('seleccionar_paquetes', sucursal_idDestino = sucursal_idDestino,sucursal_idOrigen=sucursal_idOrigen))  

#REGISTRO LLEGADA DE TRANSPORTE
@app.route('/registrar_llegada/<int:sucursal_id>')
def registrar_llegada_transporte(sucursal_id):
    sucursal = Sucursal.query.get(sucursal_id)
    Transportes = Transporte.query.filter_by(fechahorallegada=None, idsucursal=sucursal_id).all()
    return render_template('registrar_llegada.html', Transportes = Transportes, sucursal=sucursal)

@app.route('/registrarTransporte/<int:sucursal_id>', methods=['GET', 'POST'])
def regristroTransporte(sucursal_id):
    sucursal = Sucursal.query.get(sucursal_id)
    if request.method == 'POST':
        transportesLlegados_ids = request.form.getlist('transportes')

        if not transportesLlegados_ids :
            return render_template('error3.html', error="Por favor ingrese los datos requeridos" ,  sucursal=sucursal )
        else:
            
            fecha_hora_llegada = datetime.now()
            fecha_hora_llegada = fecha_hora_llegada.replace(second=0, microsecond=0)

            for transporte_id in transportesLlegados_ids:
                transporte = Transporte.query.get(transporte_id)
                transporte.fechahorallegada = fecha_hora_llegada
                db.session.add(transporte)
        
                db.session.commit()

                flash('Transporte registrado correctamente.', 'success')
                return redirect(url_for('registrar_llegada_transporte', sucursal_id = sucursal_id)) 



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)