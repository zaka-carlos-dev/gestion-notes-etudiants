from flask import Flask, render_template, request, redirect, session, send_file
from flask_sqlalchemy import SQLAlchemy
import os
import pandas as pd
from io import BytesIO

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bts_ida_v4.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'bts_ida_2026_final'
db = SQLAlchemy(app)

ADMIN_USER="admin"
ADMIN_PASS="ida2026"

MATIERES = {
    "francais": {"nom": "Français", "coef": 2},
    "anglais": {"nom": "Anglais", "coef": 2},
    "maths": {"nom": "Maths", "coef": 3},
    "economie": {"nom": "Economie", "coef": 2},
    "gestion": {"nom": "Gestion", "coef": 2},
    "droit": {"nom": "Droit", "coef": 1},
    "entrepreneuriat": {"nom": "Entrepreneuriat", "coef": 1},
    "algo": {"nom": "Algo", "coef": 3},
    "langage": {"nom": "Langages évolués", "coef": 3},
    "devweb": {"nom": "Dev Web", "coef": 4},
    "bdd": {"nom": "BDD", "coef": 3},
    "archi": {"nom": "Archi", "coef": 2},
    "se": {"nom": "SE", "coef": 2},
    "merise": {"nom": "Etude de Cas", "coef": 8},
}
TOTAL_COEF = 38

class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False, unique=True)
    classe = db.Column(db.String(20), default="BTS 1 IDA")
    francais = db.Column(db.Float, default=0)
    anglais = db.Column(db.Float, default=0)
    maths = db.Column(db.Float, default=0)
    economie = db.Column(db.Float, default=0)
    gestion = db.Column(db.Float, default=0)
    droit = db.Column(db.Float, default=0)
    entrepreneuriat = db.Column(db.Float, default=0)
    algo = db.Column(db.Float, default=0)
    langage = db.Column(db.Float, default=0)
    devweb = db.Column(db.Float, default=0)
    bdd = db.Column(db.Float, default=0)
    archi = db.Column(db.Float, default=0)
    se = db.Column(db.Float, default=0)
    merise = db.Column(db.Float, default=0)

    def moyenne(self):
        total = self.francais*2 + self.anglais*2 + self.maths*3 + self.economie*2 + self.gestion*2 + self.droit*1 + self.entrepreneuriat*1 + self.algo*3 + self.langage*3 + self.devweb*4 + self.bdd*3 + self.archi*2 + self.se*2 + self.merise*8
        return total / TOTAL_COEF

with app.app_context():
    db.create_all()

def get_classement():
    etudiants = Etudiant.query.all()
    sorted_et = sorted(etudiants, key=lambda x: x.moyenne(), reverse=True)
    result = []
    for i, e in enumerate(sorted_et):
        moy = e.moyenne()
        result.append({"id": e.id, "nom": e.nom, "moyenne": moy, "rang": i+1, "decision": "Admis en BTS 2" if moy>=10 else "Ajourné", "mention": "TB" if moy>=16 else "B" if moy>=14 else "AB" if moy>=12 else "Passable" if moy>=10 else "Insuff", "obj": e})
    return result

@app.route('/')
def index():
    classement = get_classement()
    total = len(classement)
    taux = sum(1 for e in classement if e["moyenne"]>=10)/total*100 if total>0 else 0
    moy_classe = sum(e["moyenne"] for e in classement)/total if total>0 else 0
    meilleure = classement[0]["moyenne"] if total>0 else 0
    return render_template('index.html', etudiants=classement, total=total, taux=taux, moy_classe=moy_classe, meilleure=meilleure)

@app.route('/add', methods=['POST'])
def add():
    nom = request.form['nom'].strip()
    if Etudiant.query.count()>=35 and not Etudiant.query.filter_by(nom=nom).first():
        return "Classe pleine 35 max", 400
    e = Etudiant.query.filter_by(nom=nom).first()
    if not e:
        e = Etudiant(nom=nom, classe=request.form['classe'])
        db.session.add(e)
    e.francais=float(request.form['francais'] or 0); e.anglais=float(request.form['anglais'] or 0); e.maths=float(request.form['maths'] or 0); e.economie=float(request.form['economie'] or 0); e.gestion=float(request.form['gestion'] or 0); e.droit=float(request.form['droit'] or 0); e.entrepreneuriat=float(request.form['entrepreneuriat'] or 0); e.algo=float(request.form['algo'] or 0); e.langage=float(request.form['langage'] or 0); e.devweb=float(request.form['devweb'] or 0); e.bdd=float(request.form['bdd'] or 0); e.archi=float(request.form['archi'] or 0); e.se=float(request.form['se'] or 0); e.merise=float(request.form['merise'] or 0)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    e=Etudiant.query.get(id)
    if e: db.session.delete(e); db.session.commit()
    return redirect('/')

@app.route('/admin', methods=['GET','POST'])
def admin_login():
    if request.method=='POST' and request.form['username']==ADMIN_USER and request.form['password']==ADMIN_PASS:
        session['admin']=True
        return redirect('/admin/dashboard')
    return render_template('admin_login.html')

@app.route('/admin/dashboard')
def admin_dash():
    if not session.get('admin'): return redirect('/admin')
    return render_template('admin_dashboard.html', etudiants=get_classement())

@app.route('/admin/export')
def export():
    if not session.get('admin'): return redirect('/admin')
    data=[{"Nom":e["nom"],"Moyenne":round(e["moyenne"],2),"Rang":e["rang"],"Decision":e["decision"]} for e in get_classement()]
    df=pd.DataFrame(data)
    out=BytesIO(); df.to_excel(out,index=False); out.seek(0)
    return send_file(out, download_name="BTS_IDA.xlsx", as_attachment=True)

@app.route('/admin/logout')
def logout():
    session.pop('admin',None); return redirect('/')

application=app
if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT",5000)))
