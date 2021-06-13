from flask import render_template, url_for, flash, redirect
from todoapp.forms import FormCadastro, FormLogin, FormLista, FormTarefa
from flask_login import login_user, current_user, logout_user, login_required
from todoapp.models import Usuario, Lista, Tarefa
from todoapp import app, bcrypt


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
    form.descricao.data = lista.descricao
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
        tarefa.data = form.data.data
        tarefa.save()
        flash('Tarefa alterada com sucesso!', 'success')
        return redirect(url_for('listas', id_lista=id_lista))
    form.descricao.data = tarefa.descricao
    return render_template('editar_tarefa.html', tarefa=tarefa, form=form, id_lista=id_lista)
