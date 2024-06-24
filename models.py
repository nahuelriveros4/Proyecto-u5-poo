from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Sucursal(db.Model):
    __tablename__ = 'sucursal'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True , nullable=False)
    provincia = db.Column(db.String(30), nullable=False)
    localidad = db.Column(db.String(30), nullable=False)
    direccion= db.Column(db.String(60), nullable=False)
    idrepartidor = db.relationship('Repartidor', backref='sucursal', cascade="all,delete-orphan")
    paquetes = db.relationship('Paquete', backref='sucursal', cascade="all,delete-orphan")
    transportes = db.relationship('Transporte', backref='sucursal', cascade="all,delete-orphan")

class Repartidor(db.Model):
    __tablename__ = 'repartidor'
    id =db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    dni = db.Column(db.String(20), unique=True, nullable=False)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    paquetes = db.relationship('Paquete', backref='repartidor', cascade="all,delete-orphan")

class Paquete(db.Model):
    __tablename__ = 'paquete'
    id = db.Column(db.Integer, primary_key=True)
    numeroenvio = db.Column(db.Integer, unique=True, nullable=False)
    peso = db.Column(db.Float, nullable=False)
    nomdestinatario = db.Column(db.String(20), nullable=False)
    dirdestinatario= db.Column(db.String(30), nullable=False)
    entregado = db.Column(db.Boolean, nullable=False)
    observaciones = db.Column(db.String(50))
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    idtransporte = db.Column(db.Integer, db.ForeignKey('transporte.id'))
    idrepartidor= db.Column(db.Integer, db.ForeignKey('repartidor.id'))

class Transporte(db.Model):
    __tablename__ = 'transporte'
    id = db.Column(db.Integer, primary_key=True)
    numerotransporte = db.Column(db.Integer, unique=True, nullable=False)
    fechahorasalida= db.Column(db.DateTime)
    fechahorallegada= db.Column(db.DateTime)
    idsucursal = db.Column(db.Integer, db.ForeignKey('sucursal.id'))
    paquetes = db.relationship('Paquete', backref='transporte', cascade="all,delete-orphan")

