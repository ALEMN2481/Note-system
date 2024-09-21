from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from myproject.auth import login_required
from myproject.db import get_db

bp = Blueprint('students', __name__)

@bp.route('/')
def index():
    
    
    db = get_db()
    posts = db.execute(
        'SELECT students.id, name, birth_date, phone, nacional_id'
        ' FROM students p JOIN user u ON p.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('students/index.html', posts=posts)

@bp.route('/create', methods=('GET', 'POST'))
@login_required

def create():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        phone = request.form['phone']
        nacional_id = request.form['nacional_id']
        error = None

        if not name:
            error = 'Name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO students (name, birth_date, phone, nacional_id)'
                ' VALUES (?, ?, ?)',
                (name, birth_date, phone, nacional_id, g.user['id'])
            )
            db.commit()
            return redirect(url_for('students.index'))

    return render_template('students/create.html')

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, name, birth_date, phone, nacional_id'
        ' FROM students p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        phone = request.form['phone']
        nacional_id = request.form['nacional_id']
        error = None

        if not name:
            error = 'name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE students SET name = ?, birth_date = ?, phone = ?, nacional_id = ? '
                ' WHERE id = ?',
                (name, birth_date, phone, nacional_id, id)
            )
            db.commit()
            return redirect(url_for('students.index'))

    return render_template('students/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM students WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('students.index'))