from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'v2-babi-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes_v2.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    classe = db.Column(db.String(50), default='Classe A')
    matiere = db.Column(db.String(50), nullable=False)
    note = db.Column(db.Float, nullable=False)

def mention(moy):
    if moy >= 16: return "Très Bien"
    if moy >= 14: return "Bien"
    if moy >= 12: return "Assez Bien"
    if moy >= 10: return "Passable"
    return "Insuffisant"

@app.route('/')
def index():
    notes = Note.query.all()
    grouped = defaultdict(list)
    for n in notes: grouped[n.nom].append(n)
    eleves = []
    for nom, lst in grouped.items():
        moy = sum(x.note for x in lst)/len(lst)
        eleves.append({'nom':nom,'classe':lst[0].classe,'notes':lst,'moyenne':round(moy,2),'mention':mention(moy),'statut':'Admis' if moy>=10 else 'Redouble'})
    eleves.sort(key=lambda x: x['moyenne'], reverse=True)
    for i,e in enumerate(eleves): e['rang']=i+1
    total=len(eleves)
    moy_classe=round(sum(e['moyenne'] for e in eleves)/total,1) if total else 0
    taux=round(len([e for e in eleves if e['moyenne']>=10])/total*100) if total else 0
    meilleure=eleves[0]['moyenne'] if eleves else 0
    meilleur_nom=eleves[0]['nom'] if eleves else "-"
    return render_template('index.html', eleves=eleves, total=total, moy_classe=moy_classe, taux=taux, meilleure=meilleure, meilleur_nom=meilleur_nom)

@app.route('/add', methods=['POST'])
def add():
    db.session.add(Note(nom=request.form['nom'], classe=request.form['classe'], matiere=request.form['matiere'], note=float(request.form['note'])))
    db.session.commit()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete(id):
    Note.query.filter_by(id=id).delete()
    db.session.commit()
    return redirect('/')

with app.app_context(): db.create_all()
if __name__ == '__main__': app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
