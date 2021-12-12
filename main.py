import sympy.core.add
from flask import Flask, render_template, request
import psycopg2
import numpy
from sympy import *

r = Symbol('r')
#colocar a senha do banco de dados
db = psycopg2.connect(host="localhost", user="postgres", password="", database="maximoseminimosdb", port=5432)


class Embalagem:
    def __init__(self, custo_material_tampa, custo_material, volume):
        self.volume = volume
        self.h = self.volume / (numpy.pi * r**2)
        self.custo_material_tampa = custo_material_tampa
        self.custo_material = custo_material
        self.custo_tampa_total = self.custo_material_tampa * r**2 * numpy.pi
        self.custo_base_total = self.custo_material * r**2 * numpy.pi
        self.custo_lateral_total = self.custo_material * 2 * r * self.h * numpy.pi
        self.custo_total = self.custo_tampa_total + self.custo_base_total + self.custo_lateral_total
        self.derivada_custo_total = self.custo_total.diff()
        self.eq_derivada_igual_zero = Eq(self.derivada_custo_total, 0)




app = Flask(__name__)

@app.route("/resultado", methods=["POST"])
def resultado():

    volume = float(request.form["volume"])
    custo_material = float(request.form["custo_material"])
    custo_material_tampa = float(request.form["custo_material_tampa"])
    embalagem = Embalagem(custo_material_tampa, custo_material, volume)

    valor_raio = solve(embalagem.eq_derivada_igual_zero, r)
    raio_real = []
    for raio in valor_raio:
        if type(raio) == sympy.core.numbers.Float:
            raio_real.append(raio)
    custo = []
    for raio_melhor in raio_real:
        custo.append(embalagem.custo_total.subs(r, raio_melhor))

    aux = 0
    for busca in custo:
        if busca == min(custo):
            break
        aux = aux + 1
    valor_altura = embalagem.volume / (numpy.pi * raio_real[aux] * raio_real[aux])
    diametro = 2 * raio_real[aux]

    cursor = db.cursor()



    sql2 = """INSERT INTO Embalagem(volume, preco_material, preco_material_tampa, diametro, altura, custo)
                VALUES ("""+str(volume)+""", """+str(custo_material)+""", """+str(custo_material_tampa)+""", """+str(diametro)+""", """+str(valor_altura)+""", """+str(min(custo))+""")"""
    try:
        cursor.execute(sql2)
        db.commit()

    except:
        db.rollback()
        print("error")
    db.close()

    return render_template("resultado.html", altura=valor_altura, diametro_final=diametro, menor_custo=min(custo))


@app.route("/")
def dados():
    return render_template("getdados.html")

app.run()
