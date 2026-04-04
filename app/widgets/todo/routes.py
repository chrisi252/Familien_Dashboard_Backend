"""Todo Widget Routes"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.widgets.todo.service import TodoService
from app.utils import require_widget_permission

bp = Blueprint('todo', __name__, url_prefix='/api/families')


@bp.route('/<int:family_id>/todos', methods=['GET'])
@jwt_required()
@require_widget_permission('can_view')
def get_todos(family_id):
    try:
        return jsonify({'todos': TodoService.get_todos(family_id)}), 200
    except Exception as e:
        return jsonify({'error': 'Todos konnten nicht abgerufen werden', 'details': str(e)}), 500


@bp.route('/<int:family_id>/todos', methods=['POST'])
@jwt_required()
@require_widget_permission('can_edit')
def create_todo(family_id):
    try:
        data = request.get_json()
        if not data or not data.get('title'):
            return jsonify({'error': 'Feld "title" ist erforderlich'}), 400
        todo = TodoService.create_todo(
            family_id=family_id,
            title=data['title'],
            description=data.get('description'),
        )
        return jsonify(todo.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Todo konnte nicht erstellt werden', 'details': str(e)}), 500


@bp.route('/<int:family_id>/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
@require_widget_permission('can_edit')
def update_todo(family_id, todo_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Keine Daten übergeben'}), 400
        todo = TodoService.update_todo(todo_id, family_id, **{
            k: data[k] for k in ('title', 'description', 'is_completed') if k in data
        })
        return jsonify(todo.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Todo konnte nicht aktualisiert werden', 'details': str(e)}), 500


@bp.route('/<int:family_id>/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
@require_widget_permission('can_edit')
def delete_todo(family_id, todo_id):
    try:
        TodoService.delete_todo(todo_id, family_id)
        return jsonify({'message': 'Todo gelöscht'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        return jsonify({'error': 'Todo konnte nicht gelöscht werden', 'details': str(e)}), 500
