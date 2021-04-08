from flask import Flask, render_template, url_for, request, redirect, flash, current_app
from flaskext.mysql import MySQL
import pymysql.cursors
import datetime
import os


app = Flask(__name__)
app.secret_key = 'secret'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_DB'] = 'dictionary'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''

mysql = MySQL(app, cursorclass=pymysql.cursors.DictCursor)
# pymysql for list dictionary

@app.route('/', methods=['GET', 'POST'])
def index():
    user_response = ''
    if request.method == 'POST':
        user_input = request.form['word']
        if user_input == '':
            flash('Please add valid  inputs', 'danger')
        else:
            conn = mysql.get_db()
            cur = conn.cursor()
            cur.execute('select meaning from word where word=%s', (user_input))
            rv = cur.fetchall()
            if(len(rv) > 0):
                user_response = rv[0]['meaning']
            else:
                user_response = "The word cannot be found in this dictionary, please try again with another word"
    return render_template("index.html", user_response = user_response)

@app.route('/dashboard')
def dashboard():
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute('select * from word')
    rv = cur.fetchall()
    cur.close()
    return render_template("dashboard.html", words=rv)

@app.route('/word/<id>')
def word_details(id):
    word_id = id
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute('select * from word where id=%s', (word_id))
    rv = cur.fetchall()
    word_details = rv[0]
    cur.close()
    return render_template("word_details.html", word=word_details)

@app.route('/word/<id>/update', methods=['POST'])
def word_update(id):
    word_id = id
    word_word = request.form['word']
    word_meaning = request.form['meaning']
    if word_word == '' or word_meaning == '':
        flash('Please provide valid input', 'danger')
        return redirect(url_for('word_details', id=word_id))
    else:
        conn = mysql.get_db()
        cur = conn.cursor()
        cur.execute('update word set word=%s, meaning=%s where id=%s', (word_word, word_meaning, word_id))
        conn.commit()
        cur.close()

        flash('Word successfully updated', 'success')

        return redirect(url_for('dashboard'))
  

@app.route('/word/create', methods=['GET', 'POST'])
def word_create():
    if request.method == 'GET':
        return render_template('word_create.html')
    else: 
        word_word = request.form['word']
        word_meaning = request.form['meaning']
        if word_word == '' or word_meaning == '':
            flash('Please provide valid input', 'danger')
            return redirect(url_for('word_create'))
        else:
            conn = mysql.get_db()
            cur = conn.cursor()
            cur.execute('insert into word(word, meaning) values(%s, %s)', (word_word, word_meaning))
            conn.commit()
            cur.close()
            
            flash('Word successfully created', 'success')

            return redirect(url_for('dashboard'))


@app.route('/word/<id>/delete', methods=['POST'])
def word_delete(id):
    word_id = id
    conn = mysql.get_db()
    cur = conn.cursor()
    cur.execute('delete from word where id=%s', (word_id))
    conn.commit()
    cur.close()

    flash('Word successfully deleted', 'success')

    return redirect(url_for('dashboard'))

@app.route('/add_image', methods=['POST', 'GET'])
def add_image():
    if request.method == 'GET':
        return render_template('add_image.html')
    else:
        image = request.files['img']
        if image:
            filepath = os.path.join(current_app.root_path, 'static/images/logo.png')
            image.save(filepath)
            flash('Image successfully uploaded', 'success')
            return redirect(url_for('dashboard'))

        else:
            flash('Please upload a valid file and try again', 'danger')

if __name__ == "__main__":
    app.run(debug=True)


