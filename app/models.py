
from app import db

class Section(db.Model):
	MAX_TITLE_LENGTH = 80
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(MAX_TITLE_LENGTH))
	description = db.Column(db.Text)
	due_date = db.Column(db.DateTime)

	parent_id = db.Column(db.Integer, db.ForeignKey('section.id'))
	sub_sections = db.relationship('Section', backref=db.backref('parent', remote_side=[id]))

	tasks = db.relationship('Task', backref=db.backref('parent'))

	def __init__(self, title, description=None, due_date=None, sub_sections=None):
		if not sub_sections:
			sub_sections = []
		self.title = title
		self.due_date = due_date
		self.sub_sections = sub_sections
		self.description = description
		self.total_tasks = 0
		self.completed_tasks = 0

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
	MAX_TITLE_LENGTH = 80
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(MAX_TITLE_LENGTH))
	description = db.Column(db.Text)
	due_date = db.Column(db.DateTime)
	parent_section_id = db.Column(db.Integer, db.ForeignKey('section.id'))
	confidence = db.Column(db.Integer)

	def __init__(self, title, description=None, due_date=None, confidence = 0, parent=None):
		self.title = title
		self.description = description
		self.due_date = due_date
		self.confidence = confidence
		self.parent = parent
