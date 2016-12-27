from flask import render_template, jsonify, abort, url_for, redirect, json, request
from app import app
from app import models
from app import db

@app.route('/task', methods=['POST'])
def task_post():
	title = request.form['title'].strip()
	if not title or len(title) > models.Task.MAX_TITLE_LENGTH:
		abort(400)
	description = request.form['description'].strip()
	parent_id = request.form['parent'].strip()
	parent = models.Section.query.get(parent_id)
	if parent is None:
		abort(400)
	t = models.Task(title, description, None, 0, parent)
	db.session.add(t)
	db.session.commit()
	return redirect(url_for('section', sec_id=parent.id))


@app.route('/task/<int:task_id>', methods=['GET','POST'])
def update_task(task_id):
	task = models.Task.query.get(task_id)
	if task is None:
		abort(404)
	if request.method == 'POST':
		if 'delete-task' in request.form and request.form['delete-task'] == 'delete':
			parent_id = task.parent.id
			db.session.delete(task)
			db.session.commit()
			return redirect(url_for('section', sec_id=parent_id))
		elif 'update-task' in request.form and request.form['update-task'] == 'update':
			if 'title' in request.form:
				title = request.form['title'].strip()
				if title and len(title) <= models.Task.MAX_TITLE_LENGTH:
					task.title = title
				else:
					abort(400)
			if 'confidence' in request.form:
				confidence = int(request.form['confidence'])
				if confidence >= 0 and confidence <= 10:
					task.confidence = confidence
				else:
					abort(400)
			if 'description' in request.form:
				task.description = request.form['description'].strip()
			db.session.commit()
			return render_template('task.html', task=task)
		else:
			abort(400)
	else:
		return render_template('task.html', task=task)
