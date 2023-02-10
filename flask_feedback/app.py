


from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models2 import connect_db, db, User, Feedback
from forms import UserForm, FeedbackForm, LogInForm
from sqlalchemy.exc import IntegrityError




app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False




connect_db(app)


toolbar = DebugToolbarExtension(app)









@app.route('/')
def home_page():
    return render_template('index.html')









@app.route('/feedbacks/<int:id>', methods=['GET','POST'])
def show_feedback(id):

    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    form = FeedbackForm()
    
    all_feedback = Feedback.query.all()
    
    user = User.query.get(id)

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(content=content, title=title, user_id=session['user_id'])

        db.session.add(new_feedback)
        db.session.commit()

        flash("Feedback Created!", "success")

        return redirect(f'/users/{id}')

    return render_template('feedback.html', form=form, feedbacks=all_feedback, user=user)












@app.route('/feedbacks/delete/<int:id>', methods=["POST"])
def delete_feedback(id):

    if 'user_id' not in session:
        flash('Please login first', "danger")
        return redirect('/login')
    
    feedback = Feedback.query.get_or_404(id)

    if feedback.user_id == session['user_id']:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback Deleted", "info")
        return redirect(f'/users/{feedback.user_id}')

    flash("You do not have permission to do that!", "danger")
    return redirect('/login')














@app.route('/feedbacks/edit/<int:id>', methods=['GET', "POST"])
def edit_feedback(id):

    if 'user_id' not in session:
        flash('Please login first', "danger")
        return redirect('/login')
    
    feedback = Feedback.query.get_or_404(id) 
    
    form = FeedbackForm()

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data       
        db.session.commit()
        
        flash('Feedback Edited!', 'success')

        return redirect(f'/users/{feedback.user_id}')
    
    return render_template('edit_details.html', form=form)















@app.route('/register', methods=['GET', 'POST'])
def register_user():
    
    form = UserForm()
    
    if form.validate_on_submit():
        
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        
        db.session.commit()

        # try:
        #     db.session.commit()
        # except IntegrityError:
        #     form.username.errors.append('Username is taken. Please try another.')

        #     return render_template('register.html', form=form)

        session["user_id"] = new_user.id
        flash('Welcome! Successfully created an account.', "success")

        return redirect(f'/users/{new_user.id}')

    return render_template('register.html', form=form)







@app.route('/users/<int:id>', methods=['GET'])
def details_page(id):
    
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    else:
        user = User.query.get(id)

    return render_template('details.html', user=user)










@app.route('/users/delete/<int:id>', methods=['GET','POST'])
def delete_user(id):
    
    if "user_id" not in session:
        flash("Please login first!", "danger")
        return redirect('/')
    
    else:

        user = User.query.get_or_404(id)

        db.session.delete(user)
        db.session.commit()

        return redirect('/login')













@app.route('/login', methods=['GET', 'POST'])
def login_user():

    form = LogInForm()

    if form.validate_on_submit():
        
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome back, {user.username}!', "primary")
            session["user_id"] = user.id
            return redirect(f'/users/{user.id}')
        
        else:
            form.username.errors = ["Incorrect username/password please try again."]


    return render_template('login.html', form=form)












@app.route('/logout')
def logout_user():
    
    session.pop('user_id')
    
    flash("Logged out.", "info")
    
    return redirect('/')    




