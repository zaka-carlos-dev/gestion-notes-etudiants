from flask import Flask, render_template, request, redirect
app = Flask(__name__)
etudiants = [{"nom": "Zaka Carlos", "matiere": "Dev Web", "note": "16/20"}]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        nom = request.form.get('nom')
        matiere = request.form.get('matiere')
        note = request.form.get('note')
        if nom and matiere and note:
            etudiants.append({'nom': nom, 'matiere': matiere, 'note': note})
        return redirect('/')
    return render_template('index.html', etudiants=etudiants)

@app.route('/delete/<int:id>')
def delete(id):
    if 0 <= id < len(etudiants):
        etudiants.pop(id)
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)