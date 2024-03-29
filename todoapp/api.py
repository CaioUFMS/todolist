from peewee import JOIN, DoesNotExist
from playhouse.shortcuts import model_to_dict
from datetime import datetime
from todoapp.models import Lista, Tarefa
from flask import request, jsonify
from todoapp import app
from flask_login import current_user, login_required


@app.route('/api/listas', defaults={'id_lista': None}, methods=['GET', 'POST'])
@app.route('/api/listas/<int:id_lista>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_listas(id_lista):
    if request.method == 'GET':
        if id_lista:
            try:
                lista = Lista.select(Lista, Tarefa).join(Tarefa, JOIN.LEFT_OUTER).where(Lista.id == id_lista).get()
            except DoesNotExist:
                lista = None

            if not lista or lista.usuario.id != current_user.id:
                return jsonify({'msg': 'Recurso não encontrado'})

            model = model_to_dict(lista, recurse=False)
            tarefas = []
            for tarefa in lista.tarefas:
                tarefa_dict = model_to_dict(tarefa, recurse=False)
                tarefa_dict['data'] = tarefa.data.strftime('%d/%m/%y')
                tarefas.append(tarefa_dict)
            model.update({'tarefas': tarefas})

            return jsonify(model)

        listas = Lista.select(Lista.id, Lista.nome).where(Lista.usuario == current_user.id)
        listas = [model_to_dict(lista, recurse=False, fields_from_query=listas) for lista in listas]
        return jsonify(listas)

    elif request.method == 'POST':
        lista = Lista.create(nome='Lista de tarefas', descricao='Descrição da lista de tarefas.',
                             usuario=current_user.id)
        return jsonify(model_to_dict(lista, recurse=False))

    elif request.method == 'PATCH':
        if id_lista:
            lista = Lista.get_or_none(Lista.id == id_lista)
            if not lista or lista.usuario.id != current_user.id:
                return jsonify({'msg': 'Recurso não encontrado'})

            data = request.json
            lista.nome = data['nome']
            lista.descricao = data['descricao']
            lista.save()
            return jsonify(model_to_dict(lista, recurse=False))

        return jsonify({'msg': 'Forneça o id da lista'})

    elif request.method == 'DELETE':
        if id_lista:
            lista = Lista.get_or_none(Lista.id == id_lista)
            if not lista or lista.usuario.id != current_user.id:
                return jsonify({'msg': 'Recurso não encontrado'})

            Tarefa.delete().where(Tarefa.lista == id_lista).execute()
            lista.delete_instance()
            return jsonify({'msg': 'Recurso excluído com sucesso'})

        return jsonify({'msg': 'Forneça o id da lista'})


@app.route('/api/listas/<int:id_lista>/tarefas', defaults={'id_tarefa': None}, methods=['POST'])
@app.route('/api/listas/<int:id_lista>/tarefas/<int:id_tarefa>', methods=['GET', 'PATCH', 'DELETE'])
@login_required
def api_tarefas(id_lista, id_tarefa):
    if request.method == 'GET':
        if not id_tarefa:
            return jsonify({'msg': 'Forneça o id da tarefa'})

        tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
        if not tarefa or tarefa.lista.usuario.id != current_user.id:
            return jsonify({'msg': 'Recurso não encontrado'})

        return jsonify(model_to_dict(tarefa, recurse=False))

    elif request.method == 'POST':
        data = request.json
        tarefa = Tarefa.create(titulo='Tarefa', descricao='Descrição da tarefa.', lista=id_lista)
        model = model_to_dict(tarefa, recurse=False)
        model['data'] = datetime.strptime(tarefa.data, '%Y-%m-%d').strftime('%d/%m/%y')
        return jsonify(model)

    elif request.method == 'PATCH':
        if not id_tarefa:
            return jsonify({'msg': 'Forneça o id da tarefa'})

        data = request.json
        tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
        if not tarefa or tarefa.lista.usuario.id != current_user.id:
            return jsonify({'msg': 'Recurso não encontrado'})

        if 'concluida' in data:
            tarefa.concluida = data['concluida']

        else:
            tarefa.titulo = data['titulo']
            tarefa.descricao = data['descricao']
            tarefa.cor = data['cor']
        tarefa.save()

        return jsonify(model_to_dict(tarefa, recurse=False))

    elif request.method == 'DELETE':
        if not id_tarefa:
            return jsonify({'msg': 'Forneça o id da tarefa'})

        tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
        if not tarefa or tarefa.lista.usuario.id != current_user.id:
            return jsonify({'msg': 'Recurso não encontrado'})

        tarefa.delete_instance()
        return jsonify({'msg': 'Recurso excluído com sucesso'})
