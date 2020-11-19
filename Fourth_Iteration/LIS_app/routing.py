from flask import render_template, url_for, flash, redirect, jsonify, request
from LIS_app import app, db, bcrypt
from LIS_app.forms import RegistrationForm, LoginForm, newRestaurantForm
from LIS_app.database import User, Restaurant, RatingButton
from flask_login import login_user, current_user, logout_user
from sqlalchemy import func

# Page Routes


@app.route("/")
@app.route("/home",  methods=['GET', 'POST'])
def Home():
    return render_template("index.html")


@app.route('/login',  methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('RestaurantRankings'))
    form = LoginForm()
    if form.validate_on_submit():
        usr = User.query.filter_by(email=form.email.data).first()
        if usr and (form.password.data == usr.password):
            login_user(usr)
            return redirect(url_for('UserPage'))
        else:
            flash('Login Unsuccessful. Please check email & password!', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('RestaurantRankings'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # Encrypts User info
        # hashed_password = bcrypt.generate_password_hash(
        #     form.password.data).decode('utf-8')
        user = User(fname=form.fname.data, lname=form.lname.data,
                    email=form.email.data, password=form.password.data)

        # Adds the new user into the database
        db.session.add(user)
        db.session.commit()

        flash('Your Account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/Restaurants', methods=['POST', 'GET'])
def restaurant_db():
    form = newRestaurantForm()
    if form.validate_on_submit():
        restaurant = Restaurant(restaurant_name=form.restaurant_name.data, ranch_name=form.ranch_name.data,
                                ranch_img=form.image.data, avg_score=form.base_score)

        db.session.add(restaurant)
        db.session.commit()
        return redirect(url_for('restaurant_db'))

    else:
        restaurants = Restaurant.query.order_by(Restaurant.restaurant_name)
        return render_template('restaurantsdb.html', title='Restaurants', form=form, restaurants=restaurants)


@app.route('/process', methods=['POST'])
def process():
    if request.method == "POST":
        restName = request.form['restaurant']
        userName = request.form['user']
        score = request.form['score']

        # print(restName, ' ', userName, ' ', score)
        if userName != 'no-user':
            user = db.session.query(User).filter_by(email=userName).first()
            restaurant = db.session.query(Restaurant).filter_by(restaurant_name=restName).first()
            newScore = RatingButton(customer_id=user.user_id, restaurant_id=restaurant.restaurant_id, score=score)

            db.session.add(newScore)
            db.session.commit()

            scores_by_restaurant = RatingButton.query.filter_by(restaurant_id=restaurant.restaurant_id).all()
            # print(scores_by_restaurant)
            # print(restaurant.restaurant_id, restaurant.avg_score)

            # Calculate average score
            total = 0
            val = 0
            for t in scores_by_restaurant:
                total += 1
                val += t.score

            avg = round(val/total, 2)
            # print(avg)

            restaurant.avg_score = avg
            db.session.commit()

            # TO DELETE ALL VALUES IN RATINGBUTTON DB:
            # db.session.query(RatingButton).delete()
            # db.session.commit()

            return jsonify({'avg' : avg})
    return jsonify(({'error' : 'Invalid user'}))


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('Home'))


@app.route('/RestaurantRankings')
def RestaurantRankings():
    restaurants = Restaurant.query.order_by(Restaurant.restaurant_name)
    return render_template('rankings.html', title='Restaurant Rankings', restaurants=restaurants)


@app.route('/UserPage')
def UserPage():
    return render_template('userpage.html', title='User Page')


@app.route('/TierList')
def TierList():
    return render_template('tierlist.html', title='Tiers')
