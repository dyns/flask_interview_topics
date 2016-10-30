
from app import db

class Section(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(80), unique=True)
	description = db.Column(db.Text)
	due_date = db.Column(db.DateTime)
	sub_sections = db.relationship('Section')
	parent_section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
	tasks = db.relationship('Task')

	def __init__(self, title, description=None, due_date=None, sub_sections=None):
		if not sub_sections:
			sub_sections = []
		self.title = title
		self.due_date = due_date
		self.sub_sections = sub_sections
		self.description = description
	def json(self):
		sub_section_json = [s.json() for s in self.sub_sections]
		date = self.due_date.utcnow().strftime('%Y-%m-%d') if self.due_date else None
		data = {
			'title': self.title, 
			'description':self.description, 
			'due_date':date,
			'sections': sub_section_json
			}
		return data

class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(80))
	description = db.Column(db.Text)
	due_date = db.Column(db.DateTime)
	parent_section_id = db.Column(db.Integer, db.ForeignKey('section.id'))

	def __init__(self, title, description=None, due_date=None):
		self.title = title
		self.description = description
		self.due_date = due_date


