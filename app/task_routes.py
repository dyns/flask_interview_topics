import os
from flask import render_template, jsonify, abort, url_for, redirect, json
from app import app
from flask import request
from app import models
from app import db
from datetime import datetime

@app.route('/task', methods=['POST'])
def task_post():
	title = request.form['title'].strip()
	description = request.form['description'].strip()
	parent_id = request.form['parent']
	parent = models.Section.query.get(parent_id)
	t = models.Task(title, description, None, 0, parent)
	db.session.add(t)
	db.session.commit()
	return redirect(url_for('index'))


@app.route('/task/<int:task_id>', methods=['GET','POST'])
def update_task(task_id):
	task = models.Task.query.get(task_id)
	if task is None:
		abort(404)
	if request.method == 'POST':
		if 'delete-task' in request.form and request.form['delete-task'] == 'delete':
			db.session.delete(task)
			db.session.commit()
			return redirect(url_for('index'))
		elif 'update-task' in request.form and request.form['update-task'] == 'update':
			if 'title' in request.form:
				if request.form['title'].strip():
					task.title = str(request.form['title'].strip())
				else:
					abort(400)
			if 'confidence' in request.form:
				task.confidence = int(request.form['confidence'])
			if 'description' in request.form:
				task.description = str(request.form['description'])
			db.session.commit()
			return render_template('task.html', task=task)
		else:
			abort(400)
	else:
		return render_template('task.html', task=task)
