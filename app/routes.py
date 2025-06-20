from flask import render_template, request, redirect, url_for, jsonify, flash, send_file, make_response
from . import db
from .models import User, Resident, Event
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

def init_routes(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.route('/')
    def index():
        return render_template('index.html', current="index")
    
    @app.route('/users')
    @login_required
    def users():
        users = User.query.all()
        return render_template('users.html', current="users", users=users)

    @app.route('/user/add', methods=["GET", "POST"])
    @login_required
    def user_add():
        if request.method == "GET":
            return render_template('user/add.html', current="users")
        if request.method == "POST":
            user = User()
            user.username = request.form["username"]
            user.password = request.form["password"]
            db.session.add(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/user/edit/<id>', methods=["GET", "POST"])
    @login_required
    def user_edit(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/edit.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            user.username = request.form["username"]
            user.password = request.form["password"]
            db.session.commit()
            return redirect("/users")

    @app.route('/user/del/<id>', methods=["GET", "POST"])
    @login_required
    def user_del(id):
        if request.method == "GET":
            user = db.get_or_404(User, id)
            return render_template('user/del.html', current="users", user=user)
        if request.method == "POST":
            user = db.get_or_404(User, request.form["id"])
            db.session.delete(user)
            db.session.commit()
            return redirect("/users")

    @app.route('/residents')
    @login_required
    def residents():
        residents = Resident.query.all()
        return render_template('resident.html', current="residents", residents=residents)

    @app.route('/resident/add', methods=["GET", "POST"])
    @login_required
    def resident_add():
        if request.method == "GET":
            return render_template('resident/add.html', current="residents")
        if request.method == "POST":
            resident = Resident()
            resident.first_name = request.form["first-name"]
            resident.last_name = request.form["last-name"]
            resident.patronymic = request.form["patronymic"]
            resident.apartment_number = request.form["apartment_number"]
            db.session.add(resident)
            db.session.commit()
            return redirect("/residents")

    @app.route('/resident/edit/<id>', methods=["GET", "POST"])
    @login_required
    def resident_edit(id):
        if request.method == "GET":
            resident = db.get_or_404(Resident, id)
            return render_template('resident/edit.html', current="residents", resident=resident)
        if request.method == "POST":
            resident = db.get_or_404(Resident, request.form["id"])
            resident.first_name = request.form["first-name"]
            resident.last_name = request.form["last-name"]
            resident.patronymic = request.form["patronymic"]
            resident.apartment_number = request.form["apartment_number"]
            db.session.commit()
            return redirect("/residents")

    @app.route('/resident/del/<id>', methods=["GET", "POST"])
    @login_required
    def resident_del(id):
        if request.method == "GET":
            resident = db.get_or_404(Resident, id)
            return render_template('resident/del.html', current="residents", resident=resident)
        if request.method == "POST":
            resident = db.get_or_404(Resident, request.form["id"])
            db.session.delete(resident)
            db.session.commit()
            return redirect("/residents")
        
    @app.route('/resident/photo-edit/<id>', methods=["GET", "POST"])
    def resident_photo_edit(id):
        if request.method == "GET":
            resident = db.get_or_404(Resident, id)
            return render_template('resident/add_photo.html', current="residents", resident=resident)
        if request.method == "POST":
            print("Hi")
            # Проверяем, есть ли файл в запросе
            if 'photo' not in request.files:
                flash('No file part')
                return redirect("/residents")
        
            file = request.files['photo']
            print(file)
        
            # Если пользователь не выбрал файл
            if file.filename == '':
                flash('No selected file')
                return redirect("/residents")
            
            def allowed_file(filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in {"jpg"}
            
            # Если файл разрешен и корректен
            if file and allowed_file(file.filename):
                if not os.path.exists(app.config['IMGS']):
                    os.makedirs(app.config['IMGS'])
                file.save(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")))
                print("OK")
                return redirect("/residents")
        return redirect("/residents")




    @app.route('/resident/photo/<id>', methods=["GET", "POST"])
    def resident_photo(id):
        if request.method == "GET":
            resident = db.get_or_404(Resident, id)
            if os.path.isfile(os.path.join(app.config['IMGS'], f"{id}.jpg")):
                return send_file(os.path.abspath(os.path.join(app.config['IMGS'], f"{id}.jpg")), as_attachment=True)
            else:
                return make_response(f"File '{id}' not found.", 404)
            
    
    
    @app.route('/residents/json')
    def residents_all():
        residents = Resident.query.all()
        result = []
        for resident in residents:
            resident_dict = resident.__dict__
            resident_dict.pop('_sa_instance_state', None)  # Удаляем служебное поле SQLAlchemy
            result.append(resident_dict)
        return jsonify(result)

    @app.route('/events')
    @login_required
    def events():
        events = Event.query.all()
        
        return render_template('events.html', current="events", events=events)

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('home'))
    
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
        
            user = User.query.filter_by(username=username, password=password).first()
            
            if user:
                login_user(user, remember=True)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect("/")
            else:
                flash('Неверное имя пользователя или пароль', 'danger')
    
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect("/")