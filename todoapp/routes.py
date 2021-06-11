from flask import render_template, url_for, flash, redirect, request, jsonify
from peewee import JOIN

from todoapp.forms import FormCadastro, FormLogin, FormLista, FormTarefa
from flask_login import login_user, current_user, logout_user, login_required
from todoapp.models import Usuario, Lista, Tarefa, DoesNotExist
from todoapp import app, bcrypt
from playhouse.shortcuts import model_to_dict


@app.route('/')
@app.route('/home')
def sobre():
    return render_template('sobre.html', title='Sobre')


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('listas'))
    form = FormCadastro()
    if form.validate_on_submit():
        hash_senha = bcrypt.generate_password_hash(form.senha.data).decode('utf-8')
        Usuario.create(nome=form.nome.data, email=form.email.data, senha=hash_senha)
        flash(f'Usuário {form.nome.data} foi criado com sucesso!', 'success')
        return redirect(url_for('login'))

    return render_template('cadastro.html', title='Cadastro', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('listas'))
    form = FormLogin()
    if form.validate_on_submit():
        user = Usuario.get_or_none(Usuario.email == form.email.data)
        if user and bcrypt.check_password_hash(user.senha, form.senha.data):
            login_user(user)
            return redirect(url_for('listas'))
        else:
            flash('Falha no login. Verifique o email e senha inseridos.', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('sobre'))


@app.route('/listas')
@login_required
def listas():
    return render_template('lista.html', title='Listas')


@app.route('/listas/<int:id_lista>/editar', methods=['GET', 'POST'])
@login_required
def editar_lista(id_lista):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    form = FormLista()
    if form.validate_on_submit():
        lista.nome = form.nome.data
        lista.descricao = form.descricao.data
        lista.save()
        flash('Lista alterada com sucesso!', 'success')
        return redirect(url_for('listas', id_lista=lista.id))
    return render_template('editar_lista.html', lista=lista, form=form)


@app.route('/listas/<int:id_lista>/tarefas/<int:id_tarefa>/editar', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id_lista, id_tarefa):
    lista = Lista.get_or_none(Lista.id == id_lista)
    if not lista or lista.usuario.id != current_user.id:
        flash('Lista não encontrada.', 'info')
        return redirect(url_for('listas'))
    tarefa = Tarefa.get_or_none(Tarefa.id == id_tarefa)
    if not tarefa:
        flash('Tarefa não encontrada.', 'info')
        return redirect(url_for('listas'))
    form = FormTarefa()
    if form.validate_on_submit():
        if not tarefa:
            flash('Esta tarefa não existe.')
            return redirect(url_for('listas'))
        tarefa.titulo = form.titulo.data
        tarefa.descricao = form.descricao.data
        if form.cor.data:
            tarefa.cor = form.cor.data
        else:
            tarefa.cor = 'rgb(255, 255, 255)'
        tarefa.save()
        flash('Tarefa alterada com sucesso!', 'success')
        return redirect(url_for('listas', id_lista=id_lista))
    form.descricao.data = tarefa.descricao
    return render_template('editar_tarefa.html', tarefa=tarefa, form=form, id_lista=id_lista)


# API
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
            model.update({'tarefas': [model_to_dict(tarefa, recurse=False) for tarefa in lista.tarefas]})
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

            Tarefa.delete().where(Tarefa.lista == id_lista)
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
        return jsonify(model_to_dict(tarefa, recurse=False))

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
