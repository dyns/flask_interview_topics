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
