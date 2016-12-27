import os
from flask import render_template, jsonify, abort, url_for, redirect, json
from app import app
from flask import request
from app import models
from app import db
from datetime import datetime
from app.sec_routes import *
from app.task_routes import *

@app.route('/', methods=['GET'])
def index():
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
