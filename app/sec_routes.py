
from flask import render_template, abort, url_for, redirect, request
from app import app
from app import models
from app import db

@app.route('/section', methods=['POST'])
def sections():
	# Create new section
	if request.method == 'POST':
		title = request.form['title'].strip()

		if not title or len(title) > models.Section.MAX_TITLE_LENGTH:
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
					if getSectionDepth(parent) <= (MAX_SECTION_DEPTH - 1):
						s.parent = parent
					else:
						abort(400)
				else:
					abort(404)

		db.session.add(s)
		db.session.commit()
		return redirect(url_for('section', sec_id=s.id))

MAX_SECTION_DEPTH = 10

def getSectionDepth(section):
	depth = 1
	while(section.parent is not None):
		depth += 1
		section = section.parent
	return depth

@app.route('/section/<int:sec_id>', methods=['GET','POST'])
def section(sec_id):
	sec = models.Section.query.get(sec_id)
	if not sec:
		abort(404)

	if request.method == 'POST':
		if 'delete-sec' in request.form and request.form['delete-sec'] == 'delete':
			remove_children(sec)
			db.session.commit()
			return redirect(url_for('index'))
		elif 'update-section' in request.form and request.form['update-section'] == 'update':
			if 'title' in request.form:
				if request.form['title'].strip() and len(request.form['title'].strip()) <= models.Section.MAX_TITLE_LENGTH:
					sec.title = request.form['title'].strip()
				else:
					abort(400)
			if 'description' in request.form:
				sec.description = request.form['description'].strip()
			db.session.commit()
			return redirect(url_for('section', sec_id=sec.id))
		else:
			abort(400)
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
