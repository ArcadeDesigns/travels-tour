from flask import Flask, render_template, flash, request, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import LoginForm, PostForm, UserForm, PasswordForm, NamerForm, SearchForm, AskForm
from flask_ckeditor import CKEditor
from flask_ckeditor import upload_success, upload_fail
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
import urllib.request
import uuid as uuid
import os

app = Flask(__name__)

ckeditor = CKEditor(app)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ennynoah.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://axwqvbezkgisrr:d5a9914dc56945db6d0b29f23e07708061406bd05c69ddc246a1aa81862eb689@ec2-52-204-195-41.compute-1.amazonaws.com:5432/da7d9hockuhno'

app.config['SECRET_KEY'] = "cairocoders-ednalan"

UPLOAD_FOLDER = 'static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_EXTENSIONS'] = ['jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG']
app.config['CKEDITOR_FILE_UPLOADER'] = 'upload'

db = SQLAlchemy(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
	return Users.query.get(int(user_id))

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['jpg', 'jpeg', 'png', 'JPG', 'gif', 'PNG', 'JPEG'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/admin")
@login_required
def admin():
	form = UserForm()
	our_users = Users.query.order_by(Users.date_added)
	posts = Posts.query.order_by(Posts.date_posted)
	asks = Asks.query.order_by(Asks.date_posted)
	id = current_user.id
	if id == 1:
		return render_template("admin.html", 
			form=form,
			name=name,
			our_users=our_users,
			posts=posts,
			asks=asks)
	else:
		flash("Sorry you have to be an Admin to access this page")
		return redirect(url_for('dashboard'))

@app.route("/cookie")
@login_required
def cookie():
		return render_template("cookie.html")

@app.route("/contribute")
@login_required
def contribute():
		return render_template("contribute.html")

@app.route("/service")
@login_required
def service():
		return render_template("service.html")

@app.route("/about")
@login_required
def about():
		return render_template("about.html")

@app.route("/privacy")
@login_required
def privacy():
		return render_template("privacy.html")

@app.route("/terms-and-conditions")
@login_required
def terms_and_conditions():
		return render_template("terms-and-conditions.html")


@app.route("/disclaimer")
@login_required
def disclaimer():
		return render_template("disclaimer.html")

@app.route('/search', methods=["POST"])
def search():
	form = SearchForm()
	posts = Posts.query
	if form.validate_on_submit():
		post.searched = form.searched.data
		
		#Query the Database
		#posts = posts.filter_by(Posts.content.like('%' + post.searched + '%'))
		posts = posts.order_by(Posts.title).all()

		return render_template("search.html",
			form=form,
			searched=post.searched,
			posts=posts)

@app.context_processor
def base():
	form = SearchForm()
	return dict(form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(username=form.username.data).first()
		if user:
			
			if check_password_hash(user.password_hash, form.password.data):
				login_user(user)
				flash("Login Successful!")
				return redirect(url_for('dashboard'))
			else:
				flash("Wrong Password Please... Try Again!")
		else:
			flash(" That User Doesn't Exist... Try Again!")

	return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
	logout_user()
	flash("You Have Successfully Logged Out! ")
	return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
	return render_template('dashboard.html')

@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
	post_to_delete = Posts.query.get_or_404(id)
	id = current_user.id
	if id == post_to_delete.poster_id or id == 1:
		try:
			db.session.delete(post_to_delete)
			db.session.commit()

			flash ("Blog Post Was Deleted Successfully!")
			

			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)

		except:
			flash ("Whoops!!! There was a Problem Deleting Post Try Again...")

			posts = Posts.query.order_by(Posts.date_posted)
			return render_template("posts.html", posts=posts)
	else:
		flash("You are not authorized to Delete this Post!")

		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)
	

@app.route('/posts')
def posts():
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("posts.html", posts=posts)


@app.route('/posts/<int:id>')
def post(id):
	post = Posts.query.get_or_404(id)
	return render_template("post.html", post=post)


@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
	post = Posts.query.get_or_404(id)
	form = PostForm()

	if form.validate_on_submit():
		post.title = form.title.data
		post.slug = form.slug.data
		post.content = form.content.data
		post.file = form.file.data

		db.session.add(post)
		db.session.commit()

		flash("Post Successfully Updated")
		return redirect(url_for('post', id=post.id))

	if current_user.id == post.poster_id or current_user.id == 1 :
		form.title.data = post.title
		form.slug.data = post.slug
		form.content.data = post.content
		return render_template('edit_post.html', form=form)

	else:
		flash(" You need Authorization to access this Post")
		posts = Posts.query.order_by(Posts.date_posted)
		return render_template("posts.html", posts=posts)

@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
	form = PostForm()
			
	if form.validate_on_submit():

		poster = current_user.id
		post = Posts(title=form.title.data, content=form.content.data, file=form.file.data, poster_id=poster, slug=form.slug.data)

		if request.files['file']:
			post.file = request.files['file']

			filename = secure_filename(post.file.filename)

			file_name = str(uuid.uuid1()) + "_" + filename
			
			saver = request.files['file']

			post.file = file_name

			try:
				db.session.add(post)
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
				flash("Image Uploaded Successfully !")
				return render_template("add_post.html",
					form=form,
					post=post,
					id = 1)
			except:
				flash("Error! Looks Like There Was a Problem... Try Again!")
				return render_template("add_post.html",
					form=form,
					post=post,
					id = 1)
		else:
			db.session.add(post)
			db.session.commit()
			flash("Image Uploaded Successfully !")
			return render_template("add_post.html",
				form=form,
				post=post,
				id = 1)
		
		form.title.data = ''
		form.content.data = ''
		form.slug.data = ''

		db.session.add(post)
		db.session.commit()

	return render_template("add_post.html",
			form=form,
			id = 1)

#Add Post Page
@app.route('/add-ask', methods=['GET', 'POST'])
def add_ask():
	form = AskForm()
			
	if form.validate_on_submit():

		poster = current_user.id
		ask = Asks(title=form.title.data, content=form.content.data, file=form.file.data, poster_id=poster, slug=form.slug.data)

		#check for file
		if request.files['file']:
			ask.file = request.files['file']

			#Grab Image name
			filename = secure_filename(ask.file.filename)

			#set the uuid
			file_name = str(uuid.uuid1()) + "_" + filename
			
			#save the image
			saver = request.files['file']

			#change it to a String to save to db
			ask.file = file_name

			try:
				db.session.add(ask)
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
				flash("Your Question has been Successfully Sent !")
				return render_template("add_ask.html",
					form=form,
					ask=ask)
			except:
				flash("Error! Looks Like There Was a Problem... Try Again!")
				return render_template("add_ask.html",
					form=form,
					ask=ask)
		else:
			db.session.add(post)
			db.session.commit()
			flash("Your Question has been Successfully Sent !")
			return render_template("add_ask.html",
				form=form,
				ask=ask)
		
		#clear the form
		form.title.data = ''
		form.content.data = ''
		form.slug.data = ''

		#add post data to database
		db.session.add(ask)
		db.session.commit()

	return render_template("add_ask.html",
			form=form,
			id = id or 1)

@app.route('/asks/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_ask(id):
	ask = Asks.query.get_or_404(id)
	form = AskForm()

	if form.validate_on_submit():
		ask.title = form.title.data
		ask.slug = form.slug.data
		ask.content = form.content.data
		ask.file = form.file.data

		#Update to DataBase
		db.session.add(ask)
		db.session.commit()

		flash("Your Question has been Successfully Sent !")
		return redirect(url_for('ask', id=ask.id))

	if current_user.id == ask.poster_id or current_user.id == 1 :
		form.title.data = ask.title
		form.slug.data = ask.slug
		form.content.data = ask.content
		return render_template('edit_ask.html', form=form)

	else:
		flash(" You need Authorization to access this Post")
		ask = Asks.query.order_by(Asks.date_posted)
		return render_template("asks.html", asks=asks)

@app.route('/asks/delete/<int:id>')
@login_required
def delete_ask(id):
	ask_to_delete = Asks.query.get_or_404(id)
	id = current_user.id
	if id == ask_to_delete.poster_id or id == 1:
		try:
			db.session.delete(ask_to_delete)
			db.session.commit()

			#return message
			flash ("Your Question has been Deleted Successfully!")
			

			#Grab all the post from the DataBase
			asks = Asks.query.order_by(Asks.date_posted)
			return render_template("asks.html", asks=asks)

		except:
			#return error message
			flash ("Whoops!!! There was a Problem Deleting Post Try Again...")

			#Grab all the post from the DataBase
			asks = Asks.query.order_by(Asks.date_posted)
			return render_template("asks.html", asks=asks)
	else:
		#return message
		flash("You are not authorized to Delete this Post!")

		#Grab all the post from the DataBase
		asks = Asks.query.order_by(Asks.date_posted)
		return render_template("asks.html", asks=asks)
	

@app.route('/asks')
def asks():
	#Grab all the post from the DataBase
	asks = Asks.query.order_by(Asks.date_posted)
	return render_template("asks.html", asks=asks)


@app.route('/asks/<int:id>')
def ask(id):
	ask = Asks.query.get_or_404(id)
	return render_template("ask.html", ask=ask)


#Json Thing
@app.route('/date')
def get_current_date():
	return {"Date": date.today()}

#Delete DataBase
@app .route('/delete/<int:id>')
@login_required
def delete(id):
	if id == current_user.id:
		user_to_delete = Users.query.get_or_404(id)
		name = None
		form = UserForm()

		try:
			db.session.delete(user_to_delete)
			db.session.commit()
			flash("User Deleted Successfully!!")

			our_users = Users.query.order_by(Users.date_added)
			return render_template("add_user.html",
				form=form,
				name=name,
				our_users=our_users)

		except:
			flash("Whoops! There was a problem deleting user, Try Again... ")
			return render_template("add_user.html",
				form=form,
				name=name,
				our_users=our_users)

	else:
		flash("Sorry, You can delete this User")
		return redirect(url_for('dashboard'))


#Create New DataBase Record
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
	form = UserForm()
	name_to_update = Users.query.get_or_404(id)
	if request.method == "POST":
		name_to_update.name = request.form['name']
		name_to_update.email = request.form['email']
		name_to_update.username = request.form['username']
		name_to_update.about_author = request.form['about_author']
		
		#check for profile pic
		if request.files['profile_pic']:
			name_to_update.profile_pic = request.files['profile_pic']

			#Grab Image name
			pic_filename = secure_filename(name_to_update.profile_pic.filename)

			#set the uuid
			pic_name = str(uuid.uuid1()) + "_" + pic_filename
			
			#save the image
			saver = request.files['profile_pic']

			#change it to a String to save to db
			name_to_update.profile_pic = pic_name

			try:
				db.session.commit()
				saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
				flash("User Updated Successfully !")
				return render_template("update.html",
					form=form,
					name_to_update = name_to_update)
			except:
				flash("Error! Looks Like There Was a Problem... Try Again!")
				return render_template("update.html",
					form=form,
					name_to_update = name_to_update)
		else:
			db.session.commit()
			flash("User Updated Successfully !")
			return render_template("update.html",
				form=form,
				name_to_update = name_to_update)

	else:
		return render_template("update.html",
				form=form,
				name_to_update = name_to_update, 
				id = id or 1)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
	name = None
	form = UserForm()
	if form.validate_on_submit():
		user = Users.query.filter_by(email=form.email.data).first()
		if user is None:
			#Hash Password
			hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
			user = Users(name=form.name.data, username=form.username.data, email=form.email.data, password_hash=hashed_pw)
			db.session.add(user)
			db.session.commit()

			flash("User Added Successfully")

		else:
			flash("This User Already Exist")
			return render_template("add_user.html",
				form=form)

		name = form.name.data
		form.name.data = ''
		form.username.data = ''
		form.email.data = ''
		form.password_hash = ''

	our_users = Users.query.order_by(Users.date_added)

	return render_template("add_user.html",
		form=form,
		name=name,
		our_users=our_users)

#create a route decorator
@app.route("/")
def index():
	#Grab all the post from the DataBase
	posts = Posts.query.order_by(Posts.date_posted)
	return render_template("index.html", 
		posts=posts)

@app.route('/files/<path:filename>')
def uploaded_files(filename):
	app = current_app._get_current_object()
	path = (app.config['UPLOAD_FOLDER'])
	return send_from_directory(path, filename)

@app.route('/upload', methods=['POST'])
def upload():
	app = current_app._get_current_object()
	f = request.files.get('upload')

	# Add more validations here
	extension = f.filename.split('.')[-1].lower()
	if extension not in ['jpg', 'gif', 'png', 'jpeg']:
		return upload_fail(message='Image only!')
	saver.save(os.path.join((app.config['UPLOAD_FOLDER']), f.filename))
	url = url_for('main.uploaded_files', filename=f.filename)
	return upload_success(url, filename=f.filename)


#localhost:5000/user/john
@app.route("/user")
@login_required
def user():
	return render_template("user.html")


#create custom error page
#invalid URL
@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"), 404

@app.errorhandler(500)
def page_not_found(e):
	return render_template("500.html"), 500

#create name page
@app.route('/name', methods=['GET', 'POST'])
def name():
	name = None
	form = NamerForm()

	#validate form
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
		flash("Form Submitted Successful")

	return render_template("name.html",
		name = name,
		form = form)


#create password Testing page
@app.route('/test_pw', methods=['GET', 'POST'])
@login_required
def test_pw():
	email = None
	password = None
	pw_to_check = None
	passed = None
	form = PasswordForm()

	#validate form
	if form.validate_on_submit():
		email = form.email.data
		password = form.password_hash.data
		form.email.data = ''
		form.password_hash.data = ""

		#Look up User by Email Address
		pw_to_check = Users.query.filter_by(email=email).first()

		#check hash password
		passed = check_password_hash(pw_to_check.password_hash, password)

		#flash("Form Submitted Successful")

	return render_template("test_pw.html",
		email = email,
		password = password,
		pw_to_check = pw_to_check,
		passed = passed,
		form = form)

#Create A Blog Post
class Asks(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	file = db.Column(db.String(), nullable=True)
	content = db.Column(db.Text)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))

	#Create a foreign Key to link two primary keys
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#Create A Blog Post
class Posts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(255))
	file = db.Column(db.String(), nullable=True)
	content = db.Column(db.Text)
	date_posted = db.Column(db.DateTime, default=datetime.utcnow)
	slug = db.Column(db.String(255))

	#Create a foreign Key to link two primary keys
	poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

#create a model
class Users(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), nullable=False, unique=True)
	name = db.Column(db.String(200), nullable=False)
	about_author = db.Column(db.Text(), nullable=True)
	email = db.Column(db.String(200), nullable=False, unique=True)
	date_added = db.Column(db.DateTime, default=datetime.utcnow)
	profile_pic = db.Column(db.String(), nullable=True)
	#Do Some Password Stuff
	password_hash = db.Column(db.String(128))

	#User can Have Many Posts
	posts = db.relationship('Posts', backref='poster')
	asks = db.relationship('Asks', backref='poster')
	
	@property
	def password(self):
		raise AttributeError(' Password Not A Readable Attribute !!! ')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	#create string
	def __repr__(self):
		return '<Name %r>' % self.name
