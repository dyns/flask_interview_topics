
from flask import render_template, jsonify, abort 
from app import app
from flask import request
from app import models
from app import db

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		top_sections = models.Section.query.filter(~models.Section.sub_sections.any()).all()
		sec_json = [s.json() for s in top_sections]
		return render_template('index.html', sections=top_sections)
	elif request.method == 'POST':
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
			db.session.add(s)
			if parent:
				parent.sub_sections.append(s)			
			db.session.commit()
			return jsonify(request.form)
		else:
			abort(400)	


@app.route('/s')
def sections():
	sections = models.Section.query.filter(~models.Section.sub_sections.any()).all()
	return jsonify([s.json() for s in sections])

