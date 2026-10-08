from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bts_ida.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Etudiant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(100))
    filiere = db.Column(db.String(100), default='IDA')
    matiere = db.Column(db.String(200))
    note = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    etudiants = Etudiant.query.all()
    if etudiants:
        total = len(etudiants)
        admis = len([e for e in etudiants if e.note >= 10])
        taux = (admis/total*100) if total>0 else 0
        moyenne_classe = sum(e.note for e in etudiants)/total
        meilleure = max(e.note for e in etudiants)
    else:
        taux = 0
        moyenne_classe = 0
        meilleure = 0
    return render_template('index.html', etudiants=etudiants, taux_admission=taux, moyenne_classe=moyenne_classe, meilleure_moyenne=meilleure)

@app.route('/add', methods=['POST'])
def add():
    nom = request.form['nom']
    classe = request.form['classe']
    filiere = request.form.get('filiere', 'IDA')
    matiere = request.form['matiere']
    note = float(request.form['note'])
    e = Etudiant(nom=nom, classe=classe, filiere=filiere, matiere=matiere, note=note)
    db.session.add(e)
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    e = Etudiant.query.get(id)
    db.session.delete(e)
    db.session.commit()
    return redirect('/')

application = app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
