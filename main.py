from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
import random
import datetime
import smtplib

##---------------------- EMAIL DATA ---------------------- ##
MY_EMAIL = "olmos.edward@gmail.com"
MY_PASSWORD = "lshgrctaaymugbhv"

##---------------------- YEAR FOR COPYRIGHT ---------------------- ##
year = datetime.datetime.now().strftime('%Y')

##---------------------- CONFIGURE BOOTSTRAP ---------------------- ##
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

##---------------------- CONNECT TO DATABASE ---------------------- ##
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##---------------------- CONFIGURE TABLE ---------------------- ##
with app.app_context():
    class ProjectEntry(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        project_number = db.Column(db.Integer, unique=True, nullable=False)
        project_level = db.Column(db.String(200), nullable=False)
        course = db.Column(db.String(200), nullable=False)
        course_provider = db.Column(db.String(200), nullable=False)
        project_name = db.Column(db.String(200), nullable=False)
        project_description = db.Column(db.String(500), nullable=False)
        topics = db.Column(db.String(300))
    # db.create_all()

##---------------------- RANDOM PROJECTS ---------------------- ##
with app.app_context():
    num_projects = len(db.session.query(ProjectEntry).all())

    random_nums = random.sample(range(1, num_projects), 4)

    random_1 = ProjectEntry.query.get(random_nums[0])
    random_2 = ProjectEntry.query.get(random_nums[1])
    random_3 = ProjectEntry.query.get(random_nums[2])
    random_4 = ProjectEntry.query.get(random_nums[3])

##---------------------- CONTACT FORM ---------------------- ##
class ContactForm(FlaskForm):
    name = StringField("name", validators=[DataRequired()])
    email = EmailField('email', validators=[DataRequired()])
    body = StringField("message", validators=[DataRequired()])
    submit = SubmitField("send")

##---------------------- ADD FORM ---------------------- ##
class AddForm(FlaskForm):
    project_number = StringField("number", validators=[DataRequired()])
    project_level = SelectField('Course Provider', choices=["Beginner", "Intermediate", "Intermediate+", "Advanced", "Professional Development Portfolio"])
    course = SelectField('Course', choices=["100 Days of Python"])
    course_provider = SelectField('Course Provider', choices=["The App Brewery"])
    project_name = StringField("name", validators=[DataRequired()])
    project_description = StringField("description", validators=[DataRequired()])
    topics = StringField("What did you learn?", validators=[DataRequired()])
    submit = SubmitField("send")


@app.route('/', methods=["POST", "GET"])
def home_page():
    form = ContactForm()

    if form.validate_on_submit():
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=MY_EMAIL, password=MY_PASSWORD)
            connection.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg=f"Subject:New message from portfolio\n\n"
                f"From: {form.name.data}\n"
                f"Email: {form.email.data}\n"
                f"Message: {form.body.data}"
        )

        return redirect(url_for("home_page"))

    return render_template("index.html", form=form, year=year, random_1=random_1, random_2=random_2, random_3=random_3, random_4=random_4, num_projects=num_projects)


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/projects')
def projects():
    with app.app_context():
        all_projects = db.session.query(ProjectEntry).all()

    return render_template("projects.html", year=year, num_projects=num_projects, projects=all_projects)


@app.route("/projects/<int:project_num>", methods=["POST", "GET"])
def show_projects(project_num):
    requested_project = ProjectEntry.query.filter_by(project_number=project_num).first()
    image = f'img/projects/project_{project_num}_img.png'

    return render_template("individual_project.html", project=requested_project,  project_num=project_num, image=image, year=year)

@app.route("/add", methods=["POST", "GET"])
def add_projects():
    form = AddForm()
    if form.validate_on_submit():
        new_project = ProjectEntry(
            project_number=form.project_number.data,
            project_name=form.project_name.data,
            project_description=form.project_description.data,
            project_level=form.project_level.data,
            course=form.course.data,
            course_provider=form.course_provider.data,
            topics=form.course.data
        )
        db.session.add(new_project)
        db.session.commit()
        return redirect(url_for("add_projects"))
    return render_template("add.html", form=form)

if __name__ == "__main__":
    app.run(debug=True)

