
from flask import render_template, jsonify, abort, url_for, redirect 
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
		parent_id = request.form['parent-id']
		parent = None
		if parent_id:
			try:
				parent_id = int(parent_id)
			except ValueError:
				abort(400)
			else:
				parent = models.Section.query.get(parent_id)
				if not parent:
					abort(400)
		if  title:
			s = models.Section(title)
			s.description = request.form['description']
			if parent:
				s.parent = parent	
			db.session.add(s)
			db.session.commit()
			return redirect(url_for('index'))
		else:
			abort(400)
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

	total_tasks = len(section.tasks)
	for task in section.tasks:
		if task.completed:
			completed_tasks += 1

	if section.sub_sections:
		for sub_s in section.sub_sections:
			sub_completed_tasks, sub_total_tasks = set_section_progress(sub_s)
			total_tasks += sub_total_tasks
			completed_tasks += sub_completed_tasks

	section.total_tasks = total_tasks
	section.completed_tasks = completed_tasks

	return (completed_tasks, total_tasks)
		
			
		

@app.route('/task', methods=['POST'])
def task_post():
	completed = False
	if 'completed' in request.form:
		completed = request.form['completed'] == '1'
	
	title = request.form['title'].strip()
	description = request.form['description'].strip()
	due_date = request.form['due-date']
	due_date = datetime.strptime(due_date, '%Y-%m-%d')
	parent_id = request.form['parent']
	parent = models.Section.query.get(parent_id)
	t = models.Task(title, description, due_date, completed, parent)
	db.session.add(t)
	db.session.commit()
	return redirect(url_for('index'))

@app.route('/task/<int:task_id>', methods=['POST'])
def update_task(task_id):
	print('asdfasdf')
	abort(404)

	task = models.Task.query.get(task_id)
	if task is None:
		abort(404)
	if 'completed' in request.form:
		completed = request.form['completed'] == '1'
		task.completed = completed
	db.session.commit()
	return redirect(url_for('index'))
	

@app.route('/s')
def sections():
	sections = models.Section.query.all()
	return jsonify([s.json() for s in sections])





