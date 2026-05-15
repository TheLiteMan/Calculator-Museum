from flask import jsonify, request
from flask_restful import Resource, abort
from data import db_session
from data.exhibits import Exhibit


def abort_if_exhibit_not_found(exhibit_id):
    """Вспомогательная функция проверки существования экспоната в базе данных"""
    session = db_session.create_session()
    exhibit = session.query(Exhibit).get(exhibit_id)
    session.close()
    if not exhibit:
        abort(404, message=f"Экспонат с идентификатором {exhibit_id} не найден в реестре")


def validate_exhibit_json(data):
    """Ручной валидатор входящих данных (замена удаленного reqparser)
    Добавляет проекту отказоустойчивость и чистые строки кода
    """
    errors = {}
    
    if 'title' not in data or not data['title'].strip():
        errors['title'] = "Поле 'title' является обязательным и не должно быть пустым"
        
    if 'short_description' not in data or not data['short_description'].strip():
        errors['short_description'] = "Поле 'short_description' является обязательным"
        
    if 'simulator_type' not in data:
        errors['simulator_type'] = "Поле 'simulator_type' должно быть указано"
    elif data['simulator_type'] not in ['abacus', 'pascalina', 'arithmometer', 'rpn', 'none']:
        errors['simulator_type'] = "Недопустимый тип симулятора устройства"
        
    if 'creation_year' in data and data['creation_year'] is not None:
        try:
            year = int(data['creation_year'])
            if year > 2026:
                errors['creation_year'] = "Год создания экспоната не может быть в будущем"
        except (ValueError, TypeError):
            errors['creation_year'] = "Год создания должен быть целым числом"
            
    return errors


class ExhibitsResource(Resource):
    def get(self, exhibit_id):
        """Получение подробной информации об одном конкретном экспонате"""
        abort_if_exhibit_not_found(exhibit_id)
        session = db_session.create_session()
        exhibit = session.query(Exhibit).get(exhibit_id)
        
        response_data = {
            'exhibit': {
                'id': exhibit.id,
                'title': exhibit.title,
                'short_description': exhibit.short_description,
                'full_description': exhibit.full_description,
                'creation_year': exhibit.creation_year,
                'simulator_type': exhibit.simulator_type,
                'views_count': exhibit.views_count,
                'created_at': exhibit.created_date.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        session.close()
        return jsonify(response_data)

    def delete(self, exhibit_id):
        """Удаление экспоната из базы данных по его идентификатору"""
        abort_if_exhibit_not_found(exhibit_id)
        session = db_session.create_session()
        exhibit = session.query(Exhibit).get(exhibit_id)
        session.delete(exhibit)
        session.commit()
        session.close()
        return jsonify({'success': 'Ресурс успешно удален из системы музея'})


class ExhibitsListResource(Resource):
    def get(self):
        """Получение краткого списка всех зарегистрированных экспонатов"""
        session = db_session.create_session()
        exhibits = session.query(Exhibit).all()
        
        output = []
        for item in exhibits:
            output.append({
                'id': item.id,
                'title': item.title,
                'short_description': item.short_description,
                'simulator_type': item.simulator_type,
                'creation_year': item.creation_year
            })
            
        session.close()
        return jsonify({'exhibits': output})

    def post(self):
        """Добавление нового экспоната через POST-запрос к API"""
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Отсутствуют JSON-данные в теле запроса'}), 400
            
        # Запускаем созданную нами валидацию вместо reqparser
        validation_errors = validate_exhibit_json(data)
        if validation_errors:
            return jsonify({'status': 'error', 'bad_fields': validation_errors}), 400
            
        session = db_session.create_session()
        exhibit = Exhibit(
            title=data['title'].strip(),
            short_description=data['short_description'].strip(),
            full_description=data.get('full_description', '').strip(),
            creation_year=data.get('creation_year'),
            simulator_type=data['simulator_type']
        )
        
        session.add(exhibit)
        session.commit()
        
        new_id = exhibit.id
        session.close()
        
        return jsonify({
            'success': 'Новый экспонат успешно обработан и сохранен',
            'assigned_id': new_id
        }), 201