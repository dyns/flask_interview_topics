
from flask import render_template, jsonify, abort, url_for, redirect 
from app import app
from flask import request
from app import models
from app import db	

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
		return render_template('index.html', sections=top_sections)

@app.route('/s')
def sections():
	sections = models.Section.query.all()
	return jsonify([s.json() for s in sections])





