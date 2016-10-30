
from flask import render_template, jsonify 
from app import app
from flask import request
from app import models
from app import db

@app.route('/', methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		top_sections = models.Section.query.all()
		sec_json = [s.json() for s in top_sections]
		return render_template('index.html', sections=str(sec_json))
	elif request.method == 'POST':
		s = models.Section(request.form['title'])
		db.session.add(s)
		db.session.commit()
		return jsonify(request.form)
