
import os
from flask import render_template, jsonify, abort, url_for, redirect, json
from app import app
from flask import request
from app import models
from app import db
from datetime import datetime

@app.route('/s', methods=['GET', 'POST'])
def sections():
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
	else:
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


def remove_children(sec):
	for task in sec.tasks:
		db.session.delete(task)
	for sub_s in sec.sub_sections:
		remove_children(sub_s)
	db.session.delete(sec)
