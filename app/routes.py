import os
from flask import render_template, jsonify, abort, url_for, redirect, json
from app import app
from flask import request
from app import models
from app import db
from datetime import datetime

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'POST':
		title = request.form['title']
		title = title.strip()

		if not title:
			abort(400)

		s = models.Section(title)

		if 'description' in request.form:
			s.description = request.form['description'].strip()

		if 'parent-id' in request.form:
			parent_id = request.form['parent-id'].strip()
			try:
				parent_id = int(parent_id)
			except ValueError:
				abort(400)
			else:
				parent = models.Section.query.get(parent_id)
				if parent:
					s.parent = parent
				else:
					abort(404)

		db.session.add(s)
		db.session.commit()
		return redirect(url_for('index'))

	elif request.method == 'GET':
		top_sections = models.Section.query.filter(models.Section.parent == None).all()
		add_progress(top_sections)
		return render_template('index.html', sections=top_sections)

def add_progress(sections):
	for section in sections:
		set_section_progress(section)


def set_section_progress(section):
	total_tasks = 0
	completed_tasks = 0

	total_tasks = len(section.tasks) * 10
	for task in section.tasks:
			completed_tasks += task.confidence

	if section.sub_sections:
		for sub_s in section.sub_sections:
			sub_completed_tasks, sub_total_tasks = set_section_progress(sub_s)
			total_tasks += sub_total_tasks
			completed_tasks += sub_completed_tasks

	total_tasks = total_tasks if total_tasks > 0 else 1
	section.total_tasks = total_tasks
	section.completed_tasks = completed_tasks

	return (completed_tasks, total_tasks)

@app.route('/task', methods=['POST'])
def task_post():
	title = request.form['title'].strip()
	description = request.form['description'].strip()
	due_date = None
	if 'due-date' in request.form and request.form['due-date'].strip():
		try:
			due_date = datetime.strptime(request.form['due-date'].strip(), '%Y-%m-%d')
		except ValueError:
			abort(400)

	parent_id = request.form['parent']
	parent = models.Section.query.get(parent_id)
	t = models.Task(title, description, due_date, 0, parent)
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
		if 'confidence' in request.form:
			task.confidence = int(request.form['confidence'])
		if 'title' in request.form:
			task.title = str(request.form['title'])
		if 'description' in request.form:
			task.description = str(request.form['description'])
		if 'due-date' in request.form:
			due_date = request.form['due-date']
			try:
				due_date = datetime.strptime(due_date, '%Y-%m-%d')
			except ValueError:
				task.due_date = None
			else:
				task.due_date = due_date
		db.session.commit()
		return redirect(url_for('index'))
	else:
		return render_template('task.html', task=task)

@app.route('/s')
def sections():
	sections = models.Section.query.all()
	return jsonify([s.json() for s in sections])

@app.route('/s/<int:sec_id>', methods=['GET','POST'])
def section(sec_id):
	sec = models.Section.query.get(sec_id)
	if not sec:
		abort(404)

	if request.method == 'POST':
		if 'delete-sec' in request.form and request.form['delete-sec'] == 'delete':
			remove_children(sec)
			db.session.commit()
			return redirect(url_for('index'))
	else:
		add_progress([sec])
		return render_template('section.html', sec=sec)

def remove_children(sec):
	for task in sec.tasks:
		db.session.delete(task)
	for sub_s in sec.sub_sections:
		remove_children(sub_s)
	db.session.delete(sec)

@app.route('/getting')
def getting_interview():
	return render_template('getting-the-interview.html')

@app.route('/load')
def load_default():
	SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
	json_url = os.path.join(SITE_ROOT, "static/", "def.json")
	data = json.load(open(json_url))
	for s in data['sections']:
		db.session.add(add_json(s))
	db.session.commit()
	return redirect(url_for('index'))

def add_json(section_json):
	sub_sections = []
	for s_s in section_json['sub-sections']:
		sub_sections.append(add_json(s_s))

	sec = models.Section(section_json['title'], section_json['description'], None, sub_sections)
	# db.session.add(sec)

	for t in section_json['tasks']:
		description = t['description'] if 'description' in t else ''
		task = models.Task(t['title'], description, None, 0, sec)
		# db.session.add(task)

	return sec
