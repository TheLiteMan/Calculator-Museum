import datetime
import logging
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import Api

from data import db_session
from data.users import User
from data.news import News
from data.exhibits import Exhibit
from data.feedback import Feedback

from forms.login import LoginForm
from forms.register import RegisterForm
from forms.exhibit import ExhibitForm
from forms.feedback import FeedbackForm

from utils.simulators import AbacusSimulator, PascalinaSimulator, ArithmometerSimulator, RpnCalculatorB334
from api import exhibits_resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'calc_museum_secure_ultra_key_2026'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=30)

api = Api(app)

# Настройка логирования сервера в файл
logging.basicConfig(
    filename='museum_system.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.context_processor
def inject_now():
    return {'now': datetime.datetime.utcnow()}


@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"Страница не найдена: {request.url}")
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.critical("Внутренняя ошибка сервера!")
    return render_template('errors/500.html'), 500


@app.route('/')
def index():
    app.logger.info("Посещение главной страницы")
    return render_template('index.html')


@app.route('/article')
def article():
    return render_template('article.html')


@app.route('/showcase')
def showcase():
    db_sess = db_session.create_session()
    search_query = request.args.get('search', '')
    filter_type = request.args.get('type', 'all')
    
    query = db_sess.query(Exhibit).filter(Exhibit.is_visible == True)
    
    if search_query:
        query = query.filter(Exhibit.title.like(f"%{search_query}%"))
    if filter_type != 'all':
        query = query.filter(Exhibit.simulator_type == filter_type)
        
    exhibits = query.order_by(Exhibit.creation_year).all()
    return render_template('showcase.html', exhibits=exhibits, search=search_query, current_type=filter_type)


@app.route('/exhibit/<int:exhibit_id>', methods=['GET', 'POST'])
def exhibit_detail(exhibit_id):
    db_sess = db_session.create_session()
    exhibit = db_sess.query(Exhibit).get_or_404(exhibit_id)
    
    # Увеличение счетчика просмотров
    exhibit.views_count += 1
    db_sess.commit()
    
    form = FeedbackForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("Только авторизованные пользователи могут оставлять отзывы", "danger")
            return redirect(url_for('login'))
        
        feedback = Feedback(
            text=form.text.data,
            rating=form.rating.data,
            user_id=current_user.id,
            exhibit_id=exhibit.id
        )
        db_sess.add(feedback)
        db_sess.commit()
        flash("Спасибо за ваш отзыв!", "success")
        return redirect(url_for('exhibit_detail', exhibit_id=exhibit.id))
        
    feedbacks = db_sess.query(Feedback).filter(Feedback.exhibit_id == exhibit.id).all()
    return render_template('exhibit_view.html', exhibit=exhibit, form=form, feedbacks=feedbacks)


# Исполнительный эндпоинт для работы интерактивных стендов симуляции через AJAX
@app.route('/api/simulate/<string:sim_type>', methods=['POST'])
def simulate_device(sim_type):
    data = request.json or {}
    action = data.get('action')
    
    if sim_type == 'abacus':
        sim = AbacusSimulator()
        if action == 'set':
            try:
                sim.set_value(int(data.get('value', 0)))
                return jsonify({'status': 'success', 'value': sim.get_value(), 'history': sim.get_history()})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 400
                
    elif sim_type == 'pascalina':
        sim = PascalinaSimulator()
        if action == 'add':
            sim.add_number(int(data.get('value', 0)))
            return jsonify({'status': 'success', 'state': sim.get_state(), 'history': sim.get_history()})
            
    elif sim_type == 'arithmometer':
        sim = ArithmometerSimulator()
        sim.set_levers(int(data.get('levers', 0)))
        if action == 'forward':
            sim.turn_handle_forward()
        elif action == 'backward':
            sim.turn_handle_backward()
        return jsonify({
            'status': 'success',
            'accumulator': sim.accumulator_register,
            'counter': sim.counting_register,
            'history': sim.get_history()
        })
        
    return jsonify({'status': 'error', 'message': 'Unknown simulator type'}), 400


@app.route('/admin/exhibits', methods=['GET', 'POST'])
@login_required
def admin_exhibits_panel():
    # Простейшая проверка прав: пусть админом будет первый зарегистрированный ID=1
    if current_user.id != 1:
        abort(403)
        
    db_sess = db_session.create_session()
    form = ExhibitForm()
    
    if form.validate_on_submit():
        exhibit = Exhibit(
            title=form.title.data,
            short_description=form.short_description.data,
            full_description=form.full_description.data,
            creation_year=form.creation_year.data,
            simulator_type=form.simulator_type.data,
            image_path=form.image_path.data,
            is_visible=form.is_visible.data
        )
        db_sess.add(exhibit)
        db_sess.commit()
        flash("Новый экспонат успешно внесен в реестр музея", "success")
        return redirect(url_for('admin_exhibits_panel'))
        
    all_items = db_sess.query(Exhibit).all()
    return render_template('admin_panel.html', form=form, exhibits=all_items)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            flash("Введенные пароли не совпадают", "danger")
            return render_template('register.html', form=form)
        
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            flash("Пользователь с таким email адресом уже зарегистрирован", "danger")
            return render_template('register.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        app.logger.info(f"Зарегистрирован новый пользователь: {user.email}")
        flash("Регистрация успешно завершена!", "success")
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            app.logger.info(f"Пользователь {user.email} вошел в систему")
            return redirect(url_for('index'))
        flash("Неверное сочетание логина и/или пароля", "danger")
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    app.logger.info(f"Пользователь {current_user.email} вышел из системы")
    logout_user()
    return redirect(url_for('index'))


# Инициализация REST-API путей
api.add_resource(exhibits_resource.ExhibitsListResource, '/api/v1/exhibits')
api.add_resource(exhibits_resource.ExhibitsResource, '/api/v1/exhibits/<int:exhibit_id>')


def setup_initial_data():
    """Автоматическое наполнение базы данных базовыми экспонатами при первом запуске"""
    db_sess = db_session.create_session()
    if db_sess.query(Exhibit).first() is None:
        abacus = Exhibit(
            title="Древнеримский Абак",
            short_description="Доска со специальными желобами для передвижения камешков.",
            full_description="Первый в истории калькулятор...",
            creation_year=-500,
            simulator_type="abacus"
        )
        pascalina = Exhibit(
            title="Паскалина Блеза Паскаля",
            short_description="Механическое колесное устройство для арифметики.",
            full_description="Создано великим ученым в 1642 году...",
            creation_year=1642,
            simulator_type="pascalina"
        )
        db_sess.add(abacus)
        db_sess.add(pascalina)
        db_sess.commit()


if __name__ == '__main__':
    db_session.global_init("db/museum.db")
    setup_initial_data()
    app.run(port=8080, host='127.0.0.1', debug=True)